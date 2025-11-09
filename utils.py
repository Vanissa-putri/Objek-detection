import pytesseract
from PIL import Image
import docx
import pandas as pd
import PyPDF2

# ============ EKSTRAKSI TEKS ============ #
def read_file_content(file):
    """
    Membaca teks dari file: .txt, .pdf, .docx, .csv, .xlsx
    """
    if file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    
    elif file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    
    elif file.name.endswith(".csv"):
        df = pd.read_csv(file)
        return df.to_string(index=False)
    
    elif file.name.endswith(".xlsx"):
        df = pd.read_excel(file)
        return df.to_string(index=False)
    
    else:
        return ""

def extract_text_from_image(file):
    """
    Mengekstrak teks dari gambar menggunakan pytesseract
    """
    img = Image.open(file)
    text = pytesseract.image_to_string(img, lang='eng+ind')
    return text

# ============ RINGKASAN TEKS ============ #
def summarize_text(text):
    """
    Membagi teks panjang menjadi beberapa chunk agar model summarizer
    bisa merangkum semua paragraf tanpa kehilangan info.
    """
    from transformers import pipeline

    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    # Split teks menjadi paragraf
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    
    summaries = []
    for para in paragraphs:
        try:
            summary_chunk = summarizer(para, max_length=250, min_length=50, do_sample=False)[0]['summary_text']
            summaries.append(summary_chunk)
        except Exception as e:
            summaries.append(para)  # fallback kalau error

    # Gabungkan semua ringkasan chunk
    final_summary = "\n".join(summaries)
    return final_summary

# ============ GENERATE QUIZ ============ #
def generate_quiz_from_text(text, num_questions=5):
    """
    Membuat pertanyaan pilihan ganda sederhana dari teks.
    Implementasi dasar: memecah kalimat & mengambil kata penting.
    """
    import random
    import re

    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
    questions = []

    for _ in range(min(num_questions, len(sentences))):
        sentence = random.choice(sentences)
        words = sentence.split()
        if len(words) < 4:
            continue
        answer_word = random.choice(words)
        question_text = sentence.replace(answer_word, "_____")
        options = [answer_word]
        # Buat 3 opsi palsu
        for _ in range(3):
            fake_word = random.choice(words)
            if fake_word != answer_word:
                options.append(fake_word)
        random.shuffle(options)
        questions.append({
            "question": question_text,
            "options": options,
            "answer": answer_word
        })
    return questions
