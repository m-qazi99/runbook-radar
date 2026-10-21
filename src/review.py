"""Deterministic review priorities derived from an existing studio result.

No network calls, generated answers, or automatic operational changes.
"""
import json
PROJECT = 'runbook-radar'
NAME = 'Runbook Radar'

def attach(request, result):
    lab = result['lab']
    items = []

    def add(key, severity, title, detail):
        items.append({'id': key, 'severity': severity, 'title': title, 'detail': detail})
    if not lab['matches']:
        add('no-match', 'high', 'No matching source passage', 'Use a supported question or add relevant source material; an empty lexical result does not justify inventing an answer.')
    labels = {e['expected'] for e in lab['evaluation']}
    uncovered = [d['title'] for d in lab['documents'] if d['title'] not in labels]
    if uncovered:
        add('label-coverage', 'review', 'Documents without evaluation labels', ', '.join(uncovered) + '. Add representative questions before making corpus-wide quality claims.')
    for i, e in enumerate(lab['evaluation']):
        rank = e['ranks'][lab['algorithm']]
        if rank is None or rank > int(request.get('top_k', 4)):
            add('query-' + str(i), 'high', 'Expected source outside top K', e['query'] + ' → ' + e['expected'] + '; first matching chunk rank: ' + (str(rank) if rank else 'no match') + '.')
    if len(lab['evaluation']) < 5:
        add('sample-size', 'review', 'Small evaluation set', str(len(lab['evaluation'])) + ' labeled query/queries. Treat the result as a synthetic exercise, not a general benchmark.')
    add('source', 'info', 'Read the complete source', 'BM25 and TF-IDF rank lexical overlap. A score is not confidence, correctness, or authorization to act.')
    items.sort(key=lambda x: {'high': 0, 'review': 1, 'info': 2}[x['severity']])
    review = {'version': '2.1.0', 'project': PROJECT, 'name': NAME, 'items': items, 'summary': {level: sum((x['severity'] == level for x in items)) for level in ['high', 'review', 'info']}, 'scope': 'Deterministic review aid from this experiment. Checklist completion does not certify correctness, safety, production readiness, or privacy.'}
    report = '# ' + NAME + ' — review handoff\n\n' + review['scope'] + '\n\n'
    for item in items:
        title = item['title'].replace('\n', ' ').replace('\r', ' ')
        detail = item['detail'].replace('\n', ' ').replace('\r', ' ')
        report += '- [ ] [' + item['severity'].upper() + '] ' + title + '\n  ' + detail + '\n'
    result['review'] = review
    result['artifacts'] += [{'name': 'review-handoff.md', 'content': report}, {'name': 'review-priorities.json', 'content': json.dumps(review, indent=2)}]
    return result
