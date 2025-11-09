import os
import io
import json
import random
import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Any

import pandas as pd
from PIL import Image
import pytesseract
import pdfplumber
import docx

# ===============================
# 📦 Database & Usage Tracking
# ===============================

DB_PATH = "data/litearn_progress.db"

def init_db(db_path: str = DB_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cur = conn.cursor()

    # Tabel untuk menyimpan progres ringkasan atau latihan pengguna
    cur.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        id TEXT PRIMARY KEY,
        username TEXT,
        type TEXT,
        timestamp TEXT,
        data TEXT
    )
    """)

    # Tabel untuk melacak batas pemakaian per user
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        count INTEGER,
        last_updated TEXT
    )
    """)
    conn.commit()
    return conn


def get_usage_count(conn, username: str) -> int:
    cur = conn.cursor()
    cur.execute("SELECT count FROM usage WHERE username = ?", (username,))
    row = cur.fetchone()
    if row:
        return int(row[0])
    else:
        cur.execute("INSERT INTO usage (username, count, last_updated) VALUES (?, ?, ?)",
                    (username, 0, datetime.utcnow().isoformat()))
        conn.commit()
        return 0


def increment_usage(conn, username: str, step: int = 1):
    cur = conn.cursor()
    cur.execute("SELECT count FROM usage WHERE username = ?", (username,))
    row = cur.fetchone()
    if row:
        newc = int(row[0]) + step
        cur.execute("UPDATE usage SET count = ?, last_updated = ? WHERE username = ?",
                    (newc, datetime.utcnow().isoformat(), username))
    else:
        cur.execute("INSERT INTO usage (username, count, last_updated) VALUES (?, ?, ?)",
                    (username, step, datetime.utcnow().isoformat()))
    conn.commit()


def check_usage_limit(conn, username: str, limit: int = 5) -> bool:
    return get_usage_count(conn, username) < limit


# ===============================
# 💾 Progress Saving & Loading
# ===============================

def save_progress(conn, username: str, typ: str, data: dict):
    cur = conn.cursor()
    rowid = str(uuid.uuid4())
    cur.execute("INSERT INTO progress (id, username, type, timestamp, data) VALUES (?, ?, ?, ?, ?)",
                (rowid, username, typ, datetime.utcnow().isoformat(), json.dumps(data)))
    conn.commit()


def load_progress_df(conn, username: str) -> pd.DataFrame:
    cur = conn.cursor()
    cur.execute("SELECT id, username, type, timestamp, data FROM progress WHERE username = ?", (username,))
    rows = cur.fetchall()
    out = []
    for r in rows:
        id, user, typ, ts, data = r
        try:
            data_json = json.loads(data)
        except:
            data_json = {}
        out.append({"id": id, "username": user, "type": typ, "timestamp": ts, "data": data_json})
    return pd.DataFrame(out) if out else pd.DataFrame(columns=["id", "username", "type", "timestamp", "data"])


# ===============================
# 📄 File Reading & OCR
# ===============================

def read_file_content(uploaded_file):
    file_type = uploaded_file.type
    text = ""

    if file_type == "text/plain":
        text = uploaded_file.read().decode("utf-8", errors="ignore")

    elif file_type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"

    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        text = "\n".join([p.text for p in doc.paragraphs])

    return text.strip()


def extract_text_from_image(image_file):
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)
    return text.strip()


# ===============================
# 🧠 Summarization
# ===============================

_SUMMARIZER = None
try:
    from transformers import pipeline
    _SUMMARIZER = pipeline("summarization", model="facebook/bart-large-cnn")
except Exception:
    _SUMMARIZER = None


def summarize_text(text: str, mode: str = "Poin singkat (bullet)", num_sentences: int = 5) -> str:
    text = (text or "").strip()
    if not text:
        return "Teks kosong."

    if _SUMMARIZER is not None:
        chunk = text[:3000]
        try:
            out = _SUMMARIZER(chunk, max_length=min(200, num_sentences * 30), min_length=30, do_sample=False)
            summary = out[0]['summary_text']
            sents = [s.strip() for s in summary.replace("\n", " ").split(". ") if s.strip()]
            bullets = ["• " + (s if s.endswith(".") else s + ".") for s in sents][:num_sentences]
            return "\n".join(bullets)
        except Exception:
            pass

    # Fallback ringkasan sederhana
    sents = [s.strip() for s in text.replace("\n", " ").split(". ") if s.strip()]
    picks = sents[:num_sentences]
    bullets = ["• " + (p if p.endswith(".") else p + ".") for p in picks]
    return "\n".join(bullets)


# ===============================
# 📝 Quiz Generator (Cloze Style)
# ===============================

def generate_quiz_from_text(text: str, n_questions: int = 5, difficulty: str = "Mudah") -> List[Dict[str, Any]]:
    text = (text or "").strip()
    sents = [s.strip() for s in text.replace("\n", " ").split(". ") if len(s.strip()) > 30]
    if not sents:
        return [{
            "question": "Tidak ada teks cukup panjang untuk membuat soal.",
            "choices": ["OK"],
            "answer": "OK"
        }]

    keywords = []
    for s in sents:
        words = [w.strip('.,()[]:;') for w in s.split() if len(w.strip('.,()[]:;')) > 6]
        if words:
            keywords.append((s, random.choice(words)))

    if not keywords:
        for s in sents:
            parts = s.split()
            if len(parts) > 3:
                keywords.append((s, parts[3]))

    random.shuffle(keywords)
    quiz = []
    for sent, kw in keywords[:n_questions]:
        q_text = sent.replace(kw, "_____")
        correct = kw
        pool = [k for _, k in keywords if k != correct]
        random.shuffle(pool)
        distractors = pool[:3]
        while len(distractors) < 3:
            distractors.append(correct[::-1][:6])
        choices = [correct] + distractors
        random.shuffle(choices)
        quiz.append({"question": q_text, "choices": choices, "answer": correct})
    return quiz
