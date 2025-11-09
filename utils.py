import os
import io
from typing import Union
from PIL import Image
import pytesseract

# File parsers
from docx import Document
from PyPDF2 import PdfReader

# Summarizer
try:
    from transformers import pipeline
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
except Exception:
    summarizer = None


# ============ FILE READER ============ #
def read_file_content(file) -> str:
    """Baca teks dari file txt, pdf, docx."""
    filename = file.name.lower()

    try:
        if filename.endswith(".txt"):
            return file.read().decode("utf-8")

        elif filename.endswith(".pdf"):
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text

        elif filename.endswith(".docx"):
            doc = Document(file)
            return "\n".join([p.text for p in doc.paragraphs])

        else:
            return ""
    except Exception as e:
        return f"Gagal membaca file: {e}"


# ============ IMAGE OCR ============ #
def extract_text_from_image(image_file) -> str:
    """Ekstrak teks dari file gambar menggunakan OCR."""
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image, lang="eng+ind")
        return text.strip()
    except Exception as e:
        return f"Gagal mengenali teks dari gambar: {e}"


# ============ SUMMARIZATION ============ #
def summarize_text(text: str, num_sentences: int = 5) -> str:
    """Ringkas teks menggunakan model AI (transformers) jika tersedia."""
    text = (text or "").strip()

    if not text:
        return "Teks kosong atau tidak terbaca."

    # Gunakan model AI jika tersedia
    if summarizer:
        try:
            result = summarizer(text[:3000], max_length=180, min_length=50, do_sample=False)
            summary = result[0]["summary_text"].strip()
            return format_bullets(summary)
        except Exception:
            pass

    # Fallback metode sederhana
    sentences = [s.strip() for s in text.split(".") if len(s.split()) > 3]
    bullets = ["• " + s.capitalize() + "." for s in sentences[:num_sentences]]
    return "\n".join(bullets) if bullets else "Tidak cukup teks untuk diringkas."


# ============ HELPER ============ #
def format_bullets(summary: str) -> str:
    """Ubah paragraf ringkasan jadi poin-poin bullet."""
    sentences = [s.strip() for s in summary.replace("\n", " ").split(". ") if s.strip()]
    bullets = ["• " + s.capitalize() + "." for s in sentences]
    return "\n".join(bullets)
