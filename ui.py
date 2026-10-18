# -*- coding: utf-8 -*-
"""
واجهة Terminal (TUI) مستوحاة من Claude Code: status bar, thinking tree,
diff viewer, context indicator, tool confirmations.
"""
import difflib
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.live import Live
from rich.text import Text
from rich.table import Table

console = Console()

MODE_COLORS = {"Plan": "cyan", "Auto": "green"}


def banner():
    console.print(Panel.fit(
        "[bold white]COWORK[/bold white] [dim]— local autonomous agent (offline, qwen2.5:0.5b)[/dim]",
        border_style="bold magenta",
    ))


def status_bar(mode: str, tokens_used: int, ctx_limit: int):
    pct = min(100, int(100 * tokens_used / max(ctx_limit, 1)))
    color = "green" if pct < 60 else ("yellow" if pct < 85 else "red")
    bar = Table.grid(expand=True)
    bar.add_column(justify="left")
    bar.add_column(justify="right")
    bar.add_row(
        f"[{MODE_COLORS.get(mode,'white')}]● {mode} Mode[/]",
        f"[{color}]Context: {tokens_used}/{ctx_limit} ({pct}%)[/]",
    )
    console.print(bar)


def memory_notice(path: str):
    console.print(f"[on blue][white] 🧠 تمت قراءة قواعد الذاكرة: {path} [/white][/on blue]")


def show_thinking_tree(agent_name: str, steps: list[tuple[str, str]]):
    """steps: [(action, note), ...]"""
    tree = Tree(f"[bold yellow]🧩 {agent_name} — Thinking[/bold yellow]")
    for action, note in steps:
        color = {"run_shell": "cyan", "read_file": "blue",
                 "write_file": "magenta", "final_answer": "green"}.get(action, "white")
        tree.add(f"[{color}]{action}[/{color}] {note}")
    console.print(tree)


def diff_viewer(old: str, new: str, filename: str = "file"):
    diff = difflib.unified_diff(old.splitlines(), new.splitlines(),
                                 fromfile=filename, tofile=filename, lineterm="")
    text = Text()
    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            text.append(line + "\n", style="green")
        elif line.startswith("-") and not line.startswith("---"):
            text.append(line + "\n", style="red")
        else:
            text.append(line + "\n", style="dim")
    console.print(Panel(text, title=f"Diff: {filename}", border_style="white"))


def tool_confirm_box(cmd: str) -> bool:
    console.print(Panel(f"[black on yellow] ⚠ تنفيذ أمر: {cmd} [/black on yellow]"))
    ans = console.input("[bold yellow]تأكيد؟ [/bold yellow][Y/n] ").strip().lower()
    return ans in ("y", "yes", "")


def session_summary(files_changed: list[str], commands_run: list[str]):
    table = Table(title="📋 ملخص الجلسة", border_style="bold blue")
    table.add_column("الملفات المعدّلة")
    table.add_column("الأوامر المنفذة")
    rows = max(len(files_changed), len(commands_run), 1)
    for i in range(rows):
        f = files_changed[i] if i < len(files_changed) else ""
        c = commands_run[i] if i < len(commands_run) else ""
        table.add_row(f, c)
    console.print(table)
