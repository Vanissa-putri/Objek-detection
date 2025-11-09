import docx
import pandas as pd
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import io

# ============ BACA FILE TEKS / DOKUMEN ============ #
def read_file_content(uploaded_file):
    """Baca isi file dari berbagai format (.txt, .pdf, .docx, .csv, .xlsx)"""
    file_type = uploaded_file.name.split(".")[-1].lower()

    if file_type == "txt":
        return uploaded_file.read().decode("utf-8", errors="ignore")

    elif file_type == "pdf":
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    elif file_type == "docx":
        doc = docx.Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])

    elif file_type in ["csv", "xlsx"]:
        try:
            df = pd.read_csv(uploaded_file) if file_type == "csv" else pd.read_excel(uploaded_file)
            return df.to_string(index=False)
        except Exception:
            return "Gagal membaca file CSV/XLSX."

    else:
        return "Format file tidak didukung."


# ============ RINGKAS TEKS ============ #
def summarize_text(text):
    """Meringkas teks sederhana tanpa API berbayar"""
    sentences = text.split(".")
    if len(sentences) < 3:
        return text
    # Ambil kalimat penting (1/3 teratas)
    n = max(3, len(sentences) // 3)
    summary = ". ".join(sentences[:n])
    return summary.strip() + "..."


# ============ EKSTRAK TEKS DARI GAMBAR ============ #
def extract_text_from_image(image_file):
    """Mengubah gambar menjadi teks menggunakan OCR"""
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image, lang="eng+ind")
    return text


# ============ LATIHAN SOAL ============ #
def parse_questions_from_text(text):
    """
    Membaca soal dari teks biasa.
    Format contoh:
    1. Ibu kota Indonesia adalah...
    a. Surabaya
    b. Jakarta
    c. Medan
    d. Bandung
    Jawaban: b
    """
    questions = []
    blocks = text.strip().split("\n\n")
    for block in blocks:
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if len(lines) >= 6:
            question = lines[0]
            options = lines[1:5]
            answer_line = [l for l in lines if l.lower().startswith("jawaban")]
            correct = answer_line[0].split(":")[-1].strip().lower() if answer_line else None
            questions.append({"soal": question, "opsi": options, "jawaban": correct})
    return questions


def parse_questions_from_file(uploaded_file):
    """
    Baca soal dari file (txt, pdf, docx, csv, xlsx)
    Harus ada kolom: 'Soal', 'A', 'B', 'C', 'D', 'Jawaban'
    """
    file_type = uploaded_file.name.split(".")[-1].lower()

    try:
        if file_type == "txt":
            text = uploaded_file.read().decode("utf-8", errors="ignore")
            return parse_questions_from_text(text)

        elif file_type == "pdf":
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return parse_questions_from_text(text)

        elif file_type == "docx":
            doc = docx.Document(uploaded_file)
            text = "\n".join([p.text for p in doc.paragraphs])
            return parse_questions_from_text(text)

        elif file_type in ["csv", "xlsx"]:
            df = pd.read_csv(uploaded_file) if file_type == "csv" else pd.read_excel(uploaded_file)
            df.columns = [c.strip().lower() for c in df.columns]
            questions = []
            for _, row in df.iterrows():
                opsi = [row.get("a", ""), row.get("b", ""), row.get("c", ""), row.get("d", "")]
                questions.append({
                    "soal": str(row.get("soal", "")),
                    "opsi": opsi,
                    "jawaban": str(row.get("jawaban", "")).strip().lower()
                })
            return questions

        else:
            return []

    except Exception as e:
        print("Error parsing questions:", e)
        return []
