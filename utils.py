import docx
import PyPDF2
import pandas as pd
import pytesseract
from PIL import Image
import io
import re
from transformers import pipeline

# ====== SUMMARIZATION MODEL (HUGGINGFACE PIPELINE) ====== #
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

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

    elif file_type in ["text/csv", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
        df = pd.read_csv(uploaded_file) if file_type == "text/csv" else pd.read_excel(uploaded_file)
        return df.to_string(index=False)

    else:
        return "Format file tidak didukung."

def extract_text_from_image(image_file):
    """Ekstrak teks dari file gambar"""
    img = Image.open(image_file)
    text = pytesseract.image_to_string(img, lang="ind")
    return text.strip()

def split_into_chunks(text, max_tokens=1000):
    """Pisahkan teks panjang jadi beberapa potongan agar bisa diproses model"""
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks, chunk = [], ""

    for sentence in sentences:
        if len(chunk) + len(sentence) < max_tokens:
            chunk += " " + sentence
        else:
            chunks.append(chunk.strip())
            chunk = sentence
    if chunk:
        chunks.append(chunk.strip())
    return chunks

def summarize_text(text):
    """Buat ringkasan teks menjadi beberapa paragraf"""
    if len(text.split()) < 50:
        return "Teks terlalu pendek untuk diringkas."

    chunks = split_into_chunks(text, max_tokens=1000)
    summaries = []

    for chunk in chunks:
        result = summarizer(chunk, max_length=200, min_length=60, do_sample=False)
        summaries.append(result[0]['summary_text'])

    # Gabungkan semua ringkasan
    final_summary = "\n\n".join(summaries)
    return final_summary.strip()

def generate_quiz_from_text(text):
    """Buat latihan soal sederhana dari teks"""
    sentences = re.split(r'(?<=[.!?]) +', text)
    selected = [s for s in sentences if len(s.split()) > 6][:5]
    questions = []

    for s in selected:
        words = s.split()
        if len(words) > 5:
            missing_word = words[len(words)//2]
            question_text = s.replace(missing_word, "_____")
            options = [missing_word] + [w for w in words[:5] if w != missing_word][:3]
            questions.append({
                "question": question_text,
                "options": sorted(list(set(options))),
                "answer": missing_word
            })

    return questions
