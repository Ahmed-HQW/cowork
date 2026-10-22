#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نقطة الدخول: python3 main.py  (أو الأمر cowork بعد التثبيت)
"""
import sys
from pathlib import Path
import shutil
from ollama_client import is_server_up
from ui import console, banner, status_bar, show_thinking_tree, memory_notice, session_summary
from bootstrap import first_launch_ingest, full_home_scan
from background import run_in_background, get_status, chat_active
from agent import CoworkAgent
from orchestrator import run_multi_agent
from config import NUM_CTX, MODEL_NAME, COWORK_DIR, CACHE_DIR, DB_DIR, LOG_DIR, HOME

SLASH_COMMANDS = {
    "/bug": "أبلغ عن مشكلة فالمهمة الحالية",
    "/compact": "ضغط الذاكرة القصيرة",
    "/design": "وضع تصميم/تخطيط بلا تنفيذ (Plan Mode)",
    "/multi": "شغّل عدة agents بالتوازي (coder/tester/docs)",
    "/scan-home": "فهرسة /home/<user> كاملة فـ الخلفية (RAG)",
    "/jobs": "عرض حالة المهام الخلفية (فهرسة، إلخ)",
    "/clean-cache": "مسح كاش Cowork (vectordb, cache, logs, checkpoints)",
    "/exit": "خروج",
}


def clean_cache():
    targets = [CACHE_DIR, DB_DIR, LOG_DIR,
               COWORK_DIR / ".ingest_checkpoint.json",
               COWORK_DIR / ".bootstrapped",
               COWORK_DIR / "job_status.json"]
    for t in targets:
        if t.is_dir():
            shutil.rmtree(t, ignore_errors=True)
            t.mkdir(parents=True, exist_ok=True)
        elif t.exists():
            t.unlink()
    console.print("[green]🧹 تم مسح الكاش بالكامل (vectordb + logs + checkpoints).[/green]")


def event_logger(agent_name, kind, data):
    if kind == "thinking":
        console.print(f"[dim yellow]💭 [{agent_name}][/dim yellow] {data}")
    elif kind == "action":
        console.print(f"[cyan]⚙ [{agent_name}][/cyan] {data['action']} {data.get('params', {})}")
    elif kind == "result":
        console.print(f"[white]↪ [{agent_name}][/white] {str(data)[:300]}")
    elif kind == "error":
        console.print(f"[red]✗ [{agent_name}][/red] {data}")


def repl():
    import pathlib
    banner()
    if not is_server_up():
        console.print("[red]✗ Ollama ماشي خدام. دير: `ollama serve` و `ollama pull qwen2.5:0.5b`[/red]")
        sys.exit(1)

    # الفهرسة تخدم فـ thread خلفي — الـ REPL يبدا direct بلا تسنية
    run_in_background("bootstrap", first_launch_ingest)
    console.print("[dim]📚 الفهرسة الأولى بدات فـ الخلفية (/jobs باش تتبع التقدم)...[/dim]")
    mode = "Auto"
    tokens_used = 0
    agent = CoworkAgent(on_event=event_logger)

    files_changed, commands_run = [], []

    while True:
        status_bar(mode, tokens_used, NUM_CTX)
        try:
            user_in = console.input("[bold magenta]cowork[/bold magenta] [dim]›[/dim] ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_in:
            continue

        if user_in == "/exit":
            break
        if user_in == "/design":
            mode = "Plan"
            console.print("[cyan]تم التحول لـ Plan Mode (تخطيط بلا تنفيذ فعلي).[/cyan]")
            continue
        if user_in.startswith("/multi"):
            goal = user_in.replace("/multi", "").strip() or "حسّن هاد المشروع"
            results = run_multi_agent(goal, ["coder", "tester", "docs"], on_event=event_logger)
            for role, out in results.items():
                console.print(f"[bold]{role}:[/bold] {out}")
            continue
        if user_in == "/scan-home":
            run_in_background("home_scan", full_home_scan, HOME)
            console.print("[dim]🔍 فهرسة /home بدات فـ الخلفية (/jobs باش تتبع).[/dim]")
            continue
        if user_in == "/jobs":
            for job, info in get_status().items():
                console.print(f"[cyan]{job}[/cyan]: {info['state']} — {info.get('progress','')}")
            continue
        if user_in == "/clean-cache":
            clean_cache()
            continue
        if user_in in SLASH_COMMANDS:
            console.print(f"[dim]{SLASH_COMMANDS[user_in]}[/dim]")
            continue

        chat_active.set()  # نوقفو الفهرسة الخلفية وقت التفكير باش ما يتناحصروش على الـ CPU
        try:
            with console.status("[yellow]🤔 كيفكر...[/yellow]", spinner="dots"):
                answer = agent.run(user_in)
        finally:
            chat_active.clear()
        console.print(f"[bold green]Cowork:[/bold green] {answer}")
        tokens_used += len(user_in.split()) + len(answer.split())

    session_summary(files_changed, commands_run)
    console.print("[bold magenta]— انتهت الجلسة. مع السلامة 👋[/bold magenta]")


if __name__ == "__main__":
    repl()
