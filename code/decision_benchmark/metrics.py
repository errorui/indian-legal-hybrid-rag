"""Same binary metrics for tool calling and every decision model."""
import math
import random
import statistics

def summarize(rows):
    n = len(rows)
    tp = sum(r['expected_route']=='search' and r.get('route')=='search' for r in rows)
    tn = sum(r['expected_route']=='no_search' and r.get('route')=='no_search' for r in rows)
    fp = sum(r['expected_route']=='no_search' and r.get('route')=='search' for r in rows)
    fn = sum(r['expected_route']=='search' and r.get('route')=='no_search' for r in rows)
    failures = sum(r.get('route') not in ('search','no_search') for r in rows)
    positive = sum(r['expected_route']=='search' for r in rows)
    negative = n-positive
    precision = tp/(tp+fp) if tp+fp else 0
    recall = tp/positive if positive else 0
    specificity = tn/negative if negative else 0
    f1 = 2*precision*recall/(precision+recall) if precision+recall else 0
    p0 = tn/(tn+fn) if tn+fn else 0
    f0 = 2*p0*specificity/(p0+specificity) if p0+specificity else 0
    p = (tp+tn)/n if n else 0
    z=1.96
    denom=1+z*z/n if n else 1
    center=(p+z*z/(2*n))/denom if n else 0
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/denom if n else 0
    times=sorted(r['duration_ms'] for r in rows if not r.get('error'))
    return {'n':n, 'accuracy':p, 'accuracy_wilson_95':[max(0,center-half),min(1,center+half)],
            'search_precision':precision,'search_recall':recall,'search_f1':f1,
            'macro_f1':(f1+f0)/2, 'true_search':tp,'true_no_search':tn,
            'unnecessary_search':fp,'missed_search':fn,'failures':failures,
            'median_ms':statistics.median(times) if times else None,
            'p95_ms':times[max(0,math.ceil(.95*len(times))-1)] if times else None}

def paired_accuracy_difference(candidate, baseline):
    baseline={r['id']:r for r in baseline}
    groups={}
    for row in candidate:
        other=baseline[row['id']]
        delta=int(row.get('route')==row['expected_route'])-int(other.get('route')==other['expected_route'])
        groups.setdefault(row['group'],[]).append(delta)
    values=list(groups.values())
    rng=random.Random(20261002)
    samples=[]
    for _ in range(4000):
        drawn=[rng.choice(values) for _ in values]
        samples.append(sum(sum(v) for v in drawn)/sum(len(v) for v in drawn))
    samples.sort()
    return {'difference':sum(sum(v) for v in values)/sum(map(len,values)),
            'cluster_bootstrap_95':[samples[100],samples[3899]],'groups':len(values)}
