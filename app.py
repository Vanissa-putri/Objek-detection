import streamlit as st
from utils import (
    read_file_content,
    summarize_text,
    extract_text_from_image,
    generate_quiz_from_text  # ✅ fungsi baru untuk latihan soal
)
import base64
import os
import random

# ============ CONFIG ============ #
st.set_page_config(page_title="Litearn - AI Edu App", page_icon="📚", layout="wide")

# ============ BACKGROUND SETUP ============ #
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

        /* ======= TEXT COLOR ======= */
        h1, h2, h3, h4, h5, h6, p, label, span {{
            color: white !important;
        }}

        /* ======= LINK STYLE ======= */
        a {{
            color: #00BFFF !important;
            font-weight: bold;
            text-decoration: none;
        }}
        a:hover {{
            color: #1E90FF !important;
            text-decoration: underline;
        }}

        /* ======= SIDEBAR ======= */
        [data-testid="stSidebar"] {{
            background-color: rgba(0, 0, 0, 0.45);
            color: white;
        }}
        [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {{
            color: white !important;
        }}

        /* ======= INPUT AREA ======= */
        textarea, input, .stTextArea textarea {{
            color: black !important;
            background-color: #ffffffcc !important;
        }}

        /* ======= FLOATING WHATSAPP BUTTON ======= */
        .whatsapp-float {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            z-index: 100;
        }}
        .whatsapp-float img {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.3);
        }}
        </style>
        """
        st.markdown(page_bg, unsafe_allow_html=True)

set_bg_image("assets/bg-litearn.jpg")

# ============ HEADER ============ #
col1, col2 = st.columns([1, 4])
with col1:
    st.image("assets/logo.png", width=100, use_container_width=False)
with col2:
    st.markdown("<h1 style='color:white; margin-top:25px;'>LITEARN - Smart Learning Assistant</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white;'>Membantu mahasiswa memahami materi kuliah dengan cepat dan efisien 💡</h3>", unsafe_allow_html=True)

# ============ SIDEBAR MENU ============ #
menu = st.sidebar.radio("Navigasi", ["Ringkasan Materi", "Latihan Soal", "Cara Penggunaan", "Bantuan", "Kontak Kami", "Tentang"])

# ============ MAIN CONTENT ============ #
if menu == "Ringkasan Materi":
    st.header("📚 Ringkasan Materi")
    st.markdown("<p>Unggah atau tempel materi kuliah lalu klik <b>Buat Ringkasan</b>.</p>", unsafe_allow_html=True)

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

elif menu == "Latihan Soal":
    st.header("🧠 Latihan Soal dari Materi")
    st.markdown("<p>Unggah atau tempel teks materi untuk menghasilkan latihan soal otomatis.</p>", unsafe_allow_html=True)

    quiz_source = st.radio("Sumber materi", ["Tempel teks", "Upload file (.txt, .pdf, .docx, .jpg, .png)"])
    quiz_text = ""

    if quiz_source == "Tempel teks":
        quiz_text = st.text_area("Tempel materi di sini", height=250)
    else:
        uploaded_file = st.file_uploader("Upload file", type=["txt", "pdf", "docx", "jpg", "png"])
        if uploaded_file:
            if uploaded_file.type.startswith("image/"):
                st.info("📷 File terdeteksi sebagai gambar. Mengonversi teks dari gambar...")
                quiz_text = extract_text_from_image(uploaded_file)
            else:
                quiz_text = read_file_content(uploaded_file)

    if quiz_text.strip():
        if st.button("🎯 Buat Soal"):
            st.success("✅ Soal berhasil dibuat!")
            questions = generate_quiz_from_text(quiz_text)
            score = 0
            user_answers = []

            for i, q in enumerate(questions):
                st.markdown(f"**{i+1}. {q['question']}**")
                answer = st.radio("Pilih jawaban:", q["options"], key=i)
                user_answers.append((answer, q["answer"]))
                st.write("---")

            if st.button("📊 Lihat Hasil"):
                correct = 0
                for idx, (ans, correct_ans) in enumerate(user_answers):
                    if ans == correct_ans:
                        correct += 1
                        st.success(f"Soal {idx+1}: Benar ✅")
                    else:
                        st.error(f"Soal {idx+1}: Salah ❌ (Jawaban benar: {correct_ans})")

                score = int((correct / len(user_answers)) * 100)
                st.markdown(f"### 🎓 Skor Akhir Kamu: **{score} / 100**")

elif menu == "Cara Penggunaan":
    st.header("📘 Cara Penggunaan Litearn")
    st.markdown("""
    1️⃣ Pilih menu **Ringkasan Materi** untuk mengunggah file atau menempelkan teks.  
    2️⃣ Klik menu **Latihan Soal** untuk membuat kuis dari materi tersebut.  
    3️⃣ Litearn akan otomatis menampilkan skor dan pembahasan soal.
    """)

elif menu == "Bantuan":
    st.header("🆘 Bantuan")
    st.markdown("""
    **Pertanyaan umum:**
    - File tidak terbaca? Pastikan formatnya `.txt`, `.pdf`, `.docx`, `.jpg`, atau `.png`.  
    - Hasil ringkasan kosong? Periksa apakah teks dalam file bisa disalin.  
    - Masalah lain? Hubungi kami di menu [**Kontak Kami**](#kontak-kami).
    """, unsafe_allow_html=True)

elif menu == "Kontak Kami":
    st.header("📞 Hubungi Kami")
    st.markdown("""
    📧 **Email:** <a href="mailto:litearn_ai@gmail.com">litearn_ai@gmail.com</a>  
    🌐 **Website:** <a href="https://litearn.streamlit.app" target="_blank">https://litearn.streamlit.app</a>  
    💬 **Instagram:** <a href="https://instagram.com/litearn.ai" target="_blank">@litearn.ai</a>
    """, unsafe_allow_html=True)

elif menu == "Tentang":
    st.header("ℹ️ Tentang LITEARN")
    st.markdown("""
    **Litearn** adalah aplikasi edukasi berbasis **AI**  
    yang membantu mahasiswa memahami materi kuliah dengan cepat.  
    Litearn dapat membaca dan meringkas teks dari dokumen maupun gambar  
    menjadi **poin-poin penting yang mudah dipahami**, serta membuat latihan soal otomatis.  
    """)
    st.success("Dari ringkasan jadi pemahaman. 🚀")

# ============ FLOATING WHATSAPP BUTTON ============ #
st.markdown("""
<div class="whatsapp-float">
    <a href="https://wa.me/6281234567890" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg">
    </a>
</div>
""", unsafe_allow_html=True)
