import streamlit as st
import re
from transformers import pipeline

# ====== Summarizer ====== #
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def split_into_chunks(text, max_words=100):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks, chunk = [], []
    word_count = 0
    for s in sentences:
        w = len(s.split())
        if word_count + w <= max_words:
            chunk.append(s)
            word_count += w
        else:
            chunks.append(" ".join(chunk))
            chunk = [s]
            word_count = w
    if chunk:
        chunks.append(" ".join(chunk))
    return chunks

def summarize_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    chunks = split_into_chunks(text, max_words=100)
    summaries = [summarizer(c, max_length=150, min_length=50, do_sample=False)[0]['summary_text'] for c in chunks]
    final_summary = " ".join(summaries)
    final_summary = re.sub(r'\b(\w+), \1\b', r'\1', final_summary)
    return final_summary

# ====== App ====== #
st.header("📚 Ringkasan Materi")
text_input = st.text_area("Tempel teks di sini", height=250)

if st.button("🔍 Buat Ringkasan"):
    if text_input.strip():
        summary = summarize_text(text_input)
        st.markdown(f"""
        <div style="
            background-color: #ffffff;
            color: black;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid rgba(0,0,0,0.1);
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            white-space: pre-wrap;
        ">
        {summary}
        </div>
        """, unsafe_allow_html=True)

        # ===== Tombol copy ===== #
        st.markdown(f"""
        <button onclick="navigator.clipboard.writeText(`{summary}`)">📋 Copy Ringkasan</button>
        <script>
        const btn = document.querySelector("button");
        btn.addEventListener("click", () => {{
            alert("Ringkasan berhasil disalin ke clipboard!");
        }});
        </script>
        """, unsafe_allow_html=True)

    else:
        st.info("Masukkan teks terlebih dahulu.")
