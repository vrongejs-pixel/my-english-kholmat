"""Structured content for the expandable practical-life curriculum."""

JOB_INTERVIEW = {
    "title": "Собеседование на работу",
    "level": "A1–A2",
    "lessons": [
        {
            "title": "Первое знакомство и рассказ о себе",
            "goal": "Поздороваться, представиться и кратко рассказать о себе на собеседовании.",
            "vocabulary": [
                ("interview", "/ˈɪntəvjuː/", "собеседование", "I have an interview today.", "Сегодня у меня собеседование."),
                ("job", "/dʒɒb/", "работа; должность", "I am looking for a job.", "Я ищу работу."),
                ("experience", "/ɪkˈspɪəriəns/", "опыт", "I have work experience.", "У меня есть опыт работы."),
                ("skill", "/skɪl/", "навык", "I have good communication skills.", "У меня хорошие навыки общения."),
                ("introduce", "/ˌɪntrəˈdjuːs/", "представлять; знакомить", "Let me introduce myself.", "Позвольте представиться."),
                ("currently", "/ˈkʌrəntli/", "в настоящее время", "I am currently looking for work.", "В настоящее время я ищу работу."),
                ("previous", "/ˈpriːviəs/", "предыдущий", "My previous job was in a factory.", "Моя предыдущая работа была на заводе."),
                ("reliable", "/rɪˈlaɪəbl/", "надёжный", "I am reliable and hardworking.", "Я надёжный и трудолюбивый."),
                ("available", "/əˈveɪləbl/", "готовый приступить; доступный", "I am available from Monday.", "Я могу приступить с понедельника."),
                ("hire", "/ˈhaɪə(r)/", "нанимать на работу", "Are you hiring new workers?", "Вы нанимаете новых работников?")
            ],
            "grammar": {
                "title": "Глагол to be в рассказе о себе",
                "rule": "Используем am с I: I am ... (Я ...). Для профессии перед существительным обычно нужен a/an: I am a driver (Я водитель). Для описания навыков и качеств используем прилагательное: I am reliable (Я надёжный).",
                "patterns": [
                    ("I am + профессия", "I am a mechanic.", "Я механик."),
                    ("I am + прилагательное", "I am hardworking.", "Я трудолюбивый."),
                    ("I am from + страна/город", "I am from Uzbekistan.", "Я из Узбекистана."),
                    ("I have + существительное", "I have experience.", "У меня есть опыт.")
                ],
                "common_error": "Нельзя говорить «I am work» в значении «Я работаю». Нужно «I work» (Present Simple) или «I am working» (сейчас работаю)."
            },
            "dialogue": [
                ("Interviewer", "Good morning. Please, come in.", "Доброе утро. Пожалуйста, проходите."),
                ("Candidate", "Good morning. Thank you.", "Доброе утро. Спасибо."),
                ("Interviewer", "Could you introduce yourself?", "Не могли бы вы представиться?"),
                ("Candidate", "My name is ____. I am from Uzbekistan.", "Меня зовут ____. Я из Узбекистана."),
                ("Candidate", "I have experience in ____. I am reliable and hardworking.", "У меня есть опыт в ____. Я надёжный и трудолюбивый."),
                ("Interviewer", "Thank you. Tell me about your previous job.", "Спасибо. Расскажите о вашей предыдущей работе.")
            ],
            "exercises": [
                {"type":"choice","question":"Как правильно сказать «Я из Узбекистана»?","options":["I is from Uzbekistan.","I am from Uzbekistan.","I from Uzbekistan."],"answer":"I am from Uzbekistan.","why":"С местоимением I используем am."},
                {"type":"text","question":"Вставь пропущенное слово: I ___ reliable.","answer":"am","why":"I + am + прилагательное."},
                {"type":"translate","question":"Переведи на английский: «У меня есть опыт работы».","answer":"I have work experience.","why":"I have = у меня есть; work experience = опыт работы."},
                {"type":"choice","question":"Выбери правильное предложение: «Я механик».","options":["I am mechanic.","I am a mechanic.","I a mechanic."],"answer":"I am a mechanic.","why":"Перед исчисляемой профессией в единственном числе используем a/an."}
            ],
            "roleplay_question": "Представься работодателю. Напиши 3–5 предложений: как тебя зовут, откуда ты, какая у тебя профессия или опыт, какие у тебя сильные качества."
        }
    ]
}
