"""Inspectable BM25/TF-IDF experiment with chunk controls and labeled evaluation."""
import json,math,re
from collections import Counter
from common import *

def run(p):
    from engine import tokens
    text=p.get('documents','');query=p.get('query','')
    if not isinstance(text,str) or not text.strip() or len(text)>MAX_CHARS:raise ValueError('Paste Markdown documentation under 2 MB.')
    try:size=int(p.get('chunk_size',70));overlap=int(p.get('overlap',15));k=int(p.get('top_k',4))
    except (TypeError,ValueError):raise ValueError('Chunk controls must be integers.')
    if not 30<=size<=300 or not 0<=overlap<size or not 1<=k<=10:raise ValueError('Chunk size: 30–300; overlap: 0 to size−1; top K: 1–10.')
    algorithm=p.get('algorithm','bm25')
    if algorithm not in {'bm25','tfidf'}:raise ValueError('Choose bm25 or tfidf.')
    docs=[];title='Untitled';body=[]
    def flush():
        if ' '.join(body).strip():docs.append({'title':title,'body':'\n'.join(body)})
    for line in text.splitlines():
        if line.startswith('# '):flush();body=[];title=line[2:].strip() or 'Untitled'
        else:body.append(line)
    flush();chunks=[]
    for docid,d in enumerate(docs):
        words=d['body'].split();start=0
        while start<len(words):
            chunks.append({'id':f'D{docid+1}-C{1+start//(size-overlap)}','doc':docid,'title':d['title'],'text':' '.join(words[start:start+size]),'start':start+1,'end':min(start+size,len(words))})
            if start+size>=len(words):break
            start+=size-overlap
    if not chunks or len(chunks)>1000:raise ValueError('Use 1–1,000 chunks. Increase chunk size for large documents.')
    counts=[Counter(tokens(c['text'])) for c in chunks];df=Counter(t for c in counts for t in c);N=len(chunks);avg=sum(sum(c.values()) for c in counts)/N or 1
    def retrieve(q,mode):
        qt=Counter(tokens(q));scores=[]
        for i,ct in enumerate(counts):
            terms=[];score=0.;dl=sum(ct.values())
            if mode=='bm25':
                for term in qt:
                    tf=ct[term];idf=math.log(1+(N-df[term]+.5)/(df[term]+.5));contribution=idf*tf*2.5/(tf+1.5*(.25+.75*dl/avg)) if tf else 0
                    score+=contribution
                    if contribution:terms.append({'term':term,'score':round(contribution,4),'frequency':tf})
            else:
                idf=lambda t:math.log((1+N)/(1+df[t]))+1
                v={t:(1+math.log(f))*idf(t) for t,f in ct.items()};qv={t:(1+math.log(f))*idf(t) for t,f in qt.items() if t in df};norm=math.sqrt(sum(x*x for x in v.values())*sum(x*x for x in qv.values()))
                for term,x in qv.items():
                    contribution=x*v.get(term,0)/norm if norm else 0;score+=contribution
                    if contribution:terms.append({'term':term,'score':round(contribution,4),'frequency':ct[term]})
            if score>0:scores.append({**chunks[i],'score':round(score,5),'terms':terms})
        return sorted(scores,key=lambda x:(-x['score'],x['id']))
    if not tokens(str(query)):raise ValueError('Enter a question with meaningful keywords.')
    matches=retrieve(str(query),algorithm)[:k];other=retrieve(str(query),'tfidf' if algorithm=='bm25' else 'bm25')[:k]
    try:questions=json.loads(p.get('evaluation','[]'))
    except (TypeError,ValueError):raise ValueError('Evaluation must be a JSON array.')
    if not isinstance(questions,list) or len(questions)>25:raise ValueError('Use at most 25 evaluation questions.')
    evaluation=[];known={d['title'] for d in docs}
    for item in questions:
        if not isinstance(item,dict) or not isinstance(item.get('query'),str) or item.get('expected') not in known:raise ValueError('Each evaluation needs a query and an expected document title that exists.')
        ranks={mode:next((i+1 for i,x in enumerate(retrieve(item['query'],mode)) if x['title']==item['expected']),None) for mode in ['bm25','tfidf']}
        evaluation.append({**item,'ranks':ranks})
    scores={mode:{'mrr':round(sum(1/x['ranks'][mode] if x['ranks'][mode] else 0 for x in evaluation)/len(evaluation),3) if evaluation else None,'hit_at_k':round(sum(x['ranks'][mode] is not None and x['ranks'][mode]<=k for x in evaluation)/len(evaluation),3) if evaluation else None} for mode in ['bm25','tfidf']}
    note='No matching evidence found' if not matches else 'Source passages, not generated answers'
    out=result('Retrieval experiment complete',[metric('Documents',len(docs)),metric('Chunks',N),metric('Matches',len(matches)),metric('Retriever',algorithm.upper())],['Citation','Score','Passage'],[[x['id']+' · '+x['title'],x['score'],x['text']] for x in matches],[finding('info',note,'Scores measure lexical ranking, not truth or confidence. Evaluation uses only the questions and expected titles supplied here.')],artifacts=[{'name':'retrieval-experiment.json','content':json.dumps({'algorithm':algorithm,'chunk_size':size,'overlap':overlap,'matches':matches,'evaluation':evaluation,'scores':scores},indent=2)}])
    out['lab']={'matches':matches,'comparison':other,'chunks':chunks,'evaluation':evaluation,'scores':scores,'query_terms':tokens(str(query)),'algorithm':algorithm,'documents':[{'title':d['title'],'words':len(d['body'].split())} for d in docs]};return out
