"""Gemini integration for MY ENGLISH. API keys are read only from Streamlit secrets/env."""
import os
import streamlit as st


def get_api_key():
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key:
            return str(key).strip()
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", "").strip()


def get_client():
    key = get_api_key()
    if not key:
        return None, "Не найден GEMINI_API_KEY. Добавь ключ в Streamlit Secrets."
    try:
        from google import genai
        return genai.Client(api_key=key), None
    except Exception as exc:
        return None, f"Не удалось загрузить Gemini SDK: {exc}"


def ask_gemini(prompt, system_instruction=None, model="gemini-3.8-flash"):
    client, error = get_client()
    if error:
        return None, error
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "system_instruction": system_instruction or (
                    "You are MY ENGLISH, a patient professional English tutor. "
                    "Explain in Russian. Use natural modern English. Match the learner's level. "
                    "Never invent a learner's answers or claim an answer is correct without checking it."
                ),
                "temperature": 0.7,
            },
        )
        answer = (getattr(response, "text", None) or "").strip()
        return (answer, None) if answer else (None, "Gemini вернул пустой ответ. Попробуй ещё раз.")
    except Exception as exc:
        return None, f"Ошибка Gemini API: {exc}"


def grammar_exercise(topic, level, count, exercise_type, known_words=""):
    prompt = f"""
Создай {count} новых упражнений по английской грамматике.
Тема: {topic}
Уровень: {level}
Тип упражнений: {exercise_type}
Используй знакомую лексику, если она указана: {known_words or "базовая повседневная лексика"}.
Для каждого задания дай:
1. Номер и условие.
2. Если это тест — 4 варианта ответа.
3. Правильный ответ.
4. Короткое объяснение на русском.
5. Перевод задания на русский, если условие на английском.
Не повторяй один и тот же шаблон. Не используй двусмысленные задания.
В конце добавь мини-правило по теме на русском.
"""
    return ask_gemini(prompt)


def check_english(topic, level, question, learner_answer, expected_answer=""):
    prompt = f"""
Проверь ответ изучающего английский.
Тема: {topic}; уровень: {level}
Задание: {question}
Ответ ученика: {learner_answer}
Ориентир/образец (может быть пустым): {expected_answer}
Оцени смысл и грамматику, допускай другие естественные правильные варианты.
Ответь по-русски: верно/частично/неверно; исправленный естественный вариант;
конкретно объясни ошибку; дай один похожий короткий пример с переводом.
"""
    return ask_gemini(prompt)


def roleplay_reply(situation, level, dialogue_history, user_message):
    prompt = f"""
Проведи реалистичный разговор на английском в роли: {situation}.
Уровень ученика: {level}.
История диалога:
{dialogue_history or "Диалог только начинается."}
Последнее сообщение ученика: {user_message}
Сначала ответь как реальный собеседник на естественном английском (1-3 предложения).
Затем на русском кратко переведи свой ответ.
Затем отдельным блоком оцени английский ученика: исправь только важные ошибки и объясни их.
Не выходи из роли, задавай один естественный следующий вопрос. Не делай диалог слишком сложным.
"""
    return ask_gemini(prompt)


def create_vocabulary_examples(words, level):
    prompt = f"""
Для этих английских слов создай естественные короткие примеры уровня {level}.
Слова: {words}
Для каждого слова: английское предложение, точный русский перевод, типичная сочетаемость.
Не придумывай редкие значения; если слово многозначное, укажи самое полезное разговорное значение.
"""
    return ask_gemini(prompt)
