import streamlit as st
from utils import (
    read_file_content,
    summarize_text,
    extract_text_from_image,
    generate_quiz_from_text
)
import base64
import os

# ============ CONFIG ============ #
st.set_page_config(page_title="Litearn - AI Edu App", page_icon="📚", layout="wide")

# ============ BACKGROUND ============ #
def set_bg_image(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as file:
            data = base64.b64encode(file.read()).decode()
        st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{data}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        /* Teks default putih agar terbaca di background gelap */
        h1, h2, h3, h4, h5, h6, p, label, span {{
            color: white !important;
        }}
        /* Sidebar semi-transparan */
        [data-testid="stSidebar"] {{
            background-color: rgba(0, 0, 0, 0.5);
        }}
        /* Kotak input teks */
        textarea, input {{
            color: black !important;
            background-color: #ffffffcc !important;
        }}
        /* Kotak ringkasan / quiz khusus */
        .summary-box {{
            background-color: #ffffffcc;
            color: black;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(0,0,0,0.1);
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            white-space: pre-wrap;
        }}
        a.contact-link {{
            color: white !important;
            text-decoration: none;
            font-weight: bold;
        }}
        a.contact-link:hover {{
            color: #00BFFF !important;
            text-decoration: underline;
        }}
        </style>
        """, unsafe_allow_html=True)

set_bg_image("assets/bg-litearn.jpg")

# ============ HEADER ============ #
col1, col2 = st.columns([1, 4])
with col1:
    st.image("assets/logo.png", width=100)
with col2:
    st.markdown("<h1 style='margin-top:25px;'>LITEARN - Smart Learning Assistant</h1>", unsafe_allow_html=True)
st.markdown("<h3>Membantu mahasiswa memahami materi kuliah dengan cepat dan efisien 💡</h3>", unsafe_allow_html=True)

# ============ MENU ============ #
menu = st.sidebar.radio(
    "Navigasi", 
    [
        "Ringkasan Materi",
        "Latihan Soal",
        "Cara Penggunaan",
        "Bantuan",
        "Pengaduan",
        "Kontak Kami",
        "Tentang"
    ]
)

# ============ RINGKASAN ============ #
if menu == "Ringkasan Materi":
    st.header("📚 Ringkasan Materi")
    st.markdown("<p>Unggah atau tempel materi kuliah lalu klik <b>Buat Ringkasan</b>.</p>", unsafe_allow_html=True)

    source = st.radio("Sumber materi", ["Tempel teks", "Upload file (.txt, .pdf, .docx, .csv, .xlsx, .jpg, .png)"])
    text = ""

    if source == "Tempel teks":
        text = st.text_area("Tempel teks / artikel / bab buku di sini", height=250)
    else:
        uploaded_file = st.file_uploader("Upload file", type=["txt", "pdf", "docx", "csv", "xlsx", "jpg", "png"])
        if uploaded_file:
            if uploaded_file.type.startswith("image/"):
                st.info("📷 File gambar terdeteksi, sedang mengekstrak teks...")
                text = extract_text_from_image(uploaded_file)
            else:
                text = read_file_content(uploaded_file)

    if text.strip():
        if st.button("🔍 Buat Ringkasan"):
            summary = summarize_text(text)
            st.subheader("🧾 Hasil Ringkasan:")
            st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
            st.info("✨ Ingin hasil ringkasan lebih akurat dan detail? Hubungi kami untuk fitur Premium!")
    else:
        st.info("Masukkan teks atau upload file terlebih dahulu.")

# ============ LATIHAN SOAL ============ #
elif menu == "Latihan Soal":
    st.header("🧠 Latihan Soal Otomatis")
    st.markdown("<p>Litearn akan membuat soal dari materi yang kamu upload atau tempelkan.</p>", unsafe_allow_html=True)

    quiz_source = st.radio("Sumber materi", ["Tempel teks", "Upload file (.txt, .pdf, .docx, .csv, .xlsx, .jpg, .png)"])
    quiz_text = ""

    if quiz_source == "Tempel teks":
        quiz_text = st.text_area("Tempel materi di sini", height=250)
    else:
        uploaded_file = st.file_uploader("Upload file", type=["txt", "pdf", "docx", "csv", "xlsx", "jpg", "png"])
        if uploaded_file:
            if uploaded_file.type.startswith("image/"):
                st.info("📷 Mengekstrak teks dari gambar...")
                quiz_text = extract_text_from_image(uploaded_file)
            else:
                quiz_text = read_file_content(uploaded_file)

    if quiz_text.strip():
        if st.button("🎯 Buat Soal"):
            st.success("✅ Soal berhasil dibuat!")
            questions = generate_quiz_from_text(quiz_text)
            answers = []
            for i, q in enumerate(questions):
                st.markdown(f"**{i+1}. {q['question']}**")
                choice = st.radio("Jawaban kamu:", q["options"], key=f"q{i}")
                answers.append((choice, q["answer"]))
                st.write("---")

            if st.button("📊 Lihat Nilai"):
                correct = sum(1 for a, b in answers if a == b)
                score = int((correct / len(answers)) * 100)
                for idx, (a, b) in enumerate(answers):
                    if a == b:
                        st.success(f"Soal {idx+1}: Benar ✅")
                    else:
                        st.error(f"Soal {idx+1}: Salah ❌ (Jawaban benar: {b})")
                st.markdown(f"### 🎓 Skor Akhir: **{score} / 100**")
    else:
        st.info("Masukkan teks atau upload file terlebih dahulu.")

# ============ CARA PENGGUNAAN ============ #
elif menu == "Cara Penggunaan":
    st.header("📘 Cara Penggunaan Litearn")
    st.markdown("""
    1️⃣ Pilih menu **Ringkasan Materi** untuk membuat ringkasan dari file atau teks.  
    2️⃣ Gunakan **Latihan Soal** untuk menghasilkan pertanyaan otomatis.  
    3️⃣ Lihat hasil dan skor kamu langsung di layar.  
    """)

# ============ BANTUAN ============ #
elif menu == "Bantuan":
    st.header("🆘 Bantuan")
    st.markdown("""
    **Pertanyaan umum:**
    - File tidak terbaca? Pastikan formatnya `.txt`, `.pdf`, `.docx`, `.csv`, `.xlsx`, `.jpg`, atau `.png`.  
    - Hasil ringkasan kosong? Pastikan teks dalam file bisa disalin.  
    - Untuk hasil lebih bagus, gunakan versi **Premium** (hubungi kami).
    """)

# ============ PENGADUAN ============ #
elif menu == "Pengaduan":
    st.header("📩 Pengaduan & Masukan Pengguna")
    st.markdown("""
    Jika kamu mengalami kendala, bug, atau ingin memberi saran pengembangan aplikasi,
    silakan isi formulir di bawah ini.  
    Tim Litearn akan membaca setiap pesan yang masuk 💬
    """)

    nama = st.text_input("Nama Lengkap")
    email = st.text_input("Email Aktif")
    subjek = st.text_input("Subjek Pesan")
    pesan = st.text_area("Isi Pesan atau Keluhan", height=150)

    if st.button("Kirim Pesan"):
        if nama and email and pesan:
            st.success("✅ Pesan berhasil dikirim! Terima kasih atas masukannya 🙌")
        else:
            st.warning("⚠️ Mohon isi semua kolom sebelum mengirim pesan.")

# ============ KONTAK ============ #
elif menu == "Kontak Kami":
    st.header("📞 Hubungi Kami")
    st.markdown("""
    📧 **Email:** <a class="contact-link" href="mailto:litearn_ai@gmail.com">litearn_ai@gmail.com</a>  
    💬 **WhatsApp:** <a class="contact-link" href="https://wa.me/6282283292897" target="_blank">Chat Kami</a>  
    🌐 **Website:** <a class="contact-link" href="https://litearn.streamlit.app" target="_blank">litearn.streamlit.app</a>
    """, unsafe_allow_html=True)

# ============ TENTANG ============ #
elif menu == "Tentang":
    st.header("ℹ️ Tentang LITEARN")
    st.markdown("""
    Litearn adalah aplikasi edukasi berbasis **AI lokal**  
    yang membantu mahasiswa memahami materi kuliah,  
    membuat ringkasan otomatis, dan latihan soal interaktif.  
    """)
    st.success("Dari ringkasan jadi pemahaman. 🚀")
