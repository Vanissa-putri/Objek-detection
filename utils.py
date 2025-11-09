import docx
import PyPDF2
import pandas as pd
import pytesseract
from PIL import Image
import re
import random
from transformers import pipeline
import streamlit as st

# ====== SUMMARIZATION MODEL (RINGAN & CEPAT) ====== #
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# ====== FUNGSIONALITAS FILE ====== #
def read_file_content(uploaded_file):
    """Baca isi file (txt, pdf, docx, csv, xlsx) dan kembalikan teks bersih"""
    file_type = uploaded_file.type

    if file_type == "text/plain":
        return uploaded_file.read().decode("utf-8")

    elif file_type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        text = " ".join(page.extract_text() for page in reader.pages if page.extract_text())
        return text.strip()

    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])

    elif file_type in ["text/csv", "application/vnd.ms-excel",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
        df = pd.read_csv(uploaded_file) if file_type == "text/csv" else pd.read_excel(uploaded_file)
        return df.to_string(index=False)

    else:
        return "Format file tidak didukung."

def extract_text_from_image(image_file):
    """Ekstrak teks dari file gambar"""
    img = Image.open(image_file)
    text = pytesseract.image_to_string(img, lang="ind")
    return text.strip()

# ====== FUNGSIONALITAS SUMMARIZATION ====== #
def split_into_chunks(text, max_words=500):
    """Pisahkan teks panjang jadi beberapa potongan agar cepat diproses model"""
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks, chunk = [], []
    word_count = 0

    for sentence in sentences:
        words = sentence.split()
        if word_count + len(words) <= max_words:
            chunk.append(sentence)
            word_count += len(words)
        else:
            chunks.append(" ".join(chunk))
            chunk = [sentence]
            word_count = len(words)
    if chunk:
        chunks.append(" ".join(chunk))
    return chunks

def summarize_text(text):
    """Ringkas teks menjadi 1 paragraf panjang, hapus duplikasi kata sederhana"""
    if len(text.split()) < 20:
        return text.strip()

    chunks = split_into_chunks(text, max_words=500)
    summaries = []

    for chunk in chunks:
        result = summarizer(chunk, max_length=500, min_length=100, do_sample=False)
        summaries.append(result[0]['summary_text'])

    final_summary = " ".join(summaries)
    final_summary = re.sub(r'\s+', ' ', final_summary).strip()
    final_summary = re.sub(r'\b(\w+), \1\b', r'\1', final_summary)  # hapus duplikasi kata

    return final_summary

# ====== FUNGSIONALITAS QUIZ ====== #
def generate_quiz_from_text(text, num_questions=5):
    """Buat latihan soal sederhana lebih cepat"""
    sentences = [s for s in re.split(r'(?<=[.!?]) +', text) if len(s.split()) > 6]
    if not sentences:
        return []

    selected = random.sample(sentences, min(num_questions, len(sentences)))
    questions = []

    for s in selected:
        words = s.split()
        missing_word = words[len(words)//2]
        question_text = s.replace(missing_word, "_____")
        options = list({missing_word} | set(words[:5]))[:4]
        questions.append({
            "question": question_text,
            "options": options,
            "answer": missing_word
        })

    return questions

# ====== FUNGSIONALITAS STREAMLIT UNTUK COPY ====== #
def display_summary_with_copy(summary_text):
    """Tampilkan ringkasan di Streamlit dengan tombol copy"""
    if not summary_text:
        st.info("Belum ada ringkasan yang dibuat.")
        return

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
        {summary_text}
        </div>
    """, unsafe_allow_html=True)

    # Tombol copy
    st.download_button(
        label="📋 Copy Ringkasan",
        data=summary_text,
        file_name="ringkasan.txt",
        mime="text/plain"
    )
