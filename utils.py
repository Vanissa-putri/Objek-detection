import docx
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import io
import re

# ======== Membaca isi file teks / pdf / docx ======== #
def read_file_content(uploaded_file):
    """Membaca isi file berdasarkan jenisnya"""
    file_type = uploaded_file.type

    if file_type == "text/plain":
        return uploaded_file.read().decode("utf-8")

    elif file_type == "application/pdf":
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text

    elif file_type in [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"
    ]:
        doc = docx.Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])

    else:
        return "⚠️ Format file tidak didukung."


# ======== Ekstraksi teks dari gambar ======== #
def extract_text_from_image(uploaded_image):
    """Mengubah gambar menjadi teks menggunakan OCR"""
    try:
        image = Image.open(uploaded_image)
        text = pytesseract.image_to_string(image, lang="ind+eng")
        return text.strip()
    except Exception as e:
        return f"⚠️ Gagal membaca teks dari gambar: {str(e)}"


# ======== Fungsi ringkasan teks sederhana ======== #
def summarize_text(text, max_sentences=5):
    """Meringkas teks menjadi beberapa kalimat penting"""
    if not text or len(text.split()) < 30:
        return "Teks terlalu pendek untuk diringkas."

    # Hilangkan karakter aneh & split jadi kalimat
    text = re.sub(r'\s+', ' ', text)
    sentences = re.split(r'(?<=[.!?]) +', text)

    # Hitung frekuensi kata (sederhana)
    words = re.findall(r'\w+', text.lower())
    freq = {}
    for word in words:
        if word not in freq:
            freq[word] = 1
        else:
            freq[word] += 1

    # Skor tiap kalimat berdasar kata penting
    sentence_scores = {}
    for sentence in sentences:
        for word in sentence.lower().split():
            if word in freq:
                sentence_scores[sentence] = sentence_scores.get(sentence, 0) + freq[word]

    # Ambil kalimat dengan skor tertinggi
    ranked_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
    summary = " ".join(ranked_sentences[:max_sentences])

    return summary.strip()
