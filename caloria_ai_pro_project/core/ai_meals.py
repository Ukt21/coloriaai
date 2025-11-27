from __future__ import annotations

import json
from typing import Dict

from openai import OpenAI

from config import settings


def _heuristic_analysis(text: str) -> Dict:
    """Простейший анализ без ИИ, на ключевых словах.

    Используется, если OPENAI_API_KEY не задан или ИИ недоступен.
    """
    base_cal = 350
    t = text.lower()

    if any(w in t for w in ["бургер", "шаурма", "пицца", "фастфуд", "фри"]):
        base_cal = 700
    elif any(w in t for w in ["салат", "овощ", "овощи", "зелень"]):
        base_cal = 200
    elif any(w in t for w in ["стейк", "мясо", "курица", "шашлык", "биф"]):
        base_cal = 500
    elif any(w in t for w in ["овсянка", "каша", "гречка", "рис"]):
        base_cal = 300

    if base_cal > 650:
        goal_hint = "многовато, если цель — похудеть"
    elif base_cal < 250:
        goal_hint = "маловато как полноценный приём пищи"
    else:
        goal_hint = "подходит для поддержания веса"

    return {
        "description": text,
        "calories": base_cal,
        "goal_hint": goal_hint,
        "source": "heuristic",
    }


def analyze_meal_text(text: str) -> Dict:
    """Анализ описания еды с помощью OpenAI (если доступен) или эвристики.

    Возвращает словарь:
    - description: краткое описание
    - calories: примерные калории
    - goal_hint: комментарий
    - source: openai|heuristic
    """
    if not settings.openai_api_key:
        return _heuristic_analysis(text)

    try:
        client = OpenAI(api_key=settings.openai_api_key)
        prompt = (
            "Ты — ассистент по питанию. Пользователь описывает приём пищи.
"
            "Опиши его кратко и оцени примерное количество калорий.
"
            "Верни JSON с полями: description (строка), calories (число), "
            "goal_hint (строка, комментарий по похудению/набору/поддержанию).

"
            f"Приём пищи: {text}"
        )

        completion = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "meal_analysis",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "calories": {"type": "number"},
                            "goal_hint": {"type": "string"},
                        },
                        "required": ["description", "calories", "goal_hint"],
                        "additionalProperties": False,
                    },
                },
            },
        )

        content = completion.output[0].content[0].text  # type: ignore[attr-defined]
        data = json.loads(content)

        return {
            "description": data.get("description", text),
            "calories": int(data.get("calories", 350)),
            "goal_hint": data.get("goal_hint", ""),
            "source": "openai",
        }
    except Exception:
        # Любая ошибка ИИ — мягко откатываемся на эвристику
        return _heuristic_analysis(text)
