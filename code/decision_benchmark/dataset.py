"""100 independently labelled cases with real shared answer replay."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ARTICLES = ['14','15','16','17','18','19','20','21','21A','22','23','24','25',
            '26','27','28','29','30','32','39A','44','51A','72','110','123']
NEW_ARTICLES = ['324','326','368','280','148','356','352','300A','226','124','143',
                '161','165','249','262','263','312','315','338','243G','243W','246','265','275','359']
DIRECT = [
    'Hello!', 'Good morning', 'Thanks for helping', 'Okay, understood', 'What can you help me with?',
    'How should I ask a question here?', 'Tell me your role', 'Can we continue later?',
    'Tell me a short joke about studying', 'Suggest a name for my study group',
    'Rewrite this politely: Send me the notes now.', 'Fix grammar: She have three books.',
    'Translate to Hindi: Thank you for your help.', 'Shorten this: I am writing to request your assistance.',
    'Turn this into bullets: Read, revise, practice.', 'Make this formal: Hey, I need a break.',
    'Explain that', 'Compare those two', 'Give me its citation', 'What about the other article?',
    'Which document did I upload?', 'I meant the second one', 'Summarize the missing attachment',
    'What article am I thinking about?', 'Translate your previous answer',
]
TRANSFORMS = ['Summarize your answer in one sentence.', 'Explain your answer in simpler words.',
              'Translate your answer to Hindi.', 'Turn your answer into bullet points.',
              'Repeat the article citation you already gave.']

def article_source(article, parents):
    pattern = re.compile(r'(?m)^\[?' + re.escape(article) + r'\.\s')
    candidates = []
    for parent in parents:
        if any('schedule' in str(h).lower() or 'contents' in str(h).lower()
               for h in parent.get('heading_path', [])):
            continue
        text = re.sub(r'<sup>\d+</sup>', '', parent['text'])
        match = pattern.search(text)
        if not match:
            continue
        rest = text[match.start():]
        offset = match.end()-match.start()
        next_article = re.search(r'(?m)^\[?\d+[A-Z]*\.\s', rest[offset:])
        if next_article:
            rest = rest[:offset+next_article.start()]
        if len(rest) > 120 and 'Contents' not in ' '.join(parent.get('heading_path', [])):
            candidates.append({'parent_id': parent['parent_id'], 'article': article, 'text': rest[:6000]})
    if not candidates:
        raise ValueError('No substantive corpus source for Article ' + article)
    return candidates[0]

def build(replays):
    rows = []
    def add(style, label, group, query, history, rationale, provenance=None):
        rows.append({'id': f'{style}-{len(rows)+1:03d}', 'style': style, 'group': group,
                     'query': query, 'history': history, 'expected_route': label,
                     'rationale': rationale, 'history_provenance': provenance})
    for i, article in enumerate(ARTICLES):
        add('single', 'search', f'single-search-{i}',
            f'Explain Article {article} of the Constitution of India and cite the provision.', [],
            'New constitutional facts and an article citation; no evidence in history.')
        add('single', 'no_search', f'single-direct-{i}', DIRECT[i], [],
            'Conversation, supplied-text transformation, or clarification of missing context.')
    for i, article in enumerate(ARTICLES):
        replay = replays[article]
        history = replay['history']
        provenance = {'model': replay['model'], 'source': replay['source'],
                      'answer_generation': 'actual provider responses; source-grounded reference replay'}
        add('multi', 'no_search', f'multi-{article}', TRANSFORMS[i % len(TRANSFORMS)], history,
            'Only transform or repeat the grounded answer and citation already present.', provenance)
        add('multi', 'search', f'multi-{article}',
            (f'Keep it simple, and compare that with Article {NEW_ARTICLES[i]} with a source citation.'
             if i % 2 == 0 else f'Now explain Article {NEW_ARTICLES[i]} and cite its text.'), history,
            f'Article {NEW_ARTICLES[i]} is a new subject absent from this reference conversation.', provenance)
    return rows

def validate(rows):
    if len(rows) != 100 or len({r['id'] for r in rows}) != 100:
        raise ValueError('Expected exactly 100 unique cases')
    for style in ('single', 'multi'):
        for label in ('search', 'no_search'):
            if sum(r['style'] == style and r['expected_route'] == label for r in rows) != 25:
                raise ValueError('Required 25 cases in every style/label cell')
    for row in rows:
        if bool(row['history']) != (row['style'] == 'multi'):
            raise ValueError('Conversation-style mismatch')
        if row['style'] == 'multi':
            if len(row['history']) not in (2, 4) or not row['history_provenance']:
                raise ValueError('Reference history/provenance missing')
            target = NEW_ARTICLES[ARTICLES.index(row['group'][6:])]
            if re.search(r'\bArticle\s+' + re.escape(target) + r'\b', ' '.join(m['content'] for m in row['history']), re.I):
                raise ValueError('New target already present in history: ' + row['id'])
    return rows

def generate():
    from .adapters import BaselineAdapter
    from backend.services.langgraph_workflow import _ai_message
    provider = BaselineAdapter()
    parents = json.loads((ROOT/'data/chunks/parentchunks2.json').read_text(encoding='utf-8'))
    sources = {article: article_source(article, parents) for article in ARTICLES}
    cache = HERE/'reference_replays.json'
    replays = json.loads(cache.read_text(encoding='utf-8')) if cache.exists() else {}
    for i, article in enumerate(ARTICLES):
        if article in replays:
            continue
        source = sources[article]
        seed = f'Explain Article {article} briefly and cite it.'
        messages = [{'role': 'system', 'content':
            'Answer using only the provided article. Use at most 35 words. Include the article number '
            'and parent identifier as a citation. Do not mention other articles.\nSOURCE:\n' +
            source['parent_id'] + '\n' + source['text']}, {'role': 'user', 'content': seed}]
        response = _ai_message(provider.provider.chat(model=provider.settings.generation_model,
                                messages=messages, think=False))
        answer = str(response.content).strip()
        if not answer or response.tool_calls or len(answer.split()) > 60:
            raise ValueError('Invalid reference answer for ' + article)
        if article.lower() not in answer.lower() or source['parent_id'] not in answer:
            raise ValueError('Reference citation missing for ' + article)
        history = [{'role':'user','content':seed}, {'role':'assistant','content':answer}]
        if i % 2:
            followup = 'Restate the same answer in a single short sentence, preserving its citation.'
            messages += history[1:] + [{'role':'user','content':followup}]
            response = _ai_message(provider.provider.chat(model=provider.settings.generation_model,
                                    messages=messages, think=False))
            answer2 = str(response.content).strip()
            if not answer2 or response.tool_calls or len(answer2.split()) > 60:
                raise ValueError('Invalid reference follow-up for ' + article)
            history += [{'role':'user','content':followup}, {'role':'assistant','content':answer2}]
        replays[article] = {'history':history, 'model':provider.settings.generation_model, 'source':source}
        cache.write_text(json.dumps(replays, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f'Reference conversations: {len(replays)}/25', flush=True)
    rows = validate(build(replays))
    (HERE/'cases.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows), encoding='utf-8')
    return rows
