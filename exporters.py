from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer
from reportlab.lib.styles import getSampleStyleSheet
def export_markdown(r):
    m=r['metrics']
    return (f"# Text Summary Report — {r['title']}\n\n"
            f"**Engine:** {r['engine']}\n\n## Original Text\n\n{r['original_text']}\n\n"
            f"## Summarized Text\n\n{r['summary']}\n\n## Metrics\n\n"
            f"- Original words: {m['original_words']}\n- Summary words: {m['summary_words']}\n- Compression: {m['compression_pct']:.1f}%\n\n"
            "> Compare the summary with the original for important content.\n")
def export_txt(r): return export_markdown(r).replace('# ','').replace('**','')
def export_pdf(r):
    b=BytesIO(); doc=SimpleDocTemplate(b,pagesize=A4,rightMargin=40,leftMargin=40,topMargin=40,bottomMargin=40); styles=getSampleStyleSheet(); story=[]
    blocks=[f"Text Summary Report — {r['title']}",f"Engine: {r['engine']}",'Original Text',r['original_text'],'Summarized Text',r['summary'],'Metrics',f"Original words: {r['metrics']['original_words']}",f"Summary words: {r['metrics']['summary_words']}",f"Compression: {r['metrics']['compression_pct']:.1f}%"]
    for i,block in enumerate(blocks):
        safe=block.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
        style=styles['Title'] if i==0 else styles['Heading2'] if block in {'Original Text','Summarized Text','Metrics'} else styles['BodyText']
        story.append(Paragraph(safe.replace('\n','<br/>'),style)); story.append(Spacer(1,8))
    doc.build(story); return b.getvalue()
