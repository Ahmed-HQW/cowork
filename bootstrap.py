# -*- coding: utf-8 -*-
"""
أول تشغيل: قراءة وفهرسة /home/<user>/zunexa-data فـ الذاكرة طويلة المدى (RAG).
هادشي "fine-tuning محلي" بمفهوم RAG (خفيف على i3/11GB)، بلا ما نمسو Root نهائياً.

تحسينات:
- تجاهل venv/site-packages/__pycache__ وكل ملفات المكتبات (ماشي داتا ديالك).
- progress bar حية باش تعرف فين وصل.
- checkpoint (resume) باش إذا وقفتيه يكمل من فين خلا، ما يعاودش من الصفر.
"""
import json
from pathlib import Path
from config import TRAIN_SOURCE_DIR, COWORK_DIR
from memory import LongTermMemory
from security import check_path_allowed
from ui import console
from background import set_status, pause_if_chatting

MARKER = COWORK_DIR / ".bootstrapped"
CHECKPOINT = COWORK_DIR / ".ingest_checkpoint.json"
TEXT_EXT = {".py", ".md", ".txt", ".json", ".csv", ".sql", ".yaml", ".yml"}
MAX_FILE_SIZE = 500_000  # 500KB كاف لملفات نصية حقيقية، كيفلتر ملفات ضخمة غريبة

# مجلدات ماشي خاصها تتفهرس أبداً (بيئات افتراضية، مكتبات، كاش...)
SKIP_DIR_NAMES = {
    "venv", ".venv", "env", "site-packages", "__pycache__", "node_modules",
    ".git", "dist-info", "egg-info", "build", "dist", ".cache", "triton-cache",
}


def _should_skip(p: Path) -> bool:
    return any(part in SKIP_DIR_NAMES or part.endswith((".dist-info", ".egg-info"))
               for part in p.parts)


def _load_checkpoint() -> set:
    if CHECKPOINT.exists():
        try:
            return set(json.loads(CHECKPOINT.read_text()))
        except Exception:
            return set()
    return set()


def _save_checkpoint(done: set):
    CHECKPOINT.write_text(json.dumps(list(done)))


def ingest_path(source: Path, job_name: str, marker: Path | None = None):
    """
    فهرسة مسار كيفما كان، بدون ما يوقف الـ REPL — تُستدعى دايماً عبر
    background.run_in_background() من main.py.
    """
    if not check_path_allowed(str(source)):
        set_status(job_name, "error: مسار خارج النطاق المسموح")
        return
    if not source.exists():
        set_status(job_name, f"error: {source} غير موجود")
        return

    candidates = [
        p for p in source.rglob("*")
        if p.is_file()
        and p.suffix.lower() in TEXT_EXT
        and p.stat().st_size < MAX_FILE_SIZE
        and not _should_skip(p)
    ]
    if not candidates:
        set_status(job_name, "done", "0 ملف")
        if marker:
            marker.touch()
        return

    done = _load_checkpoint()
    remaining = [p for p in candidates if str(p) not in done]
    total = len(remaining)
    ltm = LongTermMemory()
    chunks = 0

    for i, p in enumerate(remaining):
        pause_if_chatting()  # نسكتو الفهرسة وقت ما تكون كتسول الشات
        set_status(job_name, "running", f"{i}/{total} — {p.name}")
        try:
            chunks += ltm.ingest_file(p)
        except Exception:
            pass
        done.add(str(p))
        if i % 20 == 0:
            _save_checkpoint(done)

    _save_checkpoint(done)
    set_status(job_name, "done", f"{chunks} مقطع من {total} ملف")
    if marker:
        marker.touch()


def first_launch_ingest():
    """تُستدعى فـ thread خلفي من main.py — ماشي بشكل مباشر/blocking."""
    if MARKER.exists():
        return
    ingest_path(TRAIN_SOURCE_DIR, "bootstrap", MARKER)


def full_home_scan(home: Path):
    """فهرسة /home/<user> كاملة فـ الخلفية."""
    ingest_path(home, "home_scan")
