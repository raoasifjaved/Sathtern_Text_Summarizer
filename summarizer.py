import math,re
from collections import Counter
STOPWORDS=set('a an the and or but if then than so because as of to in on for from with by at is are was were be been being this that these those it its they their he she his her we our you your i my me us do does did will would can could should may might have has had not no yes into over under about after before during through while which who whom what when where how also very more most some such there here only all each'.split())
WORD_RE=re.compile(r"[A-Za-z][A-Za-z0-9'-]*")
def split_sentences(text): return [s.strip() for s in re.split(r'(?<=[.!?])\s+',re.sub(r'\s+',' ',text).strip()) if s.strip()]
def tokens(text): return [t.lower() for t in WORD_RE.findall(text)]
class TextSummarizer:
    def summarize(self,text,summary_length='Balanced'):
        sentences=split_sentences(text); freq=Counter(t for t in tokens(text) if t not in STOPWORDS); max_freq=max(freq.values()) if freq else 1; scored=[]; total=len(sentences)
        for i,s in enumerate(sentences):
            words=[t for t in tokens(s) if t not in STOPWORDS]
            content=sum(freq[w]/max_freq for w in words)/math.sqrt(len(words)) if words else 0
            pos=1.15 if i<max(2,total*.15) else 1.0
            length=1.0 if 8<=len(words)<=45 else .85
            cue=.15 if re.search(r'\b(in conclusion|overall|important|key|results?|findings?|therefore|however)\b',s,re.I) else 0
            scored.append({'index':i,'sentence':s,'score':content*pos*length+cue})
        n=min({'Very Short':2,'Short':max(2,math.ceil(total*.20)),'Balanced':max(3,math.ceil(total*.30)),'Detailed':max(4,math.ceil(total*.42))}.get(summary_length,3),total)
        selected=sorted(sorted(scored,key=lambda x:x['score'],reverse=True)[:n],key=lambda x:x['index'])
        return {'summary':' '.join(x['sentence'] for x in selected),'sentence_details':[{'rank':i,'sentence':x['sentence'],'score':round(x['score'],3)} for i,x in enumerate(selected,1)]}
    def metrics(self,original,summary):
        ow=len(original.split()); sw=len(summary.split()); cp=(1-sw/ow)*100 if ow else 0
        return {'original_words':ow,'summary_words':sw,'compression_pct':round(cp,1)}
