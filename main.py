#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نقطة الدخول: python3 main.py  (أو الأمر cowork بعد التثبيت)
"""
import sys
from ollama_client import is_server_up
from ui import console, banner, status_bar, show_thinking_tree, memory_notice, session_summary
from bootstrap import first_launch_ingest
from agent import CoworkAgent
from orchestrator import run_multi_agent
from config import NUM_CTX, MODEL_NAME

SLASH_COMMANDS = {
    "/bug": "أبلغ عن مشكلة فالمهمة الحالية",
    "/compact": "ضغط الذاكرة القصيرة",
    "/design": "وضع تصميم/تخطيط بلا تنفيذ (Plan Mode)",
    "/multi": "شغّل عدة agents بالتوازي (coder/tester/docs)",
    "/exit": "خروج",
}


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

    first_launch_ingest()
    memory_notice(str(pathlib.Path.home() / "zunexa-data"))
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
        if user_in in SLASH_COMMANDS:
            console.print(f"[dim]{SLASH_COMMANDS[user_in]}[/dim]")
            continue

        answer = agent.run(user_in)
        console.print(f"[bold green]Cowork:[/bold green] {answer}")
        tokens_used += len(user_in.split()) + len(answer.split())

    session_summary(files_changed, commands_run)
    console.print("[bold magenta]— انتهت الجلسة. مع السلامة 👋[/bold magenta]")


if __name__ == "__main__":
    repl()
