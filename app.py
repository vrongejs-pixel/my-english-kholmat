import random
import sqlite3
from pathlib import Path
import streamlit as st

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "my_english_progress.db"

from vocabulary_data import VOCABULARY

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

def save_result(item, direction, answer, correct):
    with connect() as conn:
        conn.execute("""INSERT INTO word_progress (english, correct, wrong, last_result)
            VALUES (?, ?, ?, ?) ON CONFLICT(english) DO UPDATE SET
            correct=correct+excluded.correct, wrong=wrong+excluded.wrong,
            last_result=excluded.last_result""",
            (item, int(correct), int(not correct), "correct" if correct else "wrong"))
        conn.execute("INSERT INTO test_history (item,direction,user_answer,is_correct) VALUES (?,?,?,?)",
                     (item, direction, answer, int(correct)))

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
st.sidebar.radio("Разделы", ["Главная","Карточки слов","Мои сборники","Проверка слов","Грамматика","Жизненные ситуации","Конструктор заданий","Мой прогресс"], key="nav_choice", on_change=navigate, index=["Главная","Карточки слов","Мои сборники","Проверка слов","Грамматика","Жизненные ситуации","Конструктор заданий","Мой прогресс"].index(st.session_state.section))
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
    decks=get_decks()
    labels=["Базовый словарь A1"]+[f"Мой сборник: {name}" for _,name in decks]
    source=st.selectbox("Сборник",labels,key="flash_deck")
    if source=="Базовый словарь A1":
        words=[(i,e,r,c) for i,(e,r,c) in enumerate(BASE_WORDS)]
    else:
        name=source.replace("Мой сборник: ","",1)
        did=next((i for i,n in decks if n==name),None)
        words=get_words(did) if did else []
    direction=st.radio("Лицевая сторона",["Английский → Русский","Русский → Английский","Смешанный режим"],horizontal=True,key="flash_direction")
    if source=="Базовый словарь A1":
        categories=st.multiselect("Группы слов",list(VOCABULARY.keys()),default=list(VOCABULARY.keys()),key="flash_categories")
        selected=[(i,*word) for i,(category,items) in enumerate(VOCABULARY.items()) if category in categories for word in items]
        words=selected
    else:
        words=[(row[0],row[1],row[2],"","") for row in words]
    if not words:
        st.warning("Выбери хотя бы одну группу или добавь слова в свой сборник.")
    else:
        signature=(source,direction,tuple(st.session_state.get("flash_categories",[])))
        if st.session_state.get("flash_signature")!=signature:
            st.session_state.flash_signature=signature
            st.session_state.card_index=0
            st.session_state.card_revealed=False
        st.session_state.card_index%=len(words)
        w=words[st.session_state.card_index]
        # Fix the mixed direction for the current card; do not randomize it on reruns.
        if st.session_state.get("flash_card_signature") != (signature,st.session_state.card_index):
            actual=random.choice(["Английский → Русский","Русский → Английский"]) if direction=="Смешанный режим" else direction
            st.session_state.flash_actual_direction=actual
            st.session_state.flash_card_signature=(signature,st.session_state.card_index)
        actual=st.session_state.flash_actual_direction
        english,russian=w[1],w[2]
        pronunciation=w[3] if len(w)>3 else ""
        example=w[4] if len(w)>4 else ""
        example_ru=w[5] if len(w)>5 else ""
        front,back=(english,russian) if actual=="Английский → Русский" else (russian,english)
        st.caption(f"Направление: {actual} · Группа: {w[3] if len(w)==4 else 'Словарь'}")
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
            if pronunciation: st.write(f"**Произношение:** {pronunciation}")
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
        st.caption(f"Знаю: {st.session_state.known_count} · На повторение: {len(st.session_state.repeat_words)}")
        if st.session_state.repeat_words:
            with st.expander("Слова для повторения"):
                for en,ru in st.session_state.repeat_words:
                    st.write(f"**{en}** — {ru}")

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
    st.subheader("Курс грамматики")
    st.write("Выбирай тему, изучай правило и выполняй упражнения. Начинаем с A1 и постепенно усложняем.")
    lesson_names=[f"{x['level']} · {x['title']}" for x in GRAMMAR]
    idx=st.selectbox("Тема урока",range(len(GRAMMAR)),format_func=lambda i:lesson_names[i])
    lesson=GRAMMAR[idx]
    st.markdown("### Правило")
    st.write(lesson["rule"])
    st.markdown("### Примеры")
    for ex in lesson["examples"]: st.write("• "+ex)
    st.divider()
    st.markdown(f"### Упражнения · {len(lesson['tasks'])} заданий")
    qidx=st.selectbox("Выбери задание",range(len(lesson["tasks"])),format_func=lambda i:f"Задание {i+1} из {len(lesson['tasks'])}")
    q,opts,correct,explain=lesson["tasks"][qidx]
    choice=st.radio(q,opts,key=f"gram_{idx}_{qidx}")
    if st.button("Проверить грамматику",type="primary"):
        st.session_state.grammar_feedback=(idx,qidx,choice==correct,correct,explain)
    fb=st.session_state.grammar_feedback
    if fb and fb[0:2]==(idx,qidx):
        if fb[2]: st.success("Правильно! "+fb[4])
        else: st.error(f"Неверно. Правильный ответ: {fb[3]}. {fb[4]}")
    st.caption("Курс будет расширяться: новые темы и дополнительные упражнения добавляются отдельными уроками.")

elif section == "Жизненные ситуации":
    st.subheader("Английский для реальной жизни")
    topic=st.selectbox("Выбери ситуацию",list(SITUATIONS.keys()))
    items=SITUATIONS[topic]
    st.write("Изучи фразу, затем попробуй самостоятельно вспомнить ответ и проверить себя.")
    qidx=st.selectbox("Выбери ситуацию внутри темы",range(len(items)),format_func=lambda i:f"Фраза {i+1} из {len(items)}")
    en,ru,reply,reply_ru=items[qidx]
    st.markdown("#### Что ты услышишь")
    st.markdown(f"**{en}**")
    st.write(ru)
    st.markdown("#### Как можно ответить")
    if st.button("Показать пример ответа"):
        st.session_state.situation_reveal=(topic,qidx)
    if st.session_state.get("situation_reveal")== (topic,qidx):
        st.success(reply)
        st.write(reply_ru)
    st.divider()
    st.markdown("#### Проверь понимание")
    user_translation=st.text_input("Напиши по-английски ответ из примера (можно своими словами)",key=f"situation_{topic}_{qidx}")
    if st.button("Показать образец и сравнить"):
        st.session_state.situation_feedback=(topic,qidx,user_translation)
    if st.session_state.get("situation_feedback",("",-1,""))[:2]==(topic,qidx):
        st.info(f"Образец: {reply} — {reply_ru}")
        st.write("Твой ответ: "+(st.session_state.situation_feedback[2] or "Ответ не введён."))

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
