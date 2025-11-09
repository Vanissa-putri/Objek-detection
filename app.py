import streamlit as st
from utils import (
    init_db, get_usage_count, increment_usage, summarize_text,
    generate_quiz_from_text, save_progress, load_progress_df
)
from datetime import datetime

st.set_page_config(page_title="LITEARN — AI Learning Assistant", layout="wide")
conn = init_db()

# --- Sidebar: user & nav ---
st.sidebar.title("L I T E A R N")
st.sidebar.caption("AI learning assistant untuk mahasiswa")

username = st.sidebar.text_input("Nama (untuk laporan)", value="Mahasiswa")
if not username:
    st.sidebar.warning("Masukkan nama untuk menyimpan progres.")
    st.stop()

# Check premium via license code (placeholder)
st.sidebar.markdown("**Akun & Langganan**")
license_code = st.sidebar.text_input("Masukkan kode lisensi (jika ada)", type="password")
is_premium = False
if license_code.strip() == "LITEARN-PREMIUM":
    is_premium = True
    st.sidebar.success("Mode Premium aktif")
elif license_code.strip():
    st.sidebar.error("Kode lisensi tidak valid")

FREE_LIMIT = 5
usage_count = get_usage_count(conn, username)

st.sidebar.markdown(f"Pemakaian AI: **{usage_count}** / {FREE_LIMIT} (free)")
if not is_premium and usage_count >= FREE_LIMIT:
    st.sidebar.warning("Batas 5 kali gratis tercapai — upgrade untuk lanjut.")
st.sidebar.markdown("---")

# Navigation
pages = ["Ringkasan", "Latihan Soal", "Laporan", "Tentang", "Hubungi", "Bantuan", "Upgrade"]
page = st.sidebar.radio("Menu", pages)

# Helper: whether AI allowed
def ai_allowed():
    return is_premium or (usage_count < FREE_LIMIT)

# --- Page: Ringkasan ---
if page == "Ringkasan":
    st.title("Ringkasan Materi")
    st.write("Unggah atau tempel materi kuliah lalu klik **Buat Ringkasan**.")
    input_mode = st.radio("Sumber materi", ("Tempel teks", "Upload file .txt"), index=0)
    raw_text = ""
    if input_mode == "Tempel teks":
        raw_text = st.text_area("Tempel teks / artikel / bab buku di sini", height=280)
    else:
        uploaded = st.file_uploader("Upload file .txt", type=["txt"])
        if uploaded:
            raw_text = uploaded.read().decode("utf-8")

    summary_mode = st.selectbox("Mode ringkasan", ["Poin singkat (bullet)", "Ringkasan naratif"])
    num_sentences = st.slider("Jumlah poin / kalimat (perkiraan)", min_value=3, max_value=12, value=5)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Buat Ringkasan"):
            if not raw_text.strip():
                st.error("Masukkan teks dulu.")
            elif not ai_allowed():
                st.error("Batas free 5 kali tercapai. Silakan upgrade untuk melanjutkan.")
            else:
                with st.spinner("Membuat ringkasan..."):
                    summary = summarize_text(raw_text, mode=summary_mode, num_sentences=num_sentences)
                st.success("Ringkasan selesai")
                st.markdown("### Ringkasan")
                st.write(summary)
                # save progress & increment usage
                save_progress(conn, username, "summary", {"timestamp": datetime.utcnow().isoformat(), "summary": summary, "source_chars": len(raw_text)})
                increment_usage(conn, username)
                # update usage_count locally
                usage_count = get_usage_count(conn, username)
    with col2:
        st.info("Tips:\n- Gunakan teks bagian bab ~1-3 untuk hasil terbaik.\n- Jika butuh ringkasan lebih banyak, gunakan versi Premium.")

# --- Page: Latihan Soal ---
elif page == "Latihan Soal":
    st.title("Latihan Soal Adaptif")
    st.write("Buat latihan soal otomatis dari materi yang dimasukkan.")
    raw_text = st.text_area("Tempel teks / artikel (bagian penting) di sini", height=240)
    difficulty = st.selectbox("Tingkat kesulitan", ["Mudah", "Sedang", "Sulit"])
    num_questions = st.slider("Jumlah soal", min_value=1, max_value=10, value=5)

    if st.button("Buat Latihan Soal"):
        if not raw_text.strip():
            st.error("Masukkan teks dulu.")
        elif not ai_allowed():
            st.error("Batas free 5 kali tercapai. Silakan upgrade untuk melanjutkan.")
        else:
            with st.spinner("Menyusun soal..."):
                quiz = generate_quiz_from_text(raw_text, n_questions=num_questions, difficulty=difficulty)
            st.success("Latihan soal siap")
            answers = {}
            for i, q in enumerate(quiz):
                st.write(f"**Soal {i+1}.** {q['question']}")
                choice = st.radio(f"Pilih jawaban Soal {i+1}", q["choices"], key=f"q{i}")
                answers[i] = {"selected": choice, "correct": q["answer"]}
            if st.button("Koreksi Latihan"):
                score = 0
                for i, resp in answers.items():
                    if resp["selected"] == resp["correct"]:
                        score += 1
                st.write(f"Skor: **{score} / {len(answers)}**")
                save_progress(conn, username, "quiz", {"timestamp": datetime.utcnow().isoformat(), "score": score, "total": len(answers)})
                increment_usage(conn, username)
                usage_count = get_usage_count(conn, username)

# --- Page: Laporan ---
elif page == "Laporan":
    st.title("Laporan Perkembangan Belajar")
    st.write("Riwayat ringkasan dan latihan serta statistik sederhana.")
    df = load_progress_df(conn, username)
    if df.empty:
        st.info("Belum ada progres. Coba buat ringkasan atau latihan soal.")
    else:
        st.dataframe(df.sort_values("timestamp", ascending=False).reset_index(drop=True))
        quizzes = df[df['type']=="quiz"]
        if not quizzes.empty:
            avg_score = quizzes['data'].apply(lambda d: d.get('score', 0)).mean()
            st.metric("Rata-rata skor latihan", f"{avg_score:.2f}")
        summaries = df[df['type']=="summary"]
        st.write(f"Total ringkasan dibuat: **{len(summaries)}**")
        st.write(f"Total latihan dibuat: **{len(quizzes)}**")
        st.write(f"Total pemakaian AI: **{usage_count}** / {FREE_LIMIT} (free)")

# --- Page: Tentang ---
elif page == "Tentang":
    st.title("Tentang LITEARN")
    st.markdown("""
**LITEARN** adalah aplikasi edukasi berbasis kecerdasan buatan (AI) yang membantu mahasiswa memahami materi kuliah dengan cepat dan efisien.

Fitur utama:
- Merangkum buku/dokumen menjadi poin penting.
- Membuat latihan soal adaptif sesuai kemampuan.
- Laporan perkembangan belajar.
- Akses via web & mobile (Streamlit responsif).
""")
    st.markdown("**Visi:** Membantu mahasiswa belajar lebih cepat, fokus ke inti materi.\n\n**Kontak pengembang:** lihat halaman Hubungi.")

# --- Page: Hubungi ---
elif page == "Hubungi":
    st.title("Hubungi Kami")
    st.write("Kalau ada masalah, saran fitur, atau mau kerja sama, hubungi kami.")
    with st.form("contact_form"):
        name = st.text_input("Nama", value=username)
        email = st.text_input("Email")
        topic = st.selectbox("Topik", ["Masalah Teknis", "Saran Fitur", "Kerja Sama", "Lainnya"])
        message = st.text_area("Pesanmu", height=160)
        submitted = st.form_submit_button("Kirim pesan")
        if submitted:
            # Sederhana: simpan pesan ke DB sebagai 'contact'
            save_progress(conn, username, "contact", {"timestamp": datetime.utcnow().isoformat(), "name": name, "email": email, "topic": topic, "message": message})
            st.success("Pesan terkirim. Kami akan merespons via email (simulasi).")

    st.markdown("Atau email langsung ke: **support@litearn.example** (placeholder)")

# --- Page: Bantuan ---
elif page == "Bantuan":
    st.title("Bantuan / FAQ")
    st.markdown("""
**Q: Apa yang dimaksud 5 kali pemakaian gratis?**  
A: Setiap pembuatan ringkasan atau pembuatan latihan soal dihitung 1 pemakaian. Total gratis = 5.

**Q: Bagaimana cara upgrade?**  
A: Buka menu *Upgrade* dan ikuti instruksi (di versi ini: masukkan kode lisensi contoh `LITEARN-PREMIUM`).

**Q: Data disimpan di mana?**  
A: Saat ini progres disimpan lokal di database SQLite (`litearn_progress.db`). Untuk production, integrasikan penyimpanan cloud.

**Butuh bantuan lain?** Gunakan halaman Hubungi.
""")

# --- Page: Upgrade ---
elif page == "Upgrade":
    st.title("Upgrade ke LITEARN Premium")
    st.write("""
**Manfaat Premium**  
- Pemakaian AI tanpa batas (tidak ada hitungan 5 kali).  
- Ringkasan panjang dan soal lanjutan (lebih kompleks).  
- Prioritas dukungan & fitur eksport laporan.
""")
    st.markdown("**Cara uji coba (demo)**: masukkan kode `LITEARN-PREMIUM` di sidebar untuk mengaktifkan Premium.")
    st.markdown("Untuk integrasi pembayaran: sambungkan Stripe/PayPal dan berikan lisensi/flag akun setelah pembayaran.")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Litearn — prototype. Versi: 1.0")
