# -*- coding: utf-8 -*-
"""
تشغيل المهام الثقيلة (فهرسة، fine-tune-RAG) فـ thread خلفي
باش الـ REPL يبقى حر وما يتسناش حتى حاجة.
"""
import json
import threading
from pathlib import Path
from config import COWORK_DIR

STATUS_FILE = COWORK_DIR / "job_status.json"
_lock = threading.Lock()

# كيوقف أي فهرسة خلفية وقت ما يكون فيه سؤال شات حي — باش ما يتنافسوش على CPU
chat_active = threading.Event()


def pause_if_chatting():
    """تُستدعى بين كل ملف/chunk فـ الفهرسة — كتوقف وقت ما يكون شات خدام."""
    while chat_active.is_set():
        threading.Event().wait(0.3)


def set_status(job: str, state: str, progress: str = ""):
    with _lock:
        data = {}
        if STATUS_FILE.exists():
            try:
                data = json.loads(STATUS_FILE.read_text())
            except Exception:
                data = {}
        data[job] = {"state": state, "progress": progress}
        STATUS_FILE.write_text(json.dumps(data, ensure_ascii=False))


def get_status() -> dict:
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text())
        except Exception:
            return {}
    return {}


def run_in_background(job_name: str, fn, *args, **kwargs):
    """كيلانشي fn فـ thread daemon منفصل، وكيسجل الحالة فـ STATUS_FILE."""
    def _wrapper():
        set_status(job_name, "running")
        try:
            fn(*args, **kwargs)
            set_status(job_name, "done")
        except Exception as e:
            set_status(job_name, f"error: {e}")

    t = threading.Thread(target=_wrapper, daemon=True, name=job_name)
    t.start()
    return t
