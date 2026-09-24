from config import settings
SYSTEM_PROMPT='''You are Briefly AI, a factual text summarization assistant. Summarize only the supplied source. Do not introduce facts, statistics, names, events, or conclusions absent from the source. Preserve important qualifications and uncertainty. Do not claim independent verification.'''
class AIService:
    def __init__(self): self.enabled=bool(settings.groq_api_key)
    def summarize(self,text,summary_length):
        from groq import Groq
        client=Groq(api_key=settings.groq_api_key,timeout=settings.groq_timeout)
        style={'Very Short':'2 concise sentences','Short':'a compact paragraph of roughly 3 sentences','Balanced':'a concise paragraph of roughly 4-6 sentences','Detailed':'a compact multi-paragraph summary covering the major points'}.get(summary_length,'a concise summary')
        response=client.chat.completions.create(model=settings.groq_model,messages=[{'role':'system','content':SYSTEM_PROMPT},{'role':'user','content':f'Create {style} from the following source. Use only source content.\n\nSOURCE:\n{text[:settings.max_input_chars]}'}],temperature=.1,max_completion_tokens=1200)
        content=response.choices[0].message.content
        if not content: raise RuntimeError('The AI provider returned an empty summary.')
        return content.strip()
