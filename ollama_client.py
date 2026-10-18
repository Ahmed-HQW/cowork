# -*- coding: utf-8 -*-
import json
import requests
from config import OLLAMA_HOST, MODEL_NAME, EMBED_MODEL, NUM_CTX, TEMPERATURE


def chat(messages: list[dict], model: str = MODEL_NAME, force_json: bool = True) -> str:
    """نداء Ollama /api/chat مع format=json لإجبار structured output."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"num_ctx": NUM_CTX, "temperature": TEMPERATURE},
    }
    if force_json:
        payload["format"] = "json"

    r = requests.post(f"{OLLAMA_HOST}/api/chat", json=payload, timeout=300)
    r.raise_for_status()
    data = r.json()
    return data.get("message", {}).get("content", "")


def embed(text: str, model: str = EMBED_MODEL) -> list[float]:
    r = requests.post(f"{OLLAMA_HOST}/api/embeddings", json={"model": model, "prompt": text}, timeout=120)
    r.raise_for_status()
    return r.json().get("embedding", [])


def is_server_up() -> bool:
    try:
        requests.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        return True
    except Exception:
        return False
