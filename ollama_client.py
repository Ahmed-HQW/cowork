# -*- coding: utf-8 -*-
import json
import requests
from config import OLLAMA_HOST, MODEL_NAME, EMBED_MODEL, NUM_CTX, TEMPERATURE, NUM_THREAD


def chat(messages: list[dict], model: str = MODEL_NAME, force_json: bool = True) -> str:
    """
    نداء Ollama /api/chat — بلا format=json (كيبطّي الـ decoding بزاف على CPU ضعيف
    بسبب grammar-constrained sampling). التحقق من صحة JSON كيتدار بعدياً فـ agent.py.
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "keep_alive": "30m",
        "options": {
            "num_ctx": NUM_CTX,
            "temperature": TEMPERATURE,
            "num_thread": NUM_THREAD,
            "num_predict": 220,   # نحدو عدد التوكنز اللي كيولدهم — ما يكملش يحكي بلا حاجة
        },
    }
    if force_json:
        payload["format"] = "json"

    r = requests.post(f"{OLLAMA_HOST}/api/chat", json=payload, timeout=180)
    r.raise_for_status()
    data = r.json()
    return data.get("message", {}).get("content", "")


def embed(text: str, model: str = EMBED_MODEL) -> list[float]:
    r = requests.post(
        f"{OLLAMA_HOST}/api/embeddings",
        json={"model": model, "prompt": text, "keep_alive": "30m"},
        timeout=120,
    )
    r.raise_for_status()
    return r.json().get("embedding", [])


def is_server_up() -> bool:
    try:
        requests.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        return True
    except Exception:
        return False
