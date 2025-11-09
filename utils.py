import docx
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import io
import re

# ======== Fungsi untuk membaca file ======== #
def read_file_content(uploaded_file):
    """
    Membaca isi dari file txt, pdf, atau docx.
    Mengembalikan teks dalam bentuk string.
    """
    text = ""
    filename = uploaded_file.name.lower()

    # File TXT
    if filename.endswith(".txt"):
        text = uploaded_file.read().decode("utf-8", errors="ignore")

    # File PDF
    elif filename.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # File DOCX
    elif filename.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs])

    else:
        text = "Format file tidak didukung. Harap upload .txt, .pdf, atau .docx"

    return clean_text(text)


# ======== Fungsi untuk membersihkan teks ======== #
def clean_text(text):
    """
    Membersihkan teks dari karakter aneh atau berulang.
    """
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\x0c', '').strip()
    return text


# ======== Fungsi ringkasan sederhana ======== #
def summarize_text(text, max_sentences=5):
    """
    Meringkas teks sederhana berdasarkan kalimat penting (tanpa AI model eksternal).
    """
    if not text or len(text.split()) < 30:
        return "Teks terlalu pendek untuk diringkas."

    sentences = re.split(r'(?<=[.!?]) +', text)
    scored = {}

    # Hitung frekuensi kata
    words = re.findall(r'\w+', text.lower())
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1

    # Skor tiap kalimat
    for sent in sentences:
        sent_score = sum(freq.get(w.lower(), 0) for w in re.findall(r'\w+', sent))
        scored[sent] = sent_score

    # Ambil kalimat terbaik
    ranked = sorted(scored, key=scored.get, reverse=True)
    summary = " ".join(ranked[:max_sentences])
    return summary.strip()


# ======== Fungsi ekstraksi teks dari gambar ======== #
def extract_text_from_image(uploaded_image):
    """
    Mengambil teks dari gambar menggunakan OCR (pytesseract).
    """
    try:
        image = Image.open(uploaded_image)
        text = pytesseract.image_to_string(image, lang='eng+ind')
        return clean_text(text) if text.strip() else "Tidak ada teks yang terdeteksi pada gambar."
    except Exception as e:
        return f"Gagal membaca teks dari gambar: {str(e)}"
