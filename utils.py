import docx
import pandas as pd
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import io
import random

# --- Membaca berbagai jenis file ---
def read_file_content(uploaded_file):
    file_type = uploaded_file.name.split('.')[-1].lower()

    if file_type == "txt":
        return uploaded_file.read().decode("utf-8")

    elif file_type == "pdf":
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    elif file_type == "docx":
        doc = docx.Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])

    elif file_type == "csv":
        df = pd.read_csv(uploaded_file)
        return df.to_string()

    elif file_type in ["xls", "xlsx"]:
        df = pd.read_excel(uploaded_file)
        return df.to_string()

    else:
        return "❌ Format tidak didukung."

# --- Ekstraksi teks dari gambar ---
def extract_text_from_image(uploaded_image):
    image = Image.open(uploaded_image)
    return pytesseract.image_to_string(image)

# --- Ringkas teks sederhana ---
def summarize_text(text):
    sentences = text.split(".")
    if len(sentences) <= 3:
        return text
    summary = ". ".join(sentences[:3]) + "."
    return summary + "\n\n✨ Untuk ringkasan lebih detail, hubungi kami untuk fitur Premium."

# --- Buat soal sederhana ---
def generate_quiz_from_text(text):
    sentences = [s.strip() for s in text.split(".") if len(s.split()) > 4]
    if not sentences:
        return [{"question": "Tidak cukup teks untuk membuat soal.", "options": ["-"], "answer": "-"}]

    questions = []
    for s in random.sample(sentences[:min(len(sentences), 5)], min(5, len(sentences))):
        words = s.split()
        if len(words) < 5:
            continue
        missing = random.choice(words[1:-1])
        question = s.replace(missing, "_____", 1)
        options = random.sample(words, min(4, len(words)))
        if missing not in options:
            options[random.randint(0, len(options)-1)] = missing
        questions.append({"question": question, "options": options, "answer": missing})
    return questions
