import os
import re
from collections import Counter

import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()
STOP_WORDS = {"a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "in", "is", "it", "of", "on", "or", "that", "the", "to", "was", "were", "with"}


def extractive_summary(text: str, sentence_count: int) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    if len(sentences) <= sentence_count:
        return text.strip()
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    frequencies = Counter(word for word in words if word not in STOP_WORDS)
    scores = {sentence: sum(frequencies[word] for word in re.findall(r"\b[a-zA-Z]+\b", sentence.lower())) for sentence in sentences}
    selected = set(sorted(sentences, key=lambda sentence: scores[sentence], reverse=True)[:sentence_count])
    return " ".join(sentence for sentence in sentences if sentence in selected)


@st.cache_resource
def get_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def ai_summary(text: str, sentence_count: int) -> str | None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        response = get_client(api_key).models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3-flash-preview"),
            contents=f"Summarize this text in no more than {sentence_count} clear sentences. Preserve key facts.\n\n{text}",
        )
        return (response.text or "").strip() or None
    except Exception:
        return None


st.set_page_config(page_title="Text summarizer | Sathtern", page_icon=":material/summarize:")
st.title("Text summarization tool")
st.caption("Sathtern")
text = st.text_area("Long text", height=280, placeholder="Paste the text you want to summarize...")
sentence_count = st.slider("Summary length (sentences)", 1, 6, 3)
use_ai = st.toggle("Use Gemini AI when configured", value=True)

if st.button("Generate summary", type="primary", disabled=not text.strip()):
    summary = ai_summary(text, sentence_count) if use_ai else None
    source = "Gemini AI" if summary else "extractive NLP fallback"
    summary = summary or extractive_summary(text, sentence_count)
    left, right = st.columns(2)
    with left:
        st.subheader("Original text")
        st.write(text)
    with right:
        st.subheader("Summary")
        st.write(summary)
        st.caption(f"Generated with {source}.")
