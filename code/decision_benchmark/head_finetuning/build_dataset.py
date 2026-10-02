"""Build an isolated, corpus-grounded 200-case head-fine-tuning pilot.

This creates data only. No provider requests, model inference, or training.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'code'))
from decision_benchmark.contracts import make_state, record, routing_contract
from decision_benchmark.dataset import article_source

HERE = Path(__file__).resolve().parent
DATA = HERE / 'data'
EVALUATION = HERE.parent / 'cases.jsonl'
CORPUS = ROOT / 'data/chunks/parentchunks2.json'
SEED = 20261002
FAMILIES = ['evidence_present_or_missing', 'verbatim_or_heading_only',
            'rewrite_plus_evidence', 'comparison_coverage', 'older_evidence_after_topic_shift']
CHAT = [
    'Could you explain how to phrase a clear research question?',
    'Please suggest a friendly name for a reading club.',
    'I appreciate your patience with my questions.',
    'Write a two-line reminder to take regular study breaks.',
    'How can I make my notes easier to read?',
    'Suggest a simple routine for organising my desk.',
    'Can you explain the difference between summarising and translating?',
    'Please write a cheerful greeting for my classmates.',
    'I will return to this conversation after lunch.',
    'Help me word a polite request for a copy of some notes.',
]
UNCLEAR = [
    'Please analyse the clause I have in mind; I have not named it yet.',
    'Which provision was I intending to refer to?',
    'Can you explain my document? I have not attached or described it.',
    'Please compare the two provisions I forgot to identify.',
    'Tell me whether the unnamed exception I mean is relevant.',
    'Could you translate the passage? I have not supplied it.',
    'Can you quote the sentence I am thinking of?',
    'Please identify the constitutional topic I have not told you about.',
    'Explain the item I meant by the previous one; this is our first message.',
    'Review my attachment once I provide it; what information do you need first?',
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def article_refs(text):
    refs = set()
    pattern = r'\b(?:articles?|art\.?)\s+(\d+[A-Z]*(?:\s*(?:,|and|or|to|&)\s*\d+[A-Z]*)*)'
    for match in re.finditer(pattern, text, re.I):
        refs.update(x.upper() for x in re.findall(r'\d+[A-Z]*', match[1], re.I))
    return refs


def input_text(row):
    return row['query'] + '\n' + '\n'.join(m['content'] for m in row['history'])


def normalized(text):
    return ' '.join(text.casefold().split())


def fingerprint(row):
    return hashlib.sha256(json.dumps(make_state(row), sort_keys=True,
                                     ensure_ascii=False).encode()).hexdigest()


def opening_source(article, parents):
    source = article_source(article, parents)
    # Preserve the original excerpt separately; normalise OCR separators for display.
    cleaned = re.sub(r'<[^>]+>', '', source['text']).replace('\ufffd', ' — ')
    cleaned = re.sub(r'^\[?' + re.escape(article) + r'\.\s*', '', cleaned).strip()
    title, separator, body = cleaned.partition('.')
    if not separator or not body.strip():
        raise ValueError('No article heading/body boundary')
    body = body.lstrip(' —–-[]\n\r\t')
    paragraph = body.split('\n\n')[0].strip()
    first_sentence = re.split(r'(?<=[.!?])\s+', paragraph)[0].strip()
    if not 10 <= len(first_sentence.split()) <= 75 or '\ufffd' in first_sentence:
        raise ValueError('Opening sentence is unsuitable for the bounded pilot')
    if 'omitted' in first_sentence.casefold() or first_sentence.count('*') > 3:
        raise ValueError('Omitted/non-substantive provision')
    return dict(source, title=' '.join(title.split()), opening=first_sentence,
                rendering='first source sentence; HTML removed and OCR separators normalised')


def supported_answer(source):
    return (f"Article {source['article']} — {source['title']}. "
            f"Opening source passage: {source['opening']} "
            f"[Article {source['article']}; {source['parent_id']}]")


def pair_history(source, auxiliary, family, index):
    article = source['article']
    good = supported_answer(source)
    variant = index % 10
    title = source['title']
    if family == 'evidence_present_or_missing':
        queries = [
            'Can you explain the opening provision and keep the citation?',
            'What does its first passage actually say? Include the source.',
            'Please turn the opening provision into two points, with a reference.',
            'Give me the original opening words and the source for my notes.',
            'How would you explain the first passage to a beginner? Cite it.',
            'I need the text at the beginning of that article and its reference.',
            'Write a short explanation of the opening provision, using a source.',
            'Could you show me the first source passage for this topic?',
            'Please give the opening passage, then a one-line explanation and citation.',
            'What can we say from the opening provision alone? Retain its reference.',
        ]
        query = queries[variant]
        seed = f'Let us look at Article {article}, on {title.lower()}.'
        missing = f"Our topic is Article {article}: {title}."
        required = 'The requested opening passage and source reference must be present.'
    elif family == 'verbatim_or_heading_only':
        queries = [
            'Can you quote the opening body passage exactly and cite it?',
            'I need the original opening wording, rather than just the title. Include a source.',
            'Please copy the first passage word for word and keep its source reference.',
            'What are the exact opening words of the provision? Give the reference too.',
            'For a quotation in my notes, give the opening passage and citation.',
            'Show the text immediately after that heading, with a source reference.',
            'Could you supply a verbatim quotation from the beginning of that article?',
            'Please put the original first passage in quotation marks and cite the source.',
            'Now I need the opening body text, including its citation.',
            'Give the beginning of the provision in its original wording, with a reference.',
        ]
        query = queries[variant]
        seed = f'What is the heading of Article {article}?'
        missing = f"The heading of Article {article} is '{title}'."
        required = 'A heading alone does not supply the requested verbatim body passage.'
    elif family == 'rewrite_plus_evidence':
        formats = ['two short bullets', 'a study card', 'a short paragraph', 'simple English',
                   'a question-and-answer note', 'a brief Hindi explanation', 'three short points',
                   'a revision note', 'one concise explanation', 'a table with text and explanation']
        query = (f'Turn our note into {formats[variant]}, and include the original opening '
                 'passage and its source reference.')
        seed = f'Prepare a short note about Article {article}.'
        missing = f"Study note: Article {article} — {title}."
        required = 'The rewrite also asks for an opening passage and citation; the heading is insufficient.'
    elif family == 'comparison_coverage':
        other = auxiliary['article']
        queries = [
            'Compare the two opening passages, keeping both source references.',
            'Explain how the beginnings of these two provisions differ. Cite both.',
            'Make a two-row table of their opening passages and their references.',
            'For each of those articles, show the first passage and its source.',
            'What does each opening passage cover? Keep the two citations.',
            'Please put their opening text side by side, with references.',
            'Summarise only the beginning of each provision and cite the passages.',
            'Write a short comparison based on their first passages, citing both.',
            'Could you make one study card per article using its opening text and source?',
            'Quote the beginning of each article so I can compare them; include the references.',
        ]
        query = queries[variant]
        seed = f'Provide the opening passages of Articles {other} and {article}.'
        missing = supported_answer(auxiliary)
        good = supported_answer(auxiliary) + '\n' + good
        required = 'Both opening passages are needed; the positive case lacks the second passage.'
    else:
        requests = ['explain its first passage', 'give its opening text', 'make a short note from its beginning',
                    'quote its original opening words', 'translate its first passage into Hindi',
                    'summarise its opening in a sentence', 'make two bullets from its first passage',
                    'show the original opening provision', 'make a study card from its opening',
                    'explain the beginning in plain language']
        query = f'Return to Article {article}: {requests[variant]}, keeping its source reference.'
        seed = f'Keep a note about Article {article} for later.'
        missing = f"Article {article} is titled '{title}'."
        required = 'The earlier evidence must be retained across intervening discussion.'
    if family != 'comparison_coverage':
        # A cited heading still cannot support a request for the body passage.
        # Citation presence alone must not determine the route.
        missing += f" [Article {article}; {source['parent_id']}]"
    positive = [{'role':'user','content':seed}, {'role':'assistant','content':missing}]
    negative = [{'role':'user','content':seed}, {'role':'assistant','content':good}]
    if index % 2 or family == 'older_evidence_after_topic_shift':
        preferences = [
            ('Keep the language simple.', 'I will use familiar words.'),
            ('These notes are for revision.', 'I will keep the notes concise and easy to review.'),
            ('Please retain article numbers in our notes.', 'I will retain the article numbers.'),
            ('Use a neutral tone.', 'I will use a neutral tone.'),
            ('Avoid extra background unless I ask.', 'I will focus on the passage you request.'),
            ('I prefer short answers.', 'I will keep the answers short.'),
            ('Can we go one topic at a time?', 'Yes, we can discuss one topic at a time.'),
            ('I want to understand the wording first.', 'We can start with the wording.'),
            ('Please keep source references readable.', 'I will put references beside the relevant text.'),
            ('Let us use bullets when helpful.', 'I will use bullets where they help explain the text.'),
        ]
        user, assistant = preferences[variant]
        extra = [{'role':'user','content':user}, {'role':'assistant','content':assistant}]
        positive += extra
        negative += extra
    if family == 'older_evidence_after_topic_shift':
        extra = [{'role':'user','content':'Before we continue, suggest a short heading for this notebook.'},
                 {'role':'assistant','content':'A suitable heading is Constitutional Reading Notes.'}]
        positive += extra
        negative += extra
    return query, positive, negative, required


def build():
    parents = json.loads(CORPUS.read_text(encoding='utf-8'))
    evaluation = [json.loads(line) for line in EVALUATION.read_text(encoding='utf-8').splitlines()]
    eval_refs = article_refs('\n'.join(input_text(row) for row in evaluation))
    ids = set(re.findall(r'(?m)^\[?(\d+[A-Z]*)\.\s',
                        re.sub(r'<sup>\d+</sup>', '', '\n'.join(r['text'] for r in parents))))
    ordered = sorted(ids, key=lambda a:(int(re.match(r'\d+',a)[0]),a))
    rng = random.Random(SEED)
    rng.shuffle(ordered)
    candidates = []
    used_refs = set(eval_refs)
    for article in ordered:
        if int(re.match(r'\d+',article)[0]) > 395 or article in used_refs:
            continue
        try:
            source = opening_source(article, parents)
        except ValueError:
            continue
        refs = article_refs(supported_answer(source)) | {article}
        if refs & used_refs:
            continue
        candidates.append(source)
        used_refs.update(refs)
        if len(candidates) == 60:
            break
    if len(candidates) != 60:
        raise ValueError(f'Need 60 independent new corpus topics; found {len(candidates)}')
    primary, auxiliary = candidates[:50], candidates[50:]
    # Eight groups per family train, two validate. All four cases in a group stay together.
    validation_groups = set()
    for offset in range(0,50,10):
        validation_groups.update(rng.sample(list(range(offset,offset+10)),2))
    rows = []
    sources = {}
    def add(index,style,label,query,history,reason,scenario,needed):
        group=f"article-{primary[index]['article']}"
        row={'id':f'head-{len(rows)+1:03d}', 'split':'validation' if index in validation_groups else 'train',
             'group':group,'style':style,'query':query,'history':history,'expected_route':label,
             'scenario':scenario,'rationale':reason,'source_articles':needed,
             'history_origin':'constructed_corpus_grounded' if history else 'no_history',
             'label_origin':'explicit_evidence_requirement; independent of model predictions'}
        row['request']=record(make_state(row))
        row['target']={'route':label}
        rows.append(row)
    for index,source in enumerate(primary):
        article=source['article']
        family=FAMILIES[index//10]
        other=auxiliary[index%10] if family=='comparison_coverage' else None
        sources[article]=source
        if other:
            sources[other['article']]=other
        search_templates=[
            f'Find the original opening passage of Article {article} and cite its source.',
            f'I need evidence for the beginning of Article {article}, with a source reference.',
            f'What does the opening of Article {article} say? Please use and cite the corpus text.',
            f'Locate Article {article} and explain its opening passage using the original source.',
            f'For my notes, supply the opening text of Article {article} and its citation.',
            f'What does Article {article} provide at the start about {source["title"].lower()}? Cite the text.',
            f'I am studying {source["title"].lower()}. Explain the opening provision of Article {article}, citing it.',
            f'Could you make a study card from the first passage of Article {article}, with a reference?',
            f'Please quote the beginning of Article {article} so I can check its wording.',
            f'Explain the initial provision under "{source["title"]}" in Article {article} using the corpus source.',
        ]
        add(index,'single','search',search_templates[index%10],[],
            'No conversation evidence is supplied; the user requests new provision text and a source.',
            'fresh_evidence_request',[article])
        if index%5<3:
            transformations=[
                f'Reformat only this supplied excerpt into bullets; add no facts: "{supported_answer(source)}"',
                f'Translate only the supplied text into Hindi, preserving its citation: "{supported_answer(source)}"',
                f'Explain only this provided passage in simpler words: "{supported_answer(source)}"',
            ]
            direct=transformations[index%5]
            reason='The entire source passage and citation are supplied in the latest message; only a transformation is requested.'
            scenario='supplied_text_transformation'
        elif index%5==3:
            direct=CHAT[index//5]
            reason='A conversational or general writing request requires no constitutional evidence.'
            scenario='conversation_or_general_writing'
        else:
            direct=UNCLEAR[index//5]
            reason='Essential subject or text is absent; ask for clarification without a speculative search.'
            scenario='missing_context_clarification'
        add(index,'single','no_search',direct,[],reason,scenario,
            [article] if index%5<3 else [])
        query,positive,negative,requirement=pair_history(source,other,family,index)
        needed=[other['article'],article] if other else [article]
        add(index,'multi','search',query,positive,
            'Required evidence is missing. '+requirement,family,needed)
        add(index,'multi','no_search',query,negative,
            'All passages and source references required by this request are already supplied in history. '+requirement,
            family,needed)
    validate(rows,evaluation)
    return rows,sources,evaluation


def validate(rows,evaluation):
    if len(rows)!=200 or len({r['id'] for r in rows})!=200:
        raise ValueError('Exactly 200 unique training-corpus cases are required')
    expected={(style,label):50 for style in ('single','multi') for label in ('search','no_search')}
    if Counter((r['style'],r['expected_route']) for r in rows)!=expected:
        raise ValueError('Each style/label cell must have exactly 50 cases')
    for split,n in [('train',40),('validation',10)]:
        counts=Counter((r['style'],r['expected_route']) for r in rows if r['split']==split)
        if counts!={key:n for key in expected}:
            raise ValueError('Split cell imbalance')
    if len({fingerprint(r) for r in rows})!=200:
        raise ValueError('Duplicate full inference inputs')
    eval_queries={normalized(r['query']) for r in evaluation}
    eval_inputs={fingerprint(r) for r in evaluation}
    eval_refs=article_refs('\n'.join(input_text(r) for r in evaluation))
    if any(normalized(r['query']) in eval_queries or fingerprint(r) in eval_inputs for r in rows):
        raise ValueError('Evaluation query or input copied into training corpus')
    refs=article_refs('\n'.join(input_text(r) for r in rows))
    if refs & eval_refs:
        raise ValueError('Article/topic overlap with evaluation inputs: '+str(refs & eval_refs))
    split_refs={split:article_refs('\n'.join(input_text(r) for r in rows if r['split']==split))
                for split in ('train','validation')}
    if split_refs['train'] & split_refs['validation']:
        raise ValueError('Article/topic leakage between training and validation')
    groups={}
    for row in rows:
        groups.setdefault(row['group'],[]).append(row)
        if bool(row['history']) != (row['style']=='multi'):
            raise ValueError('Invalid conversation style')
        if row['request']!=record(make_state(row)) or row['target']!={'route':row['expected_route']}:
            raise ValueError('Inference/target contract mismatch')
        if set(row['request']['state'])!={'conversation'}:
            raise ValueError('Unexpected state metadata')
        if 'available_tools' in json.dumps(row['request']):
            raise ValueError('Tool inventory must not appear in conversation-only requests')
    for group,members in groups.items():
        if len(members)!=4 or len({r['split'] for r in members})!=1:
            raise ValueError('Related cases crossed split boundary: '+group)
        multi=[r for r in members if r['style']=='multi']
        positive=next(r for r in multi if r['expected_route']=='search')
        negative=next(r for r in multi if r['expected_route']=='no_search')
        if positive['query']!=negative['query'] or len(positive['history'])!=len(negative['history']):
            raise ValueError('Counterfactual pair query/depth mismatch')
        if positive['history']==negative['history']:
            raise ValueError('Opposite labels on identical history')
        if 'Opening source passage:' not in input_text(negative):
            raise ValueError('No-search case lacks its required evidence')
    return rows


def write_jsonl(path,rows):
    path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')


def main():
    eval_hash=digest(EVALUATION)
    rows,sources,evaluation=build()
    # Tokenisation is CPU preprocessing, not model inference; no GPU model is loaded.
    from transformers import AutoTokenizer
    artifacts=json.loads((ROOT/'.cache/decision_sources/artifacts.json').read_text(encoding='utf-8'))
    tokenizer=AutoTokenizer.from_pretrained(str(ROOT/artifacts['modernjev']['path']),local_files_only=True)
    token_counts={}
    for row in rows:
        request=row['request']; question=request['questions']['route']
        first=question['instructions']+'\n\nSTATE:\n'+json.dumps(request['state'],ensure_ascii=False)
        counts=[len(tokenizer(first,f'{key}: {description}',add_special_tokens=True)['input_ids'])
                for key,description in question['criteria'].items()]
        row['max_candidate_tokens']=max(counts)
        token_counts[row['id']]=max(counts)
    if max(token_counts.values())>512:
        raise ValueError(f'Complete input exceeds planned 512-token pilot budget: {max(token_counts.values())}')
    if digest(EVALUATION)!=eval_hash:
        raise RuntimeError('Existing evaluation dataset changed during construction')
    DATA.mkdir(parents=True,exist_ok=True)
    write_jsonl(DATA/'finetuning_cases.jsonl',rows)
    for split in ('train','validation'):
        write_jsonl(DATA/f'{split}.jsonl',[r for r in rows if r['split']==split])
    (DATA/'source_excerpts.json').write_text(json.dumps(sources,indent=2,ensure_ascii=False),encoding='utf-8')
    manifest={'purpose':'ModernJEV head-only fine-tuning dataset; training not executed',
        'seed':SEED,'counts':{'total':200,'train':160,'validation':40,'single':100,'multi':100,
                           'search':100,'no_search':100},
        'split_policy':'Four related cases per group; 8 train / 2 validation groups per family; article-disjoint.',
        'history_generation':'Constructed by this script from corpus excerpts; not LLM-generated conversations.',
        'labels':'Authored from explicit evidence requirements; no model predictions used as gold.',
        'evaluation_dataset':str(EVALUATION.relative_to(ROOT)),
        'evaluation_sha256_before':eval_hash,'evaluation_sha256_after':digest(EVALUATION),
        'evaluation_n':len(evaluation),'corpus_sha256':digest(CORPUS),
        'evaluation_overlap':{'exact_queries':0,'full_inputs':0,'explicit_article_references':0},
        'train_validation_overlap':{'groups':0,'explicit_article_references':0},
        'inference_state_fields':['conversation'],'routing_contract':routing_contract(),
        'checkpoint':artifacts['modernjev'],
        'planned_training':'Freeze encoder, train existing scalar decision head with grouped candidate cross-entropy.',
        'candidate_tokens':{'max':max(token_counts.values()),'min':min(token_counts.values()),'budget':512,'truncations':0},
        'conversation_depth_counts':dict(Counter(len(r['history']) for r in rows if r['style']=='multi')),
        'files':{name:digest(DATA/name) for name in ('finetuning_cases.jsonl','train.jsonl','validation.jsonl','source_excerpts.json')}}
    (DATA/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    review=['# Head-only fine-tuning dataset — 200 cases','',
        '| Split | Single search | Single no search | Multi search | Multi no search | Total |',
        '|---|---:|---:|---:|---:|---:|',
        '| Training | 40 | 40 | 40 | 40 | 160 |',
        '| Validation | 10 | 10 | 10 | 10 | 40 |','',
        'Histories are constructed, source-grounded fixtures. No LLM generation or model training was run. '
        'Source passages come from the existing parent corpus; HTML and OCR separators are normalised for readability. '
        'The original 100 evaluation inputs are unchanged. No exact query, full input, or explicit article-reference overlap was found. '
        'Training and validation share broad scenario families and templates; this small synthetic pilot does not establish production generalisation.','',
        f"All complete candidate inputs fit 512 tokens: maximum {max(token_counts.values())}; no truncation.",'',
        '## Samples','']
    for row in rows:
        review += [f"### {row['id']} · {row['split']} · {row['style']} · {row['expected_route']}",'',
                   '**Latest question:** '+row['query'],'','**Gold rationale:** '+row['rationale'],'']
        for message in row['history']:
            review += [f"**{message['role']}:** {message['content']}",'']
    (DATA/'review.md').write_text('\n'.join(review),encoding='utf-8')
    print(json.dumps({'counts':manifest['counts'],'token_budget':manifest['candidate_tokens'],
                      'evaluation_unchanged':digest(EVALUATION)==eval_hash,'output':str(DATA)},indent=2))


if __name__=='__main__':
    main()
