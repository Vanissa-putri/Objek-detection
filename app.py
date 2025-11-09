import streamlit as st
from utils import (
    read_file_content,
    summarize_text,
    extract_text_from_image
)
import base64
import os

# ============ CONFIG ============ #
st.set_page_config(page_title="Litearn - AI Edu App", page_icon="📚", layout="wide")

# Background image setup
def set_bg_image(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as file:
            data = base64.b64encode(file.read()).decode()
        page_bg = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{data}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """
        st.markdown(page_bg, unsafe_allow_html=True)

set_bg_image("assets/bg-litearn.jpg")

# Header logo
st.image("assets/logo.png", width=200)
st.markdown("<h1 style='text-align:center; color:#3E64FF;'>LITEARN - Smart Learning Assistant</h1>", unsafe_allow_html=True)
st.markdown("### Membantu mahasiswa memahami materi kuliah dengan cepat dan efisien 💡")

# Sidebar menu
menu = st.sidebar.radio("Navigasi", ["Ringkasan Materi", "Cara Penggunaan", "Bantuan", "Kontak Kami", "Tentang"])

if menu == "Ringkasan Materi":
    st.header("📚 Ringkasan Materi")
    st.write("Unggah atau tempel materi kuliah lalu klik **Buat Ringkasan**.")

    source = st.radio("Sumber materi", ["Tempel teks", "Upload file (.txt, .pdf, .docx, .jpg, .png)"])

    text = ""

    if source == "Tempel teks":
        text = st.text_area("Tempel teks / artikel / bab buku di sini", height=250)
    else:
        uploaded_file = st.file_uploader("Upload file", type=["txt", "pdf", "docx", "jpg", "png"])
        if uploaded_file:
            if uploaded_file.type.startswith("image/"):
                st.info("📷 File terdeteksi sebagai gambar. Mengonversi teks dari gambar...")
                text = extract_text_from_image(uploaded_file)
            else:
                text = read_file_content(uploaded_file)

    if text.strip():
        if st.button("🔍 Buat Ringkasan"):
            summary = summarize_text(text)
            st.subheader("🧾 Hasil Ringkasan:")
            st.write(summary)
    else:
        st.info("Masukkan teks atau upload file terlebih dahulu.")

elif menu == "Cara Penggunaan":
    st.header("📘 Cara Penggunaan Litearn")
    st.markdown("""
    1️⃣ Pilih menu **Ringkasan Materi** untuk mengunggah file atau menempelkan teks.  
    2️⃣ Litearn akan otomatis membaca isi dokumen atau teks.  
    3️⃣ Klik tombol **Buat Ringkasan** untuk mendapatkan hasilnya.
    """)

elif menu == "Bantuan":
    st.header("🆘 Bantuan")
    st.markdown("""
    **Pertanyaan umum:**
    - File tidak terbaca? Pastikan formatnya `.txt`, `.pdf`, `.docx`, `.jpg`, atau `.png`.  
    - Hasil ringkasan kosong? Periksa apakah teks dalam file bisa disalin.  
    - Masalah lain? Hubungi kami di menu **Kontak Kami**.
    """)

elif menu == "Kontak Kami":
    st.header("📞 Hubungi Kami")
    st.markdown("""
    📧 **Email:** litearn_ai@gmail.com  
    🌐 **Website:** [https://litearn.streamlit.app](https://litearn.streamlit.app)  
    💬 **Instagram:** [@litearn.ai](https://instagram.com/litearn.ai)
    """)

elif menu == "Tentang":
    st.header("ℹ️ Tentang LITEARN")
    st.markdown("""
    **Litearn** adalah aplikasi edukasi berbasis **AI**  
    yang membantu mahasiswa memahami materi kuliah dengan cepat.  
    Litearn dapat membaca dan meringkas teks dari dokumen maupun gambar  
    menjadi **poin-poin penting yang mudah dipahami**.
    """)
    st.success("Dapat digunakan di perangkat mobile dan web dengan tampilan sederhana.")
