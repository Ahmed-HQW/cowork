# -*- coding: utf-8 -*-
"""
أول تشغيل: قراءة وفهرسة /home/<user>/zunexa-data فـ الذاكرة طويلة المدى (RAG).
هادشي "fine-tuning محلي" بمفهوم RAG (خفيف على i3/11GB)، بلا ما نمسو Root نهائياً.
"""
from pathlib import Path
from config import TRAIN_SOURCE_DIR, COWORK_DIR
from memory import LongTermMemory
from security import check_path_allowed
from ui import console

MARKER = COWORK_DIR / ".bootstrapped"
TEXT_EXT = {".py", ".md", ".txt", ".json", ".csv", ".sql", ".yaml", ".yml"}


def first_launch_ingest():
    if MARKER.exists():
        return
    if not check_path_allowed(str(TRAIN_SOURCE_DIR)):
        console.print("[red]مصدر الفهرسة خارج النطاق المسموح — تم التجاهل.[/red]")
        return
    if not TRAIN_SOURCE_DIR.exists():
        console.print(f"[yellow]ماكايناش {TRAIN_SOURCE_DIR} — تخطي الفهرسة الأولى.[/yellow]")
        MARKER.touch()
        return

    console.print(f"[blue]📚 أول تشغيل: فهرسة {TRAIN_SOURCE_DIR} ...[/blue]")
    ltm = LongTermMemory()
    total = 0
    for p in TRAIN_SOURCE_DIR.rglob("*"):
        if p.is_file() and p.suffix.lower() in TEXT_EXT and p.stat().st_size < 2_000_000:
            total += ltm.ingest_file(p)
    console.print(f"[green]✅ تمت فهرسة {total} مقطع نصي من قاعدة بياناتك المحلية.[/green]")
    MARKER.touch()
