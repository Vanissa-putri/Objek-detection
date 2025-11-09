import streamlit as st
from utils import (
    read_file_content,
    summarize_text,
    extract_text_from_image,
    check_usage_limit,
    increment_usage_count
)
import base64
import os

# ============ CONFIG ============ #
st.set_page_config(page_title="Litearn - AI Edu App", page_icon="📚", layout="wide")

# Background image setup
def set_bg_image(image_file):
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
menu = st.sidebar.radio("Navigasi", ["Beranda", "Cara Penggunaan", "Bantuan", "Kontak Kami", "Tentang"])

if menu == "Beranda":
    st.header("📄 Upload Materi Kuliah")
    st.write("Unggah file (.txt, .pdf, .docx, .jpg, .png) untuk diringkas menjadi poin-poin penting.")

    uploaded_file = st.file_uploader("Upload file", type=["txt", "pdf", "docx", "jpg", "png"])

    if uploaded_file:
        if not check_usage_limit():
            st.error("❌ Batas 5 kali penggunaan gratis sudah tercapai. Silakan upgrade ke versi premium untuk melanjutkan.")
        else:
            if uploaded_file.type.startswith("image/"):
                st.info("📷 File terdeteksi sebagai gambar. Mengonversi teks dari gambar...")
                text = extract_text_from_image(uploaded_file)
            else:
                text = read_file_content(uploaded_file)

            if text.strip() == "":
                st.warning("Tidak ditemukan teks dalam file ini.")
            else:
                st.success("✅ File berhasil dibaca!")
                if st.button("🔍 Ringkas Teks"):
                    increment_usage_count()
                    summary = summarize_text(text)
                    st.subheader("🧾 Hasil Ringkasan:")
                    st.write(summary)

elif menu == "Cara Penggunaan":
    st.header("📘 Cara Penggunaan Litearn")
    st.markdown("""
    1️⃣ Pilih menu **Beranda** untuk mengunggah file dokumen atau gambar.  
    2️⃣ Litearn akan otomatis membaca isi dokumen.  
    3️⃣ Klik tombol **Ringkas Teks** untuk mendapatkan ringkasan poin penting.  
    4️⃣ Setiap pengguna mendapat 5 kali penggunaan gratis.  
    5️⃣ Jika ingin tanpa batas, upgrade ke versi premium.
    """)

elif menu == "Bantuan":
    st.header("🆘 Bantuan")
    st.markdown("""
    **Pertanyaan umum:**
    - File tidak terbaca? Pastikan formatnya `.txt`, `.pdf`, `.docx`, `.jpg`, atau `.png`.  
    - Hasil ringkasan kosong? Periksa apakah teks dalam file bisa disalin.  
    - Masalah teknis lain? Hubungi kami di menu **Kontak Kami**.
    """)

elif menu == "Kontak Kami":
    st.header("📞 Hubungi Kami")
    st.markdown("""
    Butuh bantuan atau ingin kerja sama?  
    📧 **Email:** litearn_ai@gmail.com  
    🌐 **Website:** [https://litearn.streamlit.app](https://litearn.streamlit.app)  
    💬 **Instagram:** [@litearn.ai](https://instagram.com/litearn.ai)
    """)

elif menu == "Tentang":
    st.header("ℹ️ Tentang LITEARN")
    st.markdown("""
    **Litearn** adalah aplikasi edukasi berbasis **kecerdasan buatan (AI)**  
    yang membantu mahasiswa memahami materi kuliah dengan cepat dan efisien.  
    Litearn dapat merangkum buku, artikel, maupun gambar berisi teks menjadi  
    **poin-poin penting yang mudah dipahami** serta menyediakan latihan adaptif  
    sesuai kemampuan pengguna.  
    """)

    st.success("Dapat diakses melalui perangkat mobile dan web dengan tampilan sederhana.")
