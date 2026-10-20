"""Local lexical retrieval with TF-IDF cosine scoring and cited source chunks."""
import re,math
from collections import Counter
from common import *
STOP={'the','a','an','is','are','to','of','and','or','in','for','on','how','do','i','what','with','my','it','this','that','be','can'}
def tokens(s):return[w for w in re.findall(r'[a-z0-9_]+',s.lower())if w not in STOP]

def run(p):
    text=p.get('documents','');query=p.get('query','')
    if not isinstance(text,str)or not text.strip()or len(text)>MAX_CHARS:raise ValueError('Paste documentation under 2 MB.')
    qt=tokens(str(query))
    if not qt:raise ValueError('Enter a question containing a meaningful keyword.')
    docs=[];title='Untitled runbook';body=[]
    def flush():
        if body:docs.append((title,'\n'.join(body).strip()))
    for line in text.splitlines():
        if line.startswith('# '):flush();body=[];title=line[2:].strip()or 'Untitled runbook'
        else:body.append(line)
    flush()
    chunks=[]
    for title,body in docs:
        words=body.split()
        for start in range(0,len(words),140):
            chunk=' '.join(words[start:start+180]);chunks.append((title,chunk,start+1))
    if not chunks:raise ValueError('Documentation needs some content below the headings.')
    if len(chunks)>2000:raise ValueError('Use at most 2,000 documentation chunks.')
    terms=[Counter(tokens(x[1]))for x in chunks];df=Counter(t for counts in terms for t in counts)
    idf={t:math.log((1+len(chunks))/(1+n))+1 for t,n in df.items()}
    def vector(c):return{k:(1+math.log(v))*idf.get(k,0)for k,v in c.items()}
    q=vector(Counter(qt));qnorm=math.sqrt(sum(v*v for v in q.values()));scores=[]
    for i,c in enumerate(terms):
        v=vector(c);norm=math.sqrt(sum(x*x for x in v.values()));score=sum(q.get(t,0)*x for t,x in v.items())/(norm*qnorm)if norm*qnorm else 0
        if score>0:scores.append((score,i))
    scores.sort(key=lambda x:(-x[0],x[1]));selected=scores[:5];rows=[];findings=[];report=[]
    for n,(score,i)in enumerate(selected,1):
        title,chunk,start=chunks[i];citation=f'[{n}] {title} · word {start}'
        rows.append([citation,f'{score:.3f}',chunk]);findings.append(finding('info',citation,chunk));report.extend([citation,chunk,''])
    if not selected:findings.append(finding('warning','No matching evidence found','Try terms used in the documentation. This tool does not invent an answer when retrieval finds no matches.'))
    else:findings.insert(0,finding('success','Relevant source passages retrieved','These are verbatim source excerpts ranked by lexical similarity, not a generated answer or confidence score.'))
    return result('Evidence search complete',[metric('Documents',len(docs)),metric('Chunks',len(chunks)),metric('Matches',len(selected)),metric('Mode','Local TF-IDF')],['Citation','Similarity','Source excerpt'],rows,findings,[{'label':chunks[i][0][:35],'value':round(score*100,1)}for score,i in selected],[{'name':'retrieved-evidence.txt','content':'\n'.join(report)or 'No matching evidence.'}])
