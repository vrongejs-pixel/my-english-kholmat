import json
import random
import re
import sqlite3
from pathlib import Path
import streamlit as st

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "my_english_progress.db"

from vocabulary_data import VOCABULARY
from life_situations_data import JOB_INTERVIEW
from grammar_course_data import ADVANCED_GRAMMAR, BASIC_GRAMMAR_DETAILS

CORE_VOCABULARY = json.loads((APP_DIR / "core_vocabulary.json").read_text(encoding="utf-8"))

BASE_WORDS = [
    (word[0], word[1], category)
    for category, words in VOCABULARY.items()
    for word in words
]

CATEGORIES = ["Существительные", "Глаголы", "Прилагательные", "Местоимения", "Наречия", "Предлоги", "Фразы", "Другое"]

GRAMMAR = [
    {"title":"To be: am / is / are", "level":"A1", "rule":"Глагол to be означает «быть». В настоящем времени выбираем форму по подлежащему: I am; he/she/it is; you/we/they are.", "examples":["I am ready. — Я готов.","She is at home. — Она дома.","They are at work. — Они на работе.","Are you tired? — Ты устал?"], "tasks":[
        ("I ___ from Uzbekistan.", ["am","is","are"], "am", "С местоимением I используется am."),
        ("He ___ my friend.", ["am","is","are"], "is", "С he / she / it используется is."),
        ("We ___ ready.", ["am","is","are"], "are", "С we используется are."),
        ("___ she at home?", ["Am","Is","Are"], "Is", "В вопросе is ставится перед she."),
        ("Выбери отрицание: «Я не занят».", ["I not busy","I am not busy","I is not busy"], "I am not busy", "Отрицание строится: am/is/are + not.")
    ]},
    {"title":"Личные местоимения", "level":"A1", "rule":"I — я, you — ты/вы, he — он, she — она, it — оно/это, we — мы, they — они. Местоимение обычно стоит перед глаголом.", "examples":["I work. — Я работаю.","He lives here. — Он живёт здесь.","They speak English. — Они говорят по-английски."], "tasks":[
        ("Как сказать «мы»?", ["we","they","you"], "we", "We означает «мы»."),
        ("___ works here. (Она)", ["He","She","They"], "She", "She означает «она»."),
        ("Как сказать «они»?", ["they","we","I"], "they", "They означает «они».")
    ]},
    {"title":"Have / has", "level":"A1", "rule":"Have / has означает «иметь». С I, you, we, they используем have; с he, she, it — has.", "examples":["I have a car. — У меня есть машина.","She has a job. — У неё есть работа.","Do you have time? — У тебя есть время?"], "tasks":[
        ("I ___ a brother.", ["have","has"], "have", "С I используем have."),
        ("She ___ a new job.", ["have","has"], "has", "С she используем has."),
        ("They ___ two children.", ["have","has"], "have", "С they используем have.")
    ]},
    {"title":"Present Simple", "level":"A1", "rule":"Present Simple используем для привычек, фактов и регулярных действий. I/you/we/they + глагол; he/she/it + глагол с -s/-es. Вопросы: do/does.", "examples":["I work every day. — Я работаю каждый день.","He works here. — Он работает здесь.","Do you speak English? — Ты говоришь по-английски?","She doesn't drive. — Она не водит машину."], "tasks":[
        ("I ___ in Tashkent.", ["live","lives"], "live", "С I глагол без окончания -s."),
        ("He ___ in a shop.", ["work","works"], "works", "С he к глаголу добавляем -s."),
        ("___ you speak English?", ["Do","Does"], "Do", "С you в вопросе используем do."),
        ("She ___ like coffee.", ["don't","doesn't"], "doesn't", "С she используем doesn't.")
    ]},
    {"title":"Present Continuous", "level":"A1", "rule":"Используем для действия, которое происходит сейчас. Формула: am/is/are + глагол-ing.", "examples":["I am working now. — Я сейчас работаю.","She is cooking. — Она готовит.","They are waiting. — Они ждут."], "tasks":[
        ("I ___ studying now.", ["am","is","are"], "am", "I + am + глагол-ing."),
        ("He is ___ dinner.", ["cook","cooking","cooks"], "cooking", "После is нужен глагол с -ing."),
        ("They ___ waiting.", ["am","is","are"], "are", "They + are.")
    ]},
    {"title":"Past Simple", "level":"A2", "rule":"Past Simple описывает завершённое действие в прошлом. У правильных глаголов обычно добавляется -ed; у неправильных форма меняется. Вопросы и отрицания: did.", "examples":["I worked yesterday. — Я работал вчера.","She went home. — Она пошла домой.","Did you call me? — Ты мне звонил?"], "tasks":[
        ("I ___ him yesterday.", ["see","saw","seen"], "saw", "Прошедшая форма see — saw."),
        ("We ___ at home last night.", ["was","were","are"], "were", "С we в прошедшем времени to be — were."),
        ("Did you ___ yesterday?", ["worked","work","working"], "work", "После did используем начальную форму глагола.")
    ]},
    {"title":"Future Simple", "level":"A2", "rule":"Future Simple: will + начальная форма глагола. Используем для будущих действий, решений и прогнозов.", "examples":["I will call you. — Я тебе позвоню.","She will come tomorrow. — Она придёт завтра.","Will you help me? — Ты мне поможешь?"], "tasks":[
        ("I ___ call you tomorrow.", ["will","am","did"], "will", "Будущее Simple строится с will."),
        ("She will ___ later.", ["comes","come","coming"], "come", "После will глагол стоит в начальной форме.")
    ]},
]

SITUATIONS = {
    "Собеседование на работу": [
        ("Tell me about yourself.", "Расскажите о себе.", "I have experience in this field.", "У меня есть опыт в этой сфере."),
        ("Why do you want this job?", "Почему вы хотите эту работу?", "I want to learn and develop.", "Я хочу учиться и развиваться."),
        ("When can you start?", "Когда вы можете начать?", "I can start next Monday.", "Я могу начать в следующий понедельник."),
        ("What experience do you have?", "Какой у вас опыт?", "I have two years of experience.", "У меня два года опыта.")
    ],
    "На работе": [
        ("What time does the shift start?", "Во сколько начинается смена?", "My shift starts at eight.", "Моя смена начинается в восемь."),
        ("Could you help me, please?", "Не могли бы вы мне помочь?", "Of course. What do you need?", "Конечно. Что вам нужно?"),
        ("I have finished this task.", "Я закончил это задание.", "Please check my work.", "Пожалуйста, проверьте мою работу.")
    ],
    "В магазине": [
        ("How much does this cost?", "Сколько это стоит?", "It costs ten pounds.", "Это стоит десять фунтов."),
        ("Do you have a smaller size?", "У вас есть размер поменьше?", "Let me check for you.", "Позвольте мне проверить."),
        ("Can I pay by card?", "Можно оплатить картой?", "Yes, you can.", "Да, можно.")
    ],
    "На улице": [
        ("Excuse me, where is the bus stop?", "Извините, где автобусная остановка?", "It is next to the bank.", "Она рядом с банком."),
        ("How can I get to the station?", "Как мне добраться до станции?", "Go straight and turn left.", "Идите прямо и поверните налево."),
        ("Is it far from here?", "Это далеко отсюда?", "No, it is five minutes away.", "Нет, это в пяти минутах отсюда.")
    ],
    "В ресторане": [
        ("Could I see the menu, please?", "Можно меню, пожалуйста?", "Of course. Here you are.", "Конечно. Вот, пожалуйста."),
        ("I would like a cup of tea.", "Я бы хотел чашку чая.", "Would you like anything else?", "Хотите что-нибудь ещё?"),
        ("Could I have the bill, please?", "Можно счёт, пожалуйста?", "Certainly.", "Конечно.")
    ],
    "В аэропорту": [
        ("Where is the check-in desk?", "Где стойка регистрации?", "It is over there.", "Она вон там."),
        ("May I see your passport?", "Можно ваш паспорт?", "Here you are.", "Вот, пожалуйста."),
        ("What time does boarding start?", "Во сколько начинается посадка?", "Boarding starts at six.", "Посадка начинается в шесть.")
    ],
    "Аренда жилья": [
        ("Is the apartment still available?", "Квартира ещё свободна?", "Yes, it is available.", "Да, она свободна."),
        ("How much is the rent?", "Сколько стоит аренда?", "The rent is five hundred a month.", "Аренда стоит пятьсот в месяц."),
        ("Are bills included?", "Коммунальные платежи включены?", "Yes, they are included.", "Да, они включены.")
    ],
    "У врача": [
        ("What seems to be the problem?", "Что вас беспокоит?", "I have a headache.", "У меня болит голова."),
        ("How long have you had this pain?", "Как давно у вас эта боль?", "For two days.", "Два дня."),
        ("Do you take any medicine?", "Вы принимаете какие-нибудь лекарства?", "No, I don't.", "Нет.")
    ],
    "В гостинице": [
        ("I have a reservation.", "У меня есть бронирование.", "What is your name, please?", "Как вас зовут, пожалуйста?"),
        ("Is breakfast included?", "Завтрак включён?", "Yes, breakfast is included.", "Да, завтрак включён."),
        ("What time is check-out?", "Во сколько выезд?", "Check-out is at eleven.", "Выезд в одиннадцать.")
    ],
    "В транспорте": [
        ("Does this bus go to the city centre?", "Этот автобус идёт в центр города?", "Yes, it does.", "Да."),
        ("Where should I get off?", "Где мне выходить?", "Get off at the next stop.", "Выходите на следующей остановке."),
        ("How much is a ticket?", "Сколько стоит билет?", "A ticket is two pounds.", "Билет стоит два фунта.")
    ]
}

st.set_page_config(page_title="MY ENGLISH — Метод Холмата", page_icon="📘", layout="wide")


st.markdown("""
<style>
:root { --brand:#2563eb; --brand-dark:#173b75; }
[data-testid="stAppViewContainer"] { background: #f4f7fc; }
[data-testid="stHeader"] { background: rgba(244,247,252,.92); }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#10294f 0%,#173b75 100%); }
[data-testid="stSidebar"] * { color: #f4f8ff !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { padding: .35rem .55rem; border-radius: .55rem; }
.block-container { max-width: 1240px; padding-top: 2rem; padding-bottom: 3rem; }
h1 { color:#15345f; letter-spacing:-.04em; font-weight:800; }
h2,h3 { color:#183b68; font-weight:750; }
div[data-testid="stMetric"] { background:#fff; border:1px solid #e4eaf3; border-radius:16px; padding:16px; box-shadow:0 3px 14px rgba(22,48,87,.05); }
.stButton > button { border-radius:11px; min-height:2.65rem; font-weight:650; border:1px solid #d8e2f0; }
.stButton > button[kind="primary"] { background:#2563eb; border-color:#2563eb; }
div[data-testid="stForm"], div[data-testid="stExpander"] { background:#fff; border:1px solid #e4eaf3; border-radius:14px; padding:12px; }
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea { border-radius:10px; }
div[data-testid="stProgress"] > div > div { background:#2563eb; }
</style>
""", unsafe_allow_html=True)


def connect():
    return sqlite3.connect(DB_PATH)

def init_db():
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS word_progress (
            english TEXT PRIMARY KEY, correct INTEGER NOT NULL DEFAULT 0,
            wrong INTEGER NOT NULL DEFAULT 0, last_result TEXT)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS custom_decks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS custom_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT, deck_id INTEGER NOT NULL,
            english TEXT NOT NULL, russian TEXT NOT NULL, category TEXT NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS custom_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT NOT NULL,
            prompt TEXT NOT NULL, answer TEXT NOT NULL, explanation TEXT DEFAULT '')""")
        conn.execute("""CREATE TABLE IF NOT EXISTS test_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, item TEXT, direction TEXT,
            user_answer TEXT, is_correct INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS custom_situations (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
            level TEXT NOT NULL, data_json TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

def save_result(item, direction, answer, correct):
    with connect() as conn:
        conn.execute("""INSERT INTO word_progress (english, correct, wrong, last_result)
            VALUES (?, ?, ?, ?) ON CONFLICT(english) DO UPDATE SET
            correct=correct+excluded.correct, wrong=wrong+excluded.wrong,
            last_result=excluded.last_result""",
            (item, int(correct), int(not correct), "correct" if correct else "wrong"))
        conn.execute("INSERT INTO test_history (item,direction,user_answer,is_correct) VALUES (?,?,?,?)",
                     (item, direction, answer, int(correct)))

def generate_custom_situation(user_request, level, focus, dialogue_turns):
    import requests
    api_key = st.secrets.get("GEMINI_API_KEY", "") or st.secrets.get("GOOGLE_API_KEY", "")
    if not api_key:
        raise RuntimeError("Не найден ключ Gemini. Добавь GEMINI_API_KEY в Streamlit Cloud → Settings → Secrets.")
    prompt = f"""
Ты — методист практического курса английского языка. Создай полноценный учебный модуль.
Запрос ученика: {user_request}
Уровень: {level}. Главный акцент: {focus}. Диалог: примерно {dialogue_turns} реплик.
Верни только корректный JSON без Markdown:
{{
"title":"название ситуации на русском",
"goal":"цель урока на русском",
"vocabulary":[{{"en":"слово или выражение","ipa":"IPA","ru":"перевод","example":"пример на английском","example_ru":"перевод примера"}}],
"dialogue":[{{"speaker":"Имя/роль","en":"реплика на английском","ru":"перевод на русский"}}],
"exercises":[{{"question":"задание на русском","answer":"ответ на английском","why":"объяснение на русском"}}],
"sentence_pairs":[{{"en":"полное английское предложение","ru":"точный русский перевод"}}]
}}
Требования: 20–25 полезных слов и выражений разных частей речи; связный естественный диалог с указанным количеством реплик; 12 разнообразных упражнений; 20 предложений для сборки. Усложняй материал постепенно. Учитывай уровень {level}. Каждый английский пример и каждая реплика должны иметь точный русский перевод. Не дублируй материалы. Не выдумывай правовые, медицинские или иные специальные факты — обучай языку на общих примерах. Никакого текста вне JSON.
"""
    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json={"contents":[{"parts":[{"text":prompt}]}],
              "generationConfig":{"temperature":0.6,"responseMimeType":"application/json"}},
        timeout=90
    )
    if response.status_code != 200:
        try:
            detail = response.json().get("error", {}).get("message", response.text[:400])
        except Exception:
            detail = response.text[:400]
        raise RuntimeError("Ошибка Gemini API: " + detail)
    try:
        data = json.loads(response.json()["candidates"][0]["content"]["parts"][0]["text"])
        for field in ("title","goal","vocabulary","dialogue","exercises","sentence_pairs"):
            if field not in data:
                raise ValueError(field)
        if not data["vocabulary"] or not data["dialogue"] or not data["sentence_pairs"]:
            raise ValueError("empty lesson section")
        return data
    except Exception as exc:
        raise RuntimeError("Gemini вернул неполный или некорректный урок. Попробуй ещё раз.") from exc

def load_custom_situations():
    with connect() as conn:
        return conn.execute("SELECT id,title,level,data_json FROM custom_situations ORDER BY id DESC").fetchall()

def get_decks():
    with connect() as conn:
        return conn.execute("SELECT id,name FROM custom_decks ORDER BY name").fetchall()

def get_words(deck_id):
    with connect() as conn:
        return conn.execute("SELECT id,english,russian,category FROM custom_words WHERE deck_id=? ORDER BY id", (deck_id,)).fetchall()

def navigate():
    st.session_state.section = st.session_state.nav_choice

init_db()
defaults = {
    "section":"Главная", "card_index":0, "card_revealed":False, "known_count":0,
    "test_word":None, "test_feedback":None, "grammar_feedback":None,
    "situation_feedback":None, "repeat_words":[]
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.title("📘 MY ENGLISH")
st.caption("Метод Холмата · Английский для жизни и работы")
sections = ["Главная","Карточки слов","Словарный каталог","Мои сборники","Проверка слов","Грамматика","Жизненные ситуации","Конструктор заданий","Мой прогресс"]
if st.session_state.section not in sections:
    st.session_state.section = "Главная"
if st.session_state.get("nav_choice") not in sections:
    st.session_state.nav_choice = st.session_state.section
st.sidebar.radio("Разделы", sections, key="nav_choice", on_change=navigate, index=sections.index(st.session_state.section))
section = st.session_state.section

if section == "Главная":
    st.subheader("Твой учебный маршрут")
    st.write("Проходи обучение по порядку: слова → письменная проверка → грамматика → практика реальных разговоров.")
    cols=st.columns(4)
    for c,t in zip(cols,["Карточки слов","Грамматика","Жизненные ситуации","Конструктор заданий"]):
        c.markdown("#### "+t)
    st.button("Начать с карточек", type="primary", on_click=lambda: setattr(st.session_state,"section","Карточки слов"))
    st.info("Твои результаты и собственные материалы будут сохраняться в базе приложения. На бесплатном Streamlit Cloud локальная база может сбрасываться при пересоздании приложения; для надёжного хранения подключим облачную базу отдельно.")

elif section == "Карточки слов":
    st.subheader("Карточки слов")
    st.caption(f"В большом каталоге {len(CORE_VOCABULARY):,} слов. Выбирай нужные группы и учи их в обоих направлениях.")
    decks=get_decks()
    labels=["Большой словарь (2 877 слов, включая слова для проверки)","Мой базовый набор (361 слово)"]+[f"Мой сборник: {name}" for _,name in decks]
    source=st.selectbox("Источник карточек",labels,key="flash_deck")

    selected_pos=[]
    selected_bands=[]
    if source.startswith("Большой словарь ("):
        all_pos=sorted({p for x in CORE_VOCABULARY for p in x["part_of_speech"]})
        all_bands=list(dict.fromkeys(x["frequency_band"] for x in CORE_VOCABULARY))
        selected_pos=st.multiselect("Группы по частям речи",all_pos,default=all_pos,key="core_pos_filter")
        selected_bands=st.multiselect("Частотные группы",all_bands,default=all_bands,key="core_band_filter")
        words=[
            (i,x["word"],x["translation"],x.get("ipa",""),x.get("example",""),x.get("example_ru",""),", ".join(x["part_of_speech"]),x.get("verb_forms",{}))
            for i,x in enumerate(CORE_VOCABULARY)
            if set(x["part_of_speech"]).intersection(selected_pos) and x["frequency_band"] in selected_bands
        ]
    elif source=="Мой базовый набор (361 слово)":
        categories=st.multiselect("Группы слов",list(VOCABULARY.keys()),default=list(VOCABULARY.keys()),key="flash_categories")
        words=[(i,*word,category) for i,(category,items) in enumerate(VOCABULARY.items()) if category in categories for word in items]
    else:
        name=source.replace("Мой сборник: ","",1)
        did=next((i for i,n in decks if n==name),None)
        words=[(row[0],row[1],row[2],"","","",row[3]) for row in (get_words(did) if did else [])]

    direction=st.radio("Лицевая сторона",["Английский → Русский","Русский → Английский","Смешанный режим"],horizontal=True,key="flash_direction")
    if not words:
        st.warning("Выбери хотя бы одну группу или добавь слова в свой сборник.")
    else:
        signature=(source,direction,tuple(selected_pos),tuple(selected_bands),tuple(st.session_state.get("flash_categories",[])))
        if st.session_state.get("flash_signature")!=signature:
            st.session_state.flash_signature=signature
            st.session_state.card_index=0
            st.session_state.card_revealed=False
            st.session_state.flash_card_signature=None
        st.session_state.card_index%=len(words)
        w=words[st.session_state.card_index]
        if st.session_state.get("flash_card_signature") != (signature,st.session_state.card_index):
            actual=random.choice(["Английский → Русский","Русский → Английский"]) if direction=="Смешанный режим" else direction
            st.session_state.flash_actual_direction=actual
            st.session_state.flash_card_signature=(signature,st.session_state.card_index)
        actual=st.session_state.flash_actual_direction
        english,russian=w[1],w[2]
        pronunciation=w[3] if len(w)>3 else ""
        example=w[4] if len(w)>4 else ""
        example_ru=w[5] if len(w)>5 else ""
        group=w[6] if len(w)>6 else "Словарь"
        front,back=(english,russian) if actual=="Английский → Русский" else (russian,english)
        st.caption(f"Направление: {actual} · Часть речи: {group}")
        st.progress((st.session_state.card_index+1)/len(words),text=f"Карточка {st.session_state.card_index+1} из {len(words)}")
        st.markdown(f"""<div style="background:linear-gradient(135deg,#ffffff 0%,#edf4ff 100%);border:1px solid #d9e5f5;border-radius:22px;padding:44px 20px;text-align:center;margin:16px 0;box-shadow:0 12px 30px rgba(26,60,110,.08)">
        <div style="font-size:12px;letter-spacing:.14em;color:#64748b;font-weight:700">MY ENGLISH · VOCABULARY</div>
        <div style="font-size:38px;color:#173b75;font-weight:800;margin:24px 0">{front}</div>
        <div style="font-size:22px;color:#2563eb;min-height:30px">{back if st.session_state.card_revealed else "Нажми «Показать ответ»"}</div>
        </div>""",unsafe_allow_html=True)
        if not st.session_state.card_revealed:
            if st.button("Показать ответ",type="primary",use_container_width=True):
                st.session_state.card_revealed=True
                st.rerun()
        else:
            if pronunciation: st.write(f"**Транскрипция / произношение:** {pronunciation}")
            verb_forms=w[7] if len(w)>7 and isinstance(w[7],dict) else {}
            if verb_forms:
                v2=", ".join(verb_forms.get("V2",[])) or "—"
                v3=", ".join(verb_forms.get("V3",[])) or "—"
                st.info(f"**Формы глагола:** V1 {verb_forms.get('V1',english)} · V2 {v2} · V3 {v3}")
            if example: st.write(f"**Пример:** {example}")
            if example_ru: st.caption(example_ru)
            a,b=st.columns(2)
            if a.button("✓ Знаю",type="primary",use_container_width=True):
                st.session_state.known_count+=1
                st.session_state.card_index=(st.session_state.card_index+1)%len(words)
                st.session_state.card_revealed=False
                st.session_state.flash_card_signature=None
                st.rerun()
            if b.button("↻ Повторить",use_container_width=True):
                st.session_state.repeat_words.append((english,russian))
                st.session_state.card_index=(st.session_state.card_index+1)%len(words)
                st.session_state.card_revealed=False
                st.session_state.flash_card_signature=None
                st.rerun()
        st.caption(f"Знаю в этой сессии: {st.session_state.known_count} · На повторение: {len(st.session_state.repeat_words)}")
        if st.session_state.repeat_words:
            with st.expander("Слова для повторения"):
                for en,ru in st.session_state.repeat_words:
                    st.write(f"**{en}** — {ru}")

elif section == "Словарный каталог":
    st.subheader("Большой словарный каталог")
    st.caption("Поиск по английскому слову и русскому переводу. Частотные группы показывают порядок изучения, а не официальный уровень CEFR.")
    search=st.text_input("Найти слово или перевод",placeholder="Например: work, работа, travel…",key="catalog_search").strip().lower()
    all_pos=sorted({part for x in CORE_VOCABULARY for part in x["part_of_speech"]})
    all_bands=list(dict.fromkeys(x["frequency_band"] for x in CORE_VOCABULARY))
    c1,c2=st.columns(2)
    with c1: pos_filter=st.multiselect("Часть речи",all_pos,default=all_pos,key="catalog_pos")
    with c2: band_filter=st.multiselect("Частотная группа",all_bands,default=all_bands,key="catalog_band")
    matches=[x for x in CORE_VOCABULARY if set(x["part_of_speech"]).intersection(pos_filter) and x["frequency_band"] in band_filter and (not search or search in x["word"].lower() or search in x["translation"].lower())]
    st.metric("Найдено слов",f"{len(matches):,}")
    st.dataframe([{"English":x["word"],"Перевод":x["translation"],"Транскрипция":x.get("ipa",""),"Часть речи":", ".join(x["part_of_speech"]),"Частотная группа":x["frequency_band"]} for x in matches[:150]],use_container_width=True,hide_index=True)
    if len(matches)>150: st.caption("Показаны первые 150 результатов. Уточни поиск или фильтры, чтобы увидеть нужные слова.")
    import csv
    import io
    buffer=io.StringIO()
    writer=csv.DictWriter(buffer,fieldnames=["English","Russian","IPA","Part of speech","Frequency group"])
    writer.writeheader()
    for x in matches:
        writer.writerow({"English":x["word"],"Russian":x["translation"],"IPA":x.get("ipa",""),"Part of speech":", ".join(x["part_of_speech"]),"Frequency group":x["frequency_band"]})
    st.download_button("Скачать выбранные слова в CSV",buffer.getvalue().encode("utf-8-sig"),file_name="my_english_vocabulary.csv",mime="text/csv",use_container_width=True)

elif section == "Мои сборники":
    st.subheader("Конструктор словарных сборников")
    with st.form("deck_create",clear_on_submit=True):
        new_name=st.text_input("Название сборника",placeholder="Например: Глаголы или Работа")
        create=st.form_submit_button("Создать сборник")
    if create and new_name.strip():
        try:
            with connect() as conn: conn.execute("INSERT INTO custom_decks(name) VALUES(?)",(new_name.strip(),))
            st.success("Сборник создан."); st.rerun()
        except sqlite3.IntegrityError: st.error("Такой сборник уже существует.")
    decks=get_decks()
    if decks:
        names={n:i for i,n in decks}
        chosen=st.selectbox("Выбери сборник",list(names))
        did=names[chosen]
        with st.form("word_add",clear_on_submit=True):
            en=st.text_input("Английское слово или выражение")
            ru=st.text_input("Перевод на русский")
            cat=st.selectbox("Категория",CATEGORIES)
            add=st.form_submit_button("Добавить слово")
        if add:
            if en.strip() and ru.strip():
                with connect() as conn: conn.execute("INSERT INTO custom_words(deck_id,english,russian,category) VALUES(?,?,?,?)",(did,en.strip(),ru.strip(),cat))
                st.success("Слово добавлено."); st.rerun()
            else: st.warning("Заполни оба поля.")
        st.markdown("#### Слова сборника")
        for wid,en,ru,cat in get_words(did):
            x,y,z=st.columns([2,2,2]); x.write("**"+en+"**"); y.write(ru); z.write(cat)
            if st.button("Удалить",key=f"delword{wid}"):
                with connect() as conn: conn.execute("DELETE FROM custom_words WHERE id=?",(wid,))
                st.rerun()
    else: st.info("Создай первый сборник выше.")

elif section == "Проверка слов":
    st.subheader("Письменная проверка слов")
    direction=st.radio("Направление",["Русский → английский","Английский → русский"],horizontal=True)
    if st.session_state.test_word is None: st.session_state.test_word=random.choice(BASE_WORDS)
    word=st.session_state.test_word
    prompt,expected=(word[1],word[0]) if direction=="Русский → английский" else (word[0],word[1])
    st.markdown(f"### Переведи: **{prompt}**")
    answer=st.text_input("Твой ответ",key=f"written_{word[0]}_{direction}")
    if st.button("Проверить ответ",type="primary") and answer.strip():
        accepted={p.strip().casefold() for p in expected.replace(" / ","/").split("/")}
        ok=answer.strip().casefold() in accepted
        save_result(word[0],direction,answer.strip(),ok)
        st.session_state.test_feedback=(ok,expected)
        st.rerun()
    if st.session_state.test_feedback:
        ok,exp=st.session_state.test_feedback
        st.success("Верно!") if ok else st.error(f"Правильный ответ: {exp}")
        if st.button("Следующее слово"):
            st.session_state.test_word=random.choice(BASE_WORDS); st.session_state.test_feedback=None; st.rerun()

elif section == "Грамматика":
    st.subheader("Курс грамматики — Метод Холмата")
    st.write("Полный маршрут от A1 до B2. Сначала изучай объяснение и примеры, затем выполняй практику. Можно выбрать уровень и конкретную тему.")
    course_level = st.selectbox("Уровень курса", ["A1–A2 · Основы", "B1–B2 · Средний и продвинутый"], key="grammar_course_level")
    if course_level.startswith("B1"):
        advanced_names = [f"{x['level']} · {x['title']}" for x in ADVANCED_GRAMMAR]
        adv_idx = st.selectbox("Тема урока", range(len(ADVANCED_GRAMMAR)), format_func=lambda i: advanced_names[i], key="grammar_advanced_lesson")
        lesson = ADVANCED_GRAMMAR[adv_idx]
        st.markdown(f"## {lesson['level']} · {lesson['title']}")
        st.markdown("### 1. Подробное объяснение правила")
        st.write(lesson["explanation"])
        st.markdown("### 2. Формула и построение")
        st.info(lesson["form"])
        st.markdown("### 3. Когда и зачем используется")
        for use in lesson["uses"]:
            st.markdown("• " + use)
        st.markdown("### 4. Разобранные примеры")
        for en, ru in lesson["examples"]:
            with st.container(border=True):
                st.markdown(f"**{en}**")
                st.write(ru)
        st.markdown("### 5. Типичные ошибки")
        for mistake in lesson["mistakes"]:
            st.warning(mistake)
        st.markdown("### 6. Тематический словарь")
        vocab = lesson["vocabulary"]
        vocab_names = [f"{en} — {ru}" for en, ru in vocab]
        vocab_idx = st.selectbox("Выбери слово или выражение", range(len(vocab)), format_func=lambda i: vocab_names[i], key=f"adv_vocab_{adv_idx}")
        st.success(f"{vocab[vocab_idx][0]} — {vocab[vocab_idx][1]}")
        st.caption(f"Слов и выражений в теме: {len(vocab)}")
        st.divider()
        st.markdown("### 7. Большая практика")
        st.caption("В этом уроке подготовлен набор заданий с ответами и объяснением. Проходи их по порядку; после каждого ответа разбирай правило.")
        tasks = lesson["tasks"]
        practice_key = f"adv_grammar_index_{adv_idx}"
        if practice_key not in st.session_state:
            st.session_state[practice_key] = 0
        task_index = st.session_state[practice_key] % len(tasks)
        question, correct_answer, explanation = tasks[task_index]
        st.progress((task_index + 1) / len(tasks), text=f"Задание {task_index + 1} из {len(tasks)}")
        st.markdown(f"**{question}**")
        answer_key = f"adv_grammar_answer_{adv_idx}_{task_index}"
        user_answer = st.text_input("Твой ответ", key=answer_key)
        if st.button("Проверить ответ", type="primary", key=f"adv_grammar_check_{adv_idx}_{task_index}"):
            normalize = lambda value: " ".join(re.findall(r"[a-z0-9']+", str(value).casefold()))
            accepted = [x.strip() for x in correct_answer.split(" / ")]
            ok = any(normalize(user_answer) == normalize(x) for x in accepted)
            st.session_state[answer_key + "_feedback"] = (ok, correct_answer, explanation)
            if user_answer.strip():
                save_result(correct_answer, "grammar_b1_b2", user_answer, ok)
        feedback = st.session_state.get(answer_key + "_feedback")
        if feedback:
            if feedback[0]:
                st.success("Правильно!")
            else:
                st.error("Правильный ответ: " + feedback[1])
            st.info(feedback[2])
            if st.button("Следующее задание →", key=f"adv_grammar_next_{adv_idx}_{task_index}"):
                st.session_state[practice_key] = (task_index + 1) % len(tasks)
                st.rerun()
        st.caption("Количество заданий указано честно: банк этой темы содержит именно столько проверяемых заданий. Новые упражнения будут добавляться отдельными наборами, без искусственного повторения одних и тех же вопросов.")
    else:
        lesson_names = [f"{x['level']} · {x['title']}" for x in GRAMMAR]
        idx = st.selectbox("Тема урока", range(len(GRAMMAR)), format_func=lambda i: lesson_names[i], key="grammar_lesson")
        lesson = GRAMMAR[idx]
        GRAMMAR_VOCAB = {
            0: [("ready","готовый","I am ready.","Я готов."),("tired","уставший","She is tired.","Она устала."),("at work","на работе","They are at work.","Они на работе."),("at home","дома","He is at home.","Он дома."),("busy","занятый","We are busy.","Мы заняты."),("happy","счастливый","You are happy.","Ты счастлив."),("from Uzbekistan","из Узбекистана","I am from Uzbekistan.","Я из Узбекистана."),("a student","студент","He is a student.","Он студент."),("a driver","водитель","She is a driver.","Она водитель."),("here","здесь","It is here.","Это здесь.")],
            1: [("I","я","I work here.","Я работаю здесь."),("you","ты / вы","You speak English.","Ты говоришь по-английски."),("he","он","He lives here.","Он живёт здесь."),("she","она","She works today.","Она сегодня работает."),("it","оно / это","It is new.","Это новое."),("we","мы","We study English.","Мы изучаем английский."),("they","они","They are ready.","Они готовы."),("my","мой","My job is good.","Моя работа хорошая."),("his","его","His car is new.","Его машина новая."),("their","их","Their house is big.","Их дом большой.")],
            2: [("a car","машина","I have a car.","У меня есть машина."),("a job","работа","She has a job.","У неё есть работа."),("a family","семья","We have a family.","У нас есть семья."),("time","время","They have time.","У них есть время."),("a phone","телефон","He has a phone.","У него есть телефон."),("a passport","паспорт","I have a passport.","У меня есть паспорт."),("a room","комната","She has a room.","У неё есть комната."),("a question","вопрос","You have a question.","У тебя есть вопрос."),("money","деньги","We have money.","У нас есть деньги."),("a brother","брат","He has a brother.","У него есть брат.")],
            3: [("work","работать","I work every day.","Я работаю каждый день."),("live","жить","She lives in Tashkent.","Она живёт в Ташкенте."),("speak","говорить","They speak English.","Они говорят по-английски."),("start","начинать","He starts at eight.","Он начинает в восемь."),("finish","заканчивать","We finish at six.","Мы заканчиваем в шесть."),("need","нуждаться","I need help.","Мне нужна помощь."),("like","нравиться","She likes tea.","Ей нравится чай."),("go","ходить / ехать","They go to work.","Они ходят на работу."),("drive","водить","He drives a car.","Он водит машину."),("study","учиться","You study English.","Ты изучаешь английский.")],
            4: [("working","работающий сейчас","I am working now.","Я сейчас работаю."),("cooking","готовящий","She is cooking dinner.","Она готовит ужин."),("waiting","ожидающий","They are waiting.","Они ждут."),("studying","изучающий","We are studying English.","Мы изучаем английский."),("driving","ведущий машину","He is driving.","Он ведёт машину."),("reading","читающий","I am reading a book.","Я читаю книгу."),("sleeping","спящий","The child is sleeping.","Ребёнок спит."),("talking","разговаривающий","You are talking.","Ты разговариваешь."),("cleaning","убирающий","She is cleaning the room.","Она убирает комнату."),("coming","приходящий","They are coming.","Они идут сюда.")],
            5: [("yesterday","вчера","I worked yesterday.","Я работал вчера."),("last week","на прошлой неделе","We travelled last week.","Мы путешествовали на прошлой неделе."),("went","ходил / поехал","She went home.","Она пошла домой."),("saw","увидел","He saw his friend.","Он увидел своего друга."),("bought","купил","I bought a phone.","Я купил телефон."),("came","пришёл","They came early.","Они пришли рано."),("called","позвонил","You called me.","Ты мне позвонил."),("worked","работал","He worked on Monday.","Он работал в понедельник."),("had","имел / был","We had time.","У нас было время."),("did","сделал","She did the work.","Она выполнила работу.")],
            6: [("tomorrow","завтра","I will work tomorrow.","Я буду работать завтра."),("next week","на следующей неделе","We will travel next week.","Мы поедем на следующей неделе."),("call","звонить","She will call you.","Она тебе позвонит."),("help","помогать","I will help you.","Я помогу тебе."),("come","приходить","He will come later.","Он придёт позже."),("start","начинать","They will start soon.","Они скоро начнут."),("finish","заканчивать","We will finish tomorrow.","Мы закончим завтра."),("learn","учить","You will learn English.","Ты выучишь английский."),("buy","покупать","I will buy a ticket.","Я куплю билет."),("meet","встречать","She will meet us.","Она встретит нас.")]
        }
        words = GRAMMAR_VOCAB[idx]
        st.markdown("### 1. Тематический словарь")
        st.caption(f"Слова и выражения для этой темы: {len(words)}.")
        for en, ru, example, example_ru in words:
            with st.expander(en):
                st.write(f"**Перевод:** {ru}")
                st.write(f"**Пример:** {example}")
                st.caption(example_ru)
        st.markdown("### 2. Подробное объяснение правила")
        detail = BASIC_GRAMMAR_DETAILS[idx]
        st.write(detail["explanation"])
        st.markdown("### 3. Примеры с переводом")
        for en, ru in detail["examples"]:
            with st.container(border=True):
                st.markdown(f"**{en}**")
                st.write(ru)
        st.markdown("### 4. Типичные ошибки")
        for mistake in detail["mistakes"]:
            st.warning(mistake)
        st.markdown("### 3. Практика")
        st.caption("В базовом блоке доступны тренировочные задания. Число карточек не следует путать с числом уникальных примеров: часть начальных заданий использует повторяемые грамматические шаблоны.")
        base_tasks = [{"q": q, "opts": opts, "answer": correct, "why": why} for q, opts, correct, why in lesson["tasks"]]
        practice_types = ["Выбор формы", "Перевод на английский", "Перевод на русский", "Составление предложения", "Исправление ошибки", "Вопросительная форма", "Отрицательная форма", "Смешанная тренировка"]
        chosen_type = st.selectbox("Тип упражнения", practice_types, key=f"grammar_type_{idx}")
        st.markdown("#### Практика: " + chosen_type)
        run_key = f"basic_grammar:{idx}:{chosen_type}"
        if run_key not in st.session_state:
            st.session_state[run_key] = 0
        number = st.session_state[run_key] % len(base_tasks)
        task = base_tasks[number]
        st.caption(f"Задание {number + 1} из {len(base_tasks)} в выбранном наборе")
        st.markdown(f"**{task['q']}**")
        selected = st.radio("Выбери ответ", task["opts"], key=f"basic_grammar_answer_{idx}_{chosen_type}_{number}")
        if st.button("Проверить ответ", type="primary", key=f"basic_grammar_check_{idx}_{chosen_type}_{number}"):
            ok = selected.strip().casefold() == task["answer"].casefold()
            st.session_state[f"basic_grammar_feedback_{idx}_{chosen_type}_{number}"] = (ok, task["answer"], task["why"])
            save_result(task["answer"], "grammar_a1_a2", selected, ok)
        feedback = st.session_state.get(f"basic_grammar_feedback_{idx}_{chosen_type}_{number}")
        if feedback:
            if feedback[0]:
                st.success("Правильно!")
            else:
                st.error("Правильный ответ: " + feedback[1])
            st.info(feedback[2])
            if st.button("Следующее задание →", key=f"basic_grammar_next_{idx}_{chosen_type}_{number}"):
                st.session_state[run_key] += 1
                st.rerun()

    st.divider()
elif section == "Жизненные ситуации":
    st.subheader("Жизненные ситуации — практический английский")
    st.caption("Изучай готовые жизненные ситуации или создавай собственные уроки с Gemini.")
    with st.expander("＋ Создать свою ситуацию с Gemini", expanded=True):
        with st.form("custom_situation_generator"):
            scenario_request = st.text_area("Опиши ситуацию, которую хочешь изучить", placeholder="Например: Первый день на складе в Германии: знакомство с начальником, рабочий график, перерыв, правила и вопросы коллегам.", height=110)
            col_a, col_b, col_c = st.columns(3)
            scenario_level = col_a.selectbox("Уровень", ["A1","A2","B1","B2"], index=1)
            scenario_focus = col_b.selectbox("Главный акцент", ["Слова и выражения","Диалог и разговор","Грамматика в контексте","Всё вместе"], index=3)
            dialogue_turns = col_c.selectbox("Реплик в диалоге", [12,16,20,24,30], index=2)
            create_situation = st.form_submit_button("Создать учебную ситуацию", type="primary")
    if create_situation:
        if not scenario_request.strip():
            st.warning("Сначала опиши ситуацию.")
        else:
            with st.spinner("Gemini создаёт учебный материал..."):
                try:
                    lesson_data = generate_custom_situation(scenario_request.strip(), scenario_level, scenario_focus, dialogue_turns)
                    with connect() as conn:
                        conn.execute("INSERT INTO custom_situations(title,level,data_json) VALUES(?,?,?)",
                                     (lesson_data["title"], scenario_level, json.dumps(lesson_data, ensure_ascii=False)))
                    st.success("Ситуация создана и сохранена в твоих уроках.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
    saved_situations = load_custom_situations()
    if saved_situations:
        st.markdown("### Мои созданные ситуации")
        selected_id = st.selectbox("Выбери созданный урок", [row[0] for row in saved_situations],
            format_func=lambda value: next(f"{row[1]} · {row[2]}" for row in saved_situations if row[0] == value),
            key="my_custom_situation")
        selected_row = next(row for row in saved_situations if row[0] == selected_id)
        custom_lesson = json.loads(selected_row[3])
        st.markdown(f"#### {custom_lesson['title']}")
        st.caption(f"Уровень {selected_row[2]} · {custom_lesson.get('goal','')}")
        custom_tabs = st.tabs(["Словарь","Диалог","Упражнения","Сборка предложений"])
        with custom_tabs[0]:
            vocabulary = custom_lesson["vocabulary"]
            vocab_key = f"custom_vocab_index_{selected_id}"
            if vocab_key not in st.session_state:
                st.session_state[vocab_key] = 0
            vocab_index = st.session_state[vocab_key] % len(vocabulary)
            word = vocabulary[vocab_index]
            st.caption(f"Слово {vocab_index+1} из {len(vocabulary)}")
            st.markdown(f"### {word['en']}")
            st.caption(word.get("ipa",""))
            st.write(word["ru"])
            st.info(f"{word['example']} — {word['example_ru']}")
            if st.button("Следующее слово →", key=f"custom_vocab_next_{selected_id}"):
                st.session_state[vocab_key] = vocab_index + 1
                st.rerun()
        with custom_tabs[1]:
            for line in custom_lesson["dialogue"]:
                with st.container(border=True):
                    st.caption(line.get("speaker","Собеседник"))
                    st.markdown(f"**{line['en']}**")
                    st.write(line["ru"])
        with custom_tabs[2]:
            exercises = custom_lesson["exercises"]
            ex_key = f"custom_ex_index_{selected_id}"
            if ex_key not in st.session_state:
                st.session_state[ex_key] = 0
            ex_index = st.session_state[ex_key] % len(exercises)
            exercise = exercises[ex_index]
            st.caption(f"Задание {ex_index+1} из {len(exercises)}")
            st.write(exercise["question"])
            answer_key = f"custom_ex_answer_{selected_id}_{ex_index}"
            answer = st.text_input("Твой ответ на английском", key=answer_key)
            if st.button("Проверить", key=f"custom_ex_check_{selected_id}_{ex_index}"):
                normalize = lambda value: " ".join(re.findall(r"[a-z0-9']+", str(value).casefold()))
                ok = bool(answer.strip()) and normalize(answer) == normalize(exercise["answer"])
                st.session_state[answer_key+"_result"] = (ok, exercise["answer"], exercise["why"])
                if answer.strip():
                    save_result(exercise["answer"], "custom_situation", answer, ok)
            result = st.session_state.get(answer_key+"_result")
            if result:
                if result[0]: st.success("Правильно!")
                else: st.error("Правильный ответ: " + result[1])
                st.caption(result[2])
            if st.button("Следующее упражнение →", key=f"custom_ex_next_{selected_id}"):
                st.session_state[ex_key] = ex_index + 1
                st.rerun()
        with custom_tabs[3]:
            pairs = custom_lesson["sentence_pairs"]
            sentence_key = f"custom_sentence_index_{selected_id}"
            if sentence_key not in st.session_state:
                st.session_state[sentence_key] = 0
            sentence_index = st.session_state[sentence_key] % len(pairs)
            pair = pairs[sentence_index]
            tokens = re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)?|[0-9]+|[^\\w\\s]", pair["en"])
            order_key = f"custom_sentence_order_{selected_id}"
            picked_key = f"custom_sentence_picked_{selected_id}"
            if order_key not in st.session_state or st.session_state.get(order_key+"_source") != pair["en"]:
                order = list(range(len(tokens)))
                random.shuffle(order)
                st.session_state[order_key] = order
                st.session_state[picked_key] = []
                st.session_state[order_key+"_source"] = pair["en"]
                st.session_state.pop(order_key+"_result", None)
            st.markdown(f"### {pair['ru']}")
            st.caption(f"Предложение {sentence_index+1} из {len(pairs)}")
            picked = st.session_state[picked_key]
            st.write("Твоя сборка: " + " ".join(tokens[i] for i in picked))
            word_cols = st.columns(4)
            for wi, token_id in enumerate(st.session_state[order_key]):
                if token_id not in picked and word_cols[wi % 4].button(tokens[token_id], key=f"{picked_key}_{token_id}"):
                    st.session_state[picked_key].append(token_id)
                    st.rerun()
            left, middle, right = st.columns(3)
            if left.button("Отменить", key=picked_key+"_undo", disabled=not picked):
                st.session_state[picked_key] = picked[:-1]
                st.rerun()
            if middle.button("Проверить", key=picked_key+"_check", type="primary"):
                assembled = " ".join(tokens[i] for i in picked)
                normalize = lambda value: " ".join(re.findall(r"[a-z0-9']+", value.casefold()))
                st.session_state[order_key+"_result"] = (normalize(assembled) == normalize(pair["en"]), pair["en"])
            if right.button("Следующее →", key=picked_key+"_next"):
                st.session_state[sentence_key] = sentence_index + 1
                st.session_state.pop(order_key, None)
                st.session_state.pop(picked_key, None)
                st.session_state.pop(order_key+"_result", None)
                st.rerun()
            result = st.session_state.get(order_key+"_result")
            if result:
                if result[0]: st.success("Верно!")
                else: st.error("Правильный вариант: " + result[1])
    st.markdown("### Готовая программа ситуаций")
    domains = {
        "Работа в Европе": ["Собеседование на работу"],
        "Повседневная жизнь": ["В магазине", "На улице", "В транспорте", "В ресторане"],
        "Жильё и услуги": ["Аренда жилья"],
        "Здоровье": ["У врача"],
        "Путешествия": ["В аэропорту", "В гостинице"]
    }
    domain = st.selectbox("Сфера жизни", list(domains.keys()))
    if domain == "Работа в Европе":
        module = JOB_INTERVIEW
        lesson_titles = [x["title"] for x in module["lessons"]]
        lesson_index = st.selectbox("Ситуация", range(len(lesson_titles)), format_func=lambda i: lesson_titles[i], key="life_job_lesson")
        lesson = module["lessons"][lesson_index]
        st.markdown(f"### {module['title']} · {lesson['title']}")
        st.caption(f"Уровень: {module['level']}")
        st.info("Цель общения: " + lesson["goal"])

        tabs = st.tabs(["Словарь и произношение", "Карточки", "Русский → английский", "Грамматика", "Упражнения", "Диалог", "Разговорная практика", "Сборка предложений"])
        with tabs[0]:
            st.markdown("#### Словарь ситуации")
            st.write("Сначала изучи слова. Нажми 🔊, чтобы услышать произношение.")
            for wi, word in enumerate(lesson["vocabulary"]):
                en, ipa, ru, example, example_ru = word
                c1, c2, c3 = st.columns([2, 1.4, 1])
                c1.markdown(f"**{en}**")
                c1.caption(f"{example} — {example_ru}")
                c2.write(ipa)
                c2.write(ru)
                if c3.button("🔊 Слушать", key=f"life_tts_{lesson_index}_{wi}"):
                    import streamlit.components.v1 as components
                    safe_word = json.dumps(en)
                    components.html(f"""<script>
                    const u = new SpeechSynthesisUtterance({safe_word});
                    u.lang = 'en-GB'; u.rate = 0.82;
                    window.speechSynthesis.cancel(); window.speechSynthesis.speak(u);
                    </script>""", height=0)
            st.caption("Озвучка использует голос браузера. Голосовой ввод и оценка произношения будут добавлены отдельным этапом после проверки совместимости.")
        with tabs[1]:
            st.markdown("#### Карточки для запоминания")
            card_key = f"life_card_{lesson_index}"
            if card_key not in st.session_state:
                st.session_state[card_key] = 0
            ci = st.session_state[card_key] % len(lesson["vocabulary"])
            en, ipa, ru, example, example_ru = lesson["vocabulary"][ci]
            st.markdown(f"### {en}")
            st.caption(ipa)
            reveal_key = f"life_card_reveal_{lesson_index}_{ci}"
            if st.button("Показать перевод", key=reveal_key):
                st.session_state[reveal_key+"_shown"] = True
            if st.session_state.get(reveal_key+"_shown"):
                st.success(ru)
                st.write(example)
                st.caption(example_ru)
            a, b = st.columns(2)
            if a.button("← Предыдущее", key=f"life_card_prev_{lesson_index}"):
                st.session_state[card_key] = (ci - 1) % len(lesson["vocabulary"])
                st.rerun()
            if b.button("Следующее →", key=f"life_card_next_{lesson_index}"):
                st.session_state[card_key] = (ci + 1) % len(lesson["vocabulary"])
                st.rerun()
        with tabs[2]:
            st.markdown("#### Активное вспоминание: русский → английский")
            bank = lesson.get("vocabulary_bank", [])
            if not bank:
                st.info("Словарь для письменной проверки пока готовится.")
            else:
                categories = list(dict.fromkeys(item[0] for item in bank))
                chosen_category = st.selectbox("Категория слов", ["Все категории"] + categories, key=f"life_ru_category_{lesson_index}")
                filtered_bank = [item for item in bank if chosen_category == "Все категории" or item[0] == chosen_category]
                prompt_key = f"life_ru_prompt_{lesson_index}_{chosen_category}"
                if prompt_key not in st.session_state or st.session_state.get(f"{prompt_key}_advance", False):
                    st.session_state[prompt_key] = random.choice(filtered_bank)
                    st.session_state[f"{prompt_key}_advance"] = False
                    st.session_state.pop(f"{prompt_key}_feedback", None)
                item = st.session_state[prompt_key]
                category, english, ipa, russian, example, example_ru = item
                st.caption(f"Категория: {category}")
                st.markdown(f"## {russian}")
                answer_key = f"life_ru_answer_{lesson_index}_{chosen_category}"
                typed = st.text_input("Напиши английское слово или выражение", key=answer_key)
                if st.button("Проверить перевод", type="primary", key=f"life_ru_check_{lesson_index}_{chosen_category}"):
                    normalize = lambda value: " ".join(str(value).strip().casefold().replace(".", "").replace(",", "").split())
                    ok = normalize(typed) == normalize(english)
                    st.session_state[f"{prompt_key}_feedback"] = (ok, english, ipa, example, example_ru)
                    save_result(english, "ru_to_en", typed, ok)
                feedback = st.session_state.get(f"{prompt_key}_feedback")
                if feedback:
                    if feedback[0]:
                        st.success("Правильно! Ты самостоятельно вспомнил английский вариант.")
                    else:
                        st.error("Пока неверно. Правильный ответ: " + feedback[1])
                    st.caption(feedback[2])
                    st.write(feedback[3])
                    st.caption(feedback[4])
                    if st.button("Следующее слово →", key=f"life_ru_next_{lesson_index}_{chosen_category}"):
                        st.session_state[f"{prompt_key}_advance"] = True
                        st.session_state.pop(answer_key, None)
                        st.rerun()
                st.caption(f"В этой тренировке доступно слов: {len(filtered_bank)}. Ошибки и правильные ответы записываются в историю повторения.")
        with tabs[3]:
            g = lesson["grammar"]
            st.markdown("#### " + g["title"])
            st.write(g["rule"])
            for pattern, sample, translation in g["patterns"]:
                st.markdown(f"**{pattern}**")
                st.write(f"{sample} — {translation}")
            st.warning("Типичная ошибка: " + g["common_error"])
        with tabs[4]:
            st.markdown("#### Упражнения — одно задание за раз")
            exercise_list = lesson["exercises"]
            exercise_index_key = f"life_ex_index_{lesson_index}"
            if exercise_index_key not in st.session_state:
                st.session_state[exercise_index_key] = 0
            st.session_state[exercise_index_key] %= len(exercise_list)
            ei = st.session_state[exercise_index_key]
            ex = exercise_list[ei]
            st.caption(f"Задание {ei + 1} из {len(exercise_list)}")
            st.markdown(f"**{ex['question']}**")
            ek = f"life_ex_{lesson_index}_{ei}"
            if ex["type"] == "choice":
                answer = st.radio("Выбери ответ", ex["options"], key=ek, index=None)
            else:
                answer = st.text_input("Твой ответ", key=ek)
            if st.button("Проверить", type="primary", key=ek+"_check"):
                if answer is None or not str(answer).strip():
                    st.warning("Сначала введи ответ.")
                else:
                    norm = lambda x: " ".join(str(x).strip().lower().rstrip(".!?").split())
                    correct = norm(answer) == norm(ex["answer"])
                    st.session_state[ek+"_result"] = (correct, ex["answer"], ex["why"])
            result = st.session_state.get(ek+"_result")
            if result:
                if result[0]:
                    st.success("Правильно!")
                else:
                    st.error("Пока неверно. Правильный вариант: " + result[1])
                st.caption(result[2])
            if st.button("Следующее упражнение →", key=f"life_ex_next_{lesson_index}"):
                st.session_state[exercise_index_key] = (ei + 1) % len(exercise_list)
                st.rerun()
        with tabs[5]:
            st.markdown("#### Диалог на собеседовании")
            for speaker, line, translation in lesson["dialogue"]:
                with st.container(border=True):
                    st.caption(speaker)
                    st.markdown(f"**{line}**")
                    st.write(translation)
        with tabs[6]:
            st.markdown("#### Твоя самостоятельная речь")
            st.write(lesson["roleplay_question"])
            response = st.text_area("Напиши свой ответ на английском", key=f"life_roleplay_{lesson_index}", height=150)
            if st.button("Показать задание ещё раз", key=f"life_roleplay_prompt_{lesson_index}"):
                st.info(lesson["roleplay_question"])
            st.caption("Сначала попробуй ответить самостоятельно. На следующем этапе добавим интерактивный голосовой диалог и проверку ответов.")
            if response.strip():
                st.write(f"Количество слов в ответе: {len(response.split())}")
        with tabs[7]:
            st.markdown("#### Собери английское предложение")
            st.write("Прочитай предложение на русском и нажимай английские слова в правильном порядке. Так ты запоминаешь не отдельные слова, а готовые конструкции.")
            sentence_bank = []
            for item in lesson.get("vocabulary_bank", []):
                sentence_bank.append((item[4], item[5]))
            for item in lesson.get("vocabulary", []):
                sentence_bank.append((item[3], item[4]))
            for speaker, line, translation in lesson.get("dialogue", []):
                sentence_bank.append((line, translation))
            for pattern, sample, translation in lesson.get("grammar", {}).get("patterns", []):
                sentence_bank.append((sample, translation))
            sentence_bank = list(dict.fromkeys((en, ru) for en, ru in sentence_bank if en and ru))
            build_key = f"sentence_builder_{lesson_index}"
            if build_key not in st.session_state:
                st.session_state[build_key] = 0
            st.session_state[build_key] %= len(sentence_bank)
            current_en, current_ru = sentence_bank[st.session_state[build_key]]
            tokens = re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)?|[0-9]+|[^\w\s]", current_en)
            order_key = build_key + "_order"
            selected_key = build_key + "_selected"
            if order_key not in st.session_state or st.session_state.get(build_key + "_sentence") != current_en:
                shuffled = list(range(len(tokens)))
                random.shuffle(shuffled)
                st.session_state[order_key] = shuffled
                st.session_state[selected_key] = []
                st.session_state[build_key + "_sentence"] = current_en
                st.session_state.pop(build_key + "_feedback", None)
            st.markdown("### " + current_ru)
            st.caption(f"Предложение {st.session_state[build_key] + 1} из {len(sentence_bank)}")
            st.markdown("**Твой вариант:**")
            chosen_ids = st.session_state[selected_key]
            if chosen_ids:
                st.markdown(" ".join(tokens[i] for i in chosen_ids))
            else:
                st.info("Нажимай на слова ниже, чтобы собрать предложение.")
            word_cols = st.columns(4)
            for pos, token_id in enumerate(st.session_state[order_key]):
                if token_id not in chosen_ids:
                    if word_cols[pos % 4].button(tokens[token_id], key=f"{build_key}_word_{token_id}"):
                        st.session_state[selected_key].append(token_id)
                        st.session_state.pop(build_key + "_feedback", None)
                        st.rerun()
            left, middle, right = st.columns(3)
            if left.button("Отменить последнее", key=build_key + "_undo", disabled=not chosen_ids):
                st.session_state[selected_key] = chosen_ids[:-1]
                st.session_state.pop(build_key + "_feedback", None)
                st.rerun()
            if middle.button("Очистить", key=build_key + "_clear"):
                st.session_state[selected_key] = []
                st.session_state.pop(build_key + "_feedback", None)
                st.rerun()
            if right.button("Проверить", type="primary", key=build_key + "_check"):
                assembled = " ".join(tokens[i] for i in chosen_ids)
                normalize_sentence = lambda value: " ".join(re.findall(r"[a-z0-9']+", value.casefold()))
                is_correct = normalize_sentence(assembled) == normalize_sentence(current_en)
                st.session_state[build_key + "_feedback"] = (is_correct, current_en)
            feedback = st.session_state.get(build_key + "_feedback")
            if feedback:
                if feedback[0]:
                    st.success("Правильно! Ты собрал предложение.")
                else:
                    st.error("Пока неверно. Правильный вариант: " + feedback[1])
                st.caption(current_en + " — " + current_ru)
            if st.button("Следующее предложение →", type="primary", key=build_key + "_next"):
                st.session_state[build_key] += 1
                st.session_state.pop(order_key, None)
                st.session_state.pop(selected_key, None)
                st.session_state.pop(build_key + "_feedback", None)
                st.rerun()
    else:
        legacy_topic_map = {
            "В магазине": "В магазине", "На улице": "На улице",
            "В транспорте": "В транспорте", "В ресторане": "В ресторане",
            "Аренда жилья": "Аренда жилья", "У врача": "У врача",
            "В аэропорту": "В аэропорту", "В гостинице": "В гостинице"
        }
        selected_topic = st.selectbox("Выбери конкретную ситуацию", legacy_topic_map.keys())
        items = SITUATIONS[legacy_topic_map[selected_topic]]
        for qi, (en, ru, reply, reply_ru) in enumerate(items):
            with st.container(border=True):
                st.markdown(f"**Собеседник:** {en}")
                st.write(ru)
                if st.button("Показать пример ответа", key=f"legacy_situation_{selected_topic}_{qi}"):
                    st.success(reply)
                    st.write(reply_ru)
elif section == "Конструктор заданий":
    st.subheader("Конструктор собственных заданий")
    st.write("Создавай свои вопросы и ответы по грамматике или жизненным ситуациям, сохраняй их и тренируйся.")
    with st.form("task_builder",clear_on_submit=True):
        topic=st.text_input("Тема",placeholder="Например: Собеседование на работу")
        prompt=st.text_area("Задание или вопрос",placeholder="Например: Как сказать «Я могу начать завтра»?")
        answer=st.text_input("Правильный ответ",placeholder="I can start tomorrow.")
        explanation=st.text_area("Объяснение или перевод (необязательно)")
        save=st.form_submit_button("Сохранить задание")
    if save:
        if topic.strip() and prompt.strip() and answer.strip():
            with connect() as conn:
                conn.execute("INSERT INTO custom_tasks(topic,prompt,answer,explanation) VALUES(?,?,?,?)",(topic.strip(),prompt.strip(),answer.strip(),explanation.strip()))
            st.success("Задание сохранено.")
        else: st.warning("Заполни тему, задание и правильный ответ.")
    with connect() as conn:
        topics=[x[0] for x in conn.execute("SELECT DISTINCT topic FROM custom_tasks ORDER BY topic").fetchall()]
    if topics:
        chosen=st.selectbox("Мои наборы заданий",topics)
        with connect() as conn: tasks=conn.execute("SELECT id,prompt,answer,explanation FROM custom_tasks WHERE topic=? ORDER BY id",(chosen,)).fetchall()
        st.markdown(f"### Тренировка: {chosen}")
        if "custom_task_index" not in st.session_state: st.session_state.custom_task_index=0
        st.session_state.custom_task_index%=len(tasks)
        task=tasks[st.session_state.custom_task_index]
        st.write(task[1])
        response=st.text_input("Твой ответ",key=f"custom_answer_{task[0]}")
        if st.button("Проверить задание"):
            if response.strip().casefold()==task[2].strip().casefold(): st.success("Верно!")
            else: st.error("Пока не совпало. Образец: "+task[2])
            if task[3]: st.info(task[3])
        if st.button("Следующее задание"):
            st.session_state.custom_task_index+=1; st.rerun()
        st.divider()
        for tid,p,a,e in tasks:
            with st.expander(p):
                st.write("Ответ: "+a)
                if e: st.caption(e)
                if st.button("Удалить задание",key=f"taskdel{tid}"):
                    with connect() as conn: conn.execute("DELETE FROM custom_tasks WHERE id=?",(tid,))
                    st.rerun()
    else:
        st.info("Пока нет сохранённых заданий. Создай первое в форме выше.")

elif section == "Мой прогресс":
    st.subheader("Мой прогресс")
    with connect() as conn:
        totals=conn.execute("SELECT COALESCE(SUM(correct),0),COALESCE(SUM(wrong),0) FROM word_progress").fetchone()
        weak=conn.execute("SELECT english,wrong,correct FROM word_progress WHERE wrong>0 ORDER BY wrong DESC LIMIT 10").fetchall()
        history=conn.execute("SELECT COUNT(*) FROM test_history").fetchone()[0]
    a,b,c=st.columns(3); a.metric("Правильных ответов",totals[0]); b.metric("Ошибок",totals[1]); c.metric("Проверок выполнено",history)
    st.markdown("### Слова для повторения")
    if weak:
        for en,wrong,correct in weak: st.write(f"**{en}** — ошибок: {wrong}, верных: {correct}")
    else: st.info("Пока нет записанных ошибок.")

st.divider()
st.caption("MY ENGLISH — Метод Холмата · Учебная версия в разработке")
