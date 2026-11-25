import random
import sqlite3
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "my_english_progress.db"

DECK = [
    ("I", "я", "pronoun"), ("You", "ты / вы", "pronoun"),
    ("He", "он", "pronoun"), ("She", "она", "pronoun"),
    ("We", "мы", "pronoun"), ("They", "они", "pronoun"),
    ("Be", "быть", "verb"), ("Have", "иметь", "verb"),
    ("Do", "делать", "verb"), ("Go", "идти / ехать", "verb"),
    ("Work", "работать", "verb"), ("Live", "жить", "verb"),
    ("Learn", "учить / изучать", "verb"), ("Speak", "говорить", "verb"),
    ("Eat", "есть / кушать", "verb"), ("Drink", "пить", "verb"),
    ("House", "дом", "noun"), ("Work / Job", "работа / должность", "noun"),
    ("Time", "время", "noun"), ("Day", "день", "noun"),
]

st.set_page_config(page_title="MY ENGLISH — Метод Холмата", page_icon="📘", layout="wide")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS word_progress (
                english TEXT PRIMARY KEY,
                correct INTEGER NOT NULL DEFAULT 0,
                wrong INTEGER NOT NULL DEFAULT 0,
                last_result TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS test_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                english TEXT NOT NULL,
                direction TEXT NOT NULL,
                user_answer TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

def save_answer(word, direction, answer, correct):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO word_progress (english, correct, wrong, last_result)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(english) DO UPDATE SET
              correct = correct + excluded.correct,
              wrong = wrong + excluded.wrong,
              last_result = excluded.last_result
        """, (word[0], int(correct), int(not correct), "correct" if correct else "wrong"))
        conn.execute("""
            INSERT INTO test_history (english, direction, user_answer, is_correct)
            VALUES (?, ?, ?, ?)
        """, (word[0], direction, answer, int(correct)))

def get_stats():
    with sqlite3.connect(DB_PATH) as conn:
        totals = conn.execute(
            "SELECT COALESCE(SUM(correct),0), COALESCE(SUM(wrong),0) FROM word_progress"
        ).fetchone()
        weak = conn.execute(
            "SELECT english, wrong, correct FROM word_progress WHERE wrong > 0 ORDER BY wrong DESC LIMIT 8"
        ).fetchall()
    return totals, weak

init_db()
if "card_index" not in st.session_state:
    st.session_state.card_index = 0
if "card_revealed" not in st.session_state:
    st.session_state.card_revealed = False
if "test_word" not in st.session_state:
    st.session_state.test_word = None
if "test_feedback" not in st.session_state:
    st.session_state.test_feedback = None

st.title("📘 MY ENGLISH")
st.caption("Метод Холмата · Английский для реальной жизни и работы")
st.info("Учимся последовательно: карточки → письменная проверка слов → грамматика → разговорная практика.")

section = st.sidebar.radio(
    "Разделы",
    ["Главная", "Карточки слов", "Проверка слов", "Грамматика", "Разговорная практика", "Мой прогресс"],
)

if section == "Главная":
    st.subheader("Твой учебный маршрут")
    cols = st.columns(4)
    for col, number, name in zip(
        cols, ["01", "02", "03", "04"],
        ["Карточки слов", "Письменная проверка", "Грамматика", "Разговоры"],
    ):
        with col:
            st.metric(name, number)
    st.markdown("### Первый урок · Базовый словарь A1")
    st.write("20 базовых слов и выражений. Сначала изучи их на карточках, затем проверь себя в обоих направлениях.")
    st.button("Перейти к карточкам", on_click=lambda: st.session_state.update({"_section_hint": "Карточки слов"}))
    st.caption("Подсказка: выбери нужный раздел в меню слева.")

elif section == "Карточки слов":
    st.subheader("Карточки слов · Урок 1")
    direction = st.radio("Направление", ["Английский → русский", "Русский → английский"], horizontal=True)
    word = DECK[st.session_state.card_index]
    front, back = (word[0], word[1]) if direction == "Английский → русский" else (word[1], word[0])
    st.markdown(
        f"""
        <div style="border:1px solid #8885;border-radius:18px;padding:42px 18px;text-align:center;margin:18px 0;">
          <div style="font-size:14px;opacity:.7;">СЛОВО {st.session_state.card_index + 1} ИЗ {len(DECK)}</div>
          <div style="font-size:38px;font-weight:650;margin:22px 0;">{front}</div>
          <div style="font-size:22px;min-height:32px;">{back if st.session_state.card_revealed else "Нажми «Показать перевод»"}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Показать перевод", use_container_width=True):
            st.session_state.card_revealed = True
    with c2:
        if st.button("← Назад", use_container_width=True):
            st.session_state.card_index = (st.session_state.card_index - 1) % len(DECK)
            st.session_state.card_revealed = False
            st.rerun()
    with c3:
        if st.button("Далее →", use_container_width=True):
            st.session_state.card_index = (st.session_state.card_index + 1) % len(DECK)
            st.session_state.card_revealed = False
            st.rerun()

elif section == "Проверка слов":
    st.subheader("Письменная проверка словаря")
    direction = st.radio("Направление проверки", ["Русский → английский", "Английский → русский"], horizontal=True)
    if st.session_state.test_word is None:
        st.session_state.test_word = random.choice(DECK)
    word = st.session_state.test_word
    prompt, expected = (word[1], word[0]) if direction == "Русский → английский" else (word[0], word[1])
    st.markdown(f"### Переведи: **{prompt}**")
    answer = st.text_input("Твой ответ", key=f"answer_{word[0]}_{direction}")
    if st.button("Проверить ответ", type="primary"):
        normalized = answer.strip().casefold()
        accepted = {expected.casefold()}
        if "/" in expected:
            accepted.update(part.strip().casefold() for part in expected.split("/"))
        is_correct = normalized in accepted
        save_answer(word, direction, answer.strip(), is_correct)
        st.session_state.test_feedback = (is_correct, expected)
    if st.session_state.test_feedback:
        ok, expected_answer = st.session_state.test_feedback
        if ok:
            st.success("Верно! Отличная работа.")
        else:
            st.error(f"Пока неверно. Правильный ответ: {expected_answer}")
        if st.button("Следующее слово"):
            st.session_state.test_word = random.choice(DECK)
            st.session_state.test_feedback = None
            st.rerun()

elif section == "Грамматика":
    st.subheader("Грамматика")
    st.write("Этот раздел будет открываться после изучения и проверки слов урока.")
    st.info("Следующий этап разработки: объяснения грамматики на русском, структура предложения, примеры с переводом и упражнения.")

elif section == "Разговорная практика":
    st.subheader("Разговорная практика")
    st.write("Здесь появятся реальные ролевые диалоги: работа, магазин, транспорт, жильё, врач и повседневное общение.")
    st.info("Подключение Gemini для диалогов и проверки свободных ответов будет добавлено отдельным этапом.")

elif section == "Мой прогресс":
    st.subheader("Мой прогресс")
    totals, weak = get_stats()
    a, b = st.columns(2)
    a.metric("Правильных ответов", totals[0])
    b.metric("Ошибок", totals[1])
    st.markdown("### Слова для повторения")
    if weak:
        for english, wrong, correct in weak:
            st.write(f"**{english}** — ошибок: {wrong}, верных ответов: {correct}")
    else:
        st.write("Пока нет ошибок. После письменных проверок здесь появятся слова, которые стоит повторить.")

st.divider()
st.caption("MY ENGLISH — Метод Холмата · Первая рабочая основа приложения")
