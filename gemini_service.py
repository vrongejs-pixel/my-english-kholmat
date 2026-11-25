"""Gemini integration for MY ENGLISH — Метод Холмата.
The API key is read only from Streamlit Secrets or the hosting environment.
"""
import os
import streamlit as st
from google import genai
from google.genai import types

MODEL_ID = "gemini-3.8-flash"

@st.cache_resource(show_spinner=False)
def _client(api_key: str):
    return genai.Client(api_key=api_key)

def api_key():
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""
    return key or os.getenv("GEMINI_API_KEY", "")

def ready():
    return bool(api_key())

def generate_text(prompt: str, system_instruction: str, max_output_tokens: int = 1800) -> str:
    key = api_key()
    if not key:
        raise RuntimeError("Gemini не подключён. Добавь GEMINI_API_KEY в Streamlit Secrets.")
    response = _client(key).models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.45,
            max_output_tokens=max_output_tokens,
        ),
    )
    result = (response.text or "").strip()
    if not result:
        raise RuntimeError("Gemini вернул пустой ответ. Попробуй ещё раз.")
    return result

def grammar_practice(topic: str, level: str, rule: str, count: int, task_type: str) -> str:
    system = (
        "Ты — опытный преподаватель английского языка и методист персонального курса. "
        "Объясняй по-русски, задания и примеры давай на английском с русским переводом. "
        "Не используй лексику выше указанного уровня без перевода. "
        "Создавай корректные, естественные задания, не повторяй один шаблон. "
        "В конце дай ключи ответов и короткие объяснения в отдельном разделе "
        "«Ответы для самопроверки», чтобы ученик мог сначала решить сам."
    )
    prompt = (
        f"Создай {count} новых заданий по теме: {topic}. Уровень: {level}.\n"
        f"Правило курса: {rule}\nТип заданий: {task_type}.\n"
        "Структура: короткое напоминание правила; нумерованные задания; "
        "после них ответы и объяснения. Используй разные контексты из жизни и работы. "
        "Не копируй стандартные примеры из учебников."
    )
    return generate_text(prompt, system, 2600)

def tutor_reply(messages: list, level: str, scenario: str) -> str:
    system = (
        "Ты — терпеливый преподаватель разговорного английского для взрослого ученика. "
        "Пользователь изучает английский для жизни и работы за границей. "
        f"Уровень ученика: {level}. Сценарий: {scenario}. "
        "Веди реалистичный диалог от лица выбранного собеседника. "
        "Задавай только один вопрос за раз и жди ответ. "
        "После каждого ответа ученика кратко исправляй ошибки на русском, "
        "показывай естественный вариант на английском и его русский перевод, "
        "затем продолжай разговор одним следующим вопросом. "
        "Не отвечай за ученика и не превращай диалог в длинную лекцию. "
        "Если ученик пишет по-русски, помоги сформулировать ответ по-английски."
    )
    transcript = []
    for item in messages[-16:]:
        role = "Ученик" if item["role"] == "user" else "Преподаватель"
        transcript.append(f"{role}: {item['content']}")
    return generate_text("\n".join(transcript) or "Начни диалог с приветствия.", system, 900)
