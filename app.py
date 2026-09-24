import streamlit as st
from config import settings
from summarizer import TextSummarizer
from ai_service import AIService
from database import SummaryDB
from exporters import export_markdown, export_txt, export_pdf

st.set_page_config(page_title='Briefly AI', page_icon='📝', layout='wide')
st.markdown('''<style>.block-container{padding-top:1.5rem}.hero{padding:1.4rem 1.5rem;border:1px solid rgba(127,127,127,.18);border-radius:20px;margin-bottom:1rem;background:linear-gradient(135deg,rgba(79,70,229,.12),rgba(16,185,129,.10))}</style>''', unsafe_allow_html=True)
if 'summary_result' not in st.session_state: st.session_state.summary_result = None

db=SummaryDB(settings.database_path); summarizer=TextSummarizer(); ai=AIService()
with st.sidebar:
    st.title('📝 Briefly AI'); st.caption('Reliable text summarization workspace'); st.divider()
    engine=st.radio('Summarization engine',['AI + Local Fallback','Local NLP'])
    length=st.select_slider('Summary length',options=['Very Short','Short','Balanced','Detailed'],value='Balanced')
    st.divider()
    if ai.enabled and engine=='AI + Local Fallback': st.success(f'AI connected • {settings.groq_model}')
    elif engine=='Local NLP': st.info('Local NLP mode')
    else: st.warning('No API key • Local fallback')
    st.divider(); st.subheader('Recent summaries')
    for item in db.list_summaries(8):
        if st.button(f"{item['title']} · {item['word_count']} words"[:42],key=f"s_{item['id']}"):
            loaded=db.get_summary(item['id'])
            if loaded: st.session_state.summary_result=loaded; st.rerun()

st.markdown('<div class="hero"><h1>📝 Briefly AI — Intelligent Text Summarizer</h1><p>Turn long-form content into concise, readable summaries while keeping the original text visible for comparison.</p></div>',unsafe_allow_html=True)
st.subheader('1. Enter Long Text')
title=st.text_input('Document title',placeholder='e.g. AI in Modern Healthcare')
text=st.text_area('Paste your long text here',height=330,placeholder='Paste an article, research notes, report, or other long-form text...')
up=st.file_uploader('Or upload a TXT file',type=['txt'])
if up is not None:
    text=up.getvalue().decode('utf-8',errors='replace').strip(); st.info(f'Loaded {len(text.split()):,} words from {up.name}.') if text else st.warning('The uploaded TXT file is empty.')
c1,c2=st.columns([2,1])
with c1: st.caption('Best results come from multi-paragraph content.')
with c2: st.metric('Input words',len(text.split()) if text else 0)

if st.button('✨ Generate Summary',type='primary',use_container_width=True):
    clean=text.strip()
    if not clean: st.error('Please enter or upload some text first.')
    elif len(clean.split())<settings.min_input_words: st.error(f'Please provide at least {settings.min_input_words} words.')
    elif len(clean)>settings.max_input_chars: st.error(f'Input is too long. Maximum is {settings.max_input_chars:,} characters.')
    else:
        local=summarizer.summarize(clean,length)
        if engine=='AI + Local Fallback' and ai.enabled:
            try: summary=ai.summarize(clean,length); used='Groq AI'
            except Exception as exc: st.warning(f'AI failed; local fallback used: {exc}'); summary=local['summary']; used='Local NLP Fallback'
        else: summary=local['summary']; used='Local NLP'
        result={'title':title.strip() or 'Untitled Document','original_text':clean,'summary':summary.strip(),'engine':used,'summary_length':length,'metrics':summarizer.metrics(clean,summary),'sentence_details':local['sentence_details']}
        result['id']=db.save_summary(result); st.session_state.summary_result=result; st.success('Summary generated and saved.')

if st.session_state.summary_result:
    r=st.session_state.summary_result; m=r['metrics']; st.divider(); st.subheader('2. Summary Results')
    a,b,c,d=st.columns(4); a.metric('Original words',m['original_words']); b.metric('Summary words',m['summary_words']); c.metric('Compression',f"{m['compression_pct']:.1f}%"); d.metric('Engine',r['engine'])
    left,right=st.columns(2)
    with left: st.markdown('### 📄 Original Text'); st.text_area('Original',r['original_text'],height=520,disabled=True,label_visibility='collapsed')
    with right: st.markdown('### ✨ Summarized Text'); st.text_area('Summary',r['summary'],height=520,disabled=True,label_visibility='collapsed')
    t1,t2,t3=st.tabs(['📊 Metrics','🧩 Sentence Evidence','📦 Export'])
    with t1:
        st.markdown('#### Transparent calculation'); st.code('Compression % = (1 - Summary Words / Original Words) × 100',language='text')
        st.write(f"= (1 - {m['summary_words']} / {m['original_words']}) × 100 = **{m['compression_pct']:.1f}%**")
        st.caption('Compression is a length metric, not a quality or factual-accuracy score.')
    with t2:
        for item in r['sentence_details']: st.write(f"**{item['rank']}.** {item['sentence']}  \\nScore: `{item['score']:.3f}`")
    with t3:
        st.download_button('⬇ Download Markdown',export_markdown(r),file_name='text_summary_report.md',mime='text/markdown',use_container_width=True)
        st.download_button('⬇ Download TXT',export_txt(r),file_name='text_summary_report.txt',mime='text/plain',use_container_width=True)
        st.download_button('⬇ Download PDF',export_pdf(r),file_name='text_summary_report.pdf',mime='application/pdf',use_container_width=True)
st.divider(); st.caption('Briefly AI • AI output is advisory. Compare the summary with the original source for important content.')
