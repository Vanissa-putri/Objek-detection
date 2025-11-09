import os
import json
import sqlite3
from typing import List, Dict, Any
from datetime import datetime

# -------------------------
# DB & usage tracking
# -------------------------
DB_PATH = "litearn_progress.db"

def init_db(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        id TEXT PRIMARY KEY,
        username TEXT,
        type TEXT,
        timestamp TEXT,
        data TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        count INTEGER,
        last_updated TEXT
    )
    """)
    conn.commit()
    # ensure usage row exists per username is created on demand
    return conn

def get_usage_count(conn, username: str) -> int:
    cur = conn.cursor()
    cur.execute("SELECT count FROM usage WHERE username = ?", (username,))
    row = cur.fetchone()
    if row:
        return int(row[0])
    else:
        # create initial row with 0
        cur.execute("INSERT INTO usage (username, count, last_updated) VALUES (?, ?, ?)",
                    (username, 0, datetime.utcnow().isoformat()))
        conn.commit()
        return 0

def increment_usage(conn, username: str, step:int=1):
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

# -------------------------
# progress saving / loading
# -------------------------
import uuid
def save_progress(conn, username: str, typ: str, data: dict):
    cur = conn.cursor()
    rowid = str(uuid.uuid4())
    cur.execute("INSERT INTO progress (id, username, type, timestamp, data) VALUES (?, ?, ?, ?, ?)",
                (rowid, username, typ, datetime.utcnow().isoformat(), json.dumps(data)))
    conn.commit()

import pandas as pd
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
    if out:
        return pd.DataFrame(out)
    else:
        return pd.DataFrame(columns=["id","username","type","timestamp","data"])

# -------------------------
# Summarization & Quiz (fallback pipelines)
# -------------------------
# Try to load transformers summarizer if available, otherwise fallback simple method
_SUMMARIZER = None
try:
    from transformers import pipeline
    _SUMMARIZER = pipeline("summarization", model="facebook/bart-large-cnn")
except Exception:
    _SUMMARIZER = None

def summarize_text(text: str, mode: str="Poin singkat (bullet)", num_sentences:int=5) -> str:
    text = (text or "").strip()
    if not text:
        return "Teks kosong."
    # Prefer transformers if available
    if _SUMMARIZER is not None:
        chunk = text[:3000]
        try:
            out = _SUMMARIZER(chunk, max_length=min(200, num_sentences*30), min_length=30, do_sample=False)
            summary = out[0]['summary_text']
            # format bullets
            sents = [s.strip() for s in summary.replace("\n", " ").split(". ") if s.strip()]
            bullets = ["• " + (s if s.endswith(".") else s + ".") for s in sents][:num_sentences]
            return "\n".join(bullets)
        except Exception:
            pass
    # fallback naive extraction: pick first N sentences
    sents = [s.strip() for s in text.replace("\n", " ").split(". ") if s.strip()]
    picks = sents[:num_sentences]
    bullets = ["• " + (p if p.endswith(".") else p + ".") for p in picks]
    return "\n".join(bullets)

# Simple quiz generation based on cloze of longer words
import random
def generate_quiz_from_text(text: str, n_questions:int=5, difficulty:str="Mudah") -> List[Dict[str,Any]]:
    text = (text or "").strip()
    sents = [s.strip() for s in text.replace("\n", " ").split(". ") if len(s.strip())>30]
    if not sents:
        # fallback dummy question
        return [{"question": "Tidak ada teks cukup panjang untuk membuat soal. Coba tempelkan teks", "choices": ["OK"], "answer": "OK"}]
    keywords = []
    for s in sents:
        words = [w.strip('.,()[]:;') for w in s.split() if len(w.strip('.,()[]:;'))>6]
        if words:
            keywords.append((s, random.choice(words)))
    if not keywords:
        # use shorter words
        for s in sents:
            parts = s.split()
            if len(parts) > 3:
                keywords.append((s, parts[3]))
    random.shuffle(keywords)
    quiz = []
    for sent, kw in keywords[:n_questions]:
        q_text = sent.replace(kw, "_____")
        correct = kw
        pool = [k for _,k in keywords if k != correct]
        random.shuffle(pool)
        distractors = pool[:3]
        # ensure 4 choices
        while len(distractors) < 3:
            distractors.append(correct[::-1][:6])
        choices = [correct] + distractors
        random.shuffle(choices)
        quiz.append({"question": q_text, "choices": choices, "answer": correct})
    return quiz
