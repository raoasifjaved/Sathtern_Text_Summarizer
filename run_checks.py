from pathlib import Path
import ast,tempfile
from summarizer import TextSummarizer
from database import SummaryDB
from exporters import export_markdown,export_txt,export_pdf
BASE=Path(__file__).resolve().parent
print('[1/5] Checking Python syntax...')
for n in ['app.py','config.py','summarizer.py','ai_service.py','database.py','exporters.py','run_checks.py']: ast.parse((BASE/n).read_text(encoding='utf-8'),filename=n)
print('      PASS')
sample=(BASE/'samples'/'sample_long_text.txt').read_text(encoding='utf-8'); s=TextSummarizer(); r=s.summarize(sample,'Balanced'); m=s.metrics(sample,r['summary'])
print('[2/5] Checking local NLP summarization...'); assert r['summary'] and m['summary_words']<m['original_words']; print('      PASS')
print('[3/5] Checking exact compression calculation...'); exp=round((1-m['summary_words']/m['original_words'])*100,1); assert m['compression_pct']==exp; print(f'      PASS ({m["summary_words"]}/{m["original_words"]} -> {exp:.1f}% compression)')
print('[4/5] Checking database persistence...')
with tempfile.TemporaryDirectory() as td:
    db=SummaryDB(str(Path(td)/'test.db')); payload={'title':'Sample','original_text':sample,'summary':r['summary'],'engine':'Local NLP','summary_length':'Balanced','metrics':m,'sentence_details':r['sentence_details']}; rid=db.save_summary(payload); got=db.get_summary(rid); assert got['title']=='Sample' and len(db.list_summaries())==1
print('      PASS')
print('[5/5] Checking exports...'); assert '# Text Summary Report' in export_markdown(payload) and 'Original words' in export_txt(payload) and export_pdf(payload)[:4]==b'%PDF'; print('      PASS')
print('\nALL CHECKS PASSED')
