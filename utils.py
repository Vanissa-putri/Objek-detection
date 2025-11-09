import docx
import PyPDF2
import pandas as pd
import pytesseract
from PIL import Image
import re
import random
from transformers import pipeline

# ====== SUMMARIZATION MODEL (LEBIH RINGAN & CEPAT) ====== #
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
def split_into_chunks(text, max_words=800):
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
    """Ringkas teks menjadi 1 paragraf panjang, lebih lengkap"""
    if len(text.split()) < 20:
        return text.strip()  # teks sangat pendek → kembalikan apa adanya

    chunks = split_into_chunks(text, max_words=800)
    summaries = []

    for chunk in chunks:
        # max_length lebih besar agar ringkasan panjang, min_length untuk ringkasan lengkap
        result = summarizer(chunk, max_length=400, min_length=100, do_sample=False)
        summaries.append(result[0]['summary_text'])

    # Gabungkan semua chunk menjadi 1 paragraf panjang
    final_summary = " ".join(summaries)
    final_summary = re.sub(r'\s+', ' ', final_summary).strip()  # hapus spasi ganda / line break
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
        options = list({missing_word} | set(words[:5]))[:4]  # maksimal 4 opsi unik
        questions.append({
            "question": question_text,
            "options": options,
            "answer": missing_word
        })

    return questions
