# -*- coding: utf-8 -*-
"""
الأدوات (Tools) اللي يقدر الـ Agent يستعملهم.
كل أداة محمية بطبقة الأمان (security.py) قبل التنفيذ.
"""
import subprocess
from pathlib import Path
from pydantic import BaseModel, ValidationError

from security import enforce_path, is_dangerous_command, confirm_dangerous, SecurityViolation


# ---------- Schemas (Pydantic) للتحقق قبل التنفيذ ----------
class ShellParams(BaseModel):
    cmd: str


class FileReadParams(BaseModel):
    path: str


class FileWriteParams(BaseModel):
    path: str
    content: str


class FinalAnswerParams(BaseModel):
    answer: str


TOOL_SCHEMAS = {
    "run_shell": ShellParams,
    "read_file": FileReadParams,
    "write_file": FileWriteParams,
    "final_answer": FinalAnswerParams,
}


def validate_params(action: str, params: dict):
    schema = TOOL_SCHEMAS.get(action)
    if not schema:
        raise ValueError(f"أداة غير معروفة: {action}")
    try:
        return schema(**params)
    except ValidationError as e:
        raise ValueError(f"params غير صالحة لـ {action}: {e}")


# ---------- التنفيذ الفعلي ----------
def run_shell(cmd: str) -> str:
    if is_dangerous_command(cmd):
        if not confirm_dangerous(cmd):
            return "[رُفض من المستخدم]"
    try:
        out = subprocess.run(cmd, shell=True, cwd=str(Path.home()),
                              capture_output=True, text=True, timeout=120)
        return (out.stdout or "") + (out.stderr or "")
    except Exception as e:
        return f"[خطأ تنفيذ]: {e}"


def read_file(path: str) -> str:
    enforce_path(path, "قراءة")
    p = Path(path).expanduser()
    if not p.exists():
        return f"[غير موجود]: {path}"
    return p.read_text(errors="ignore")[:20000]


def write_file(path: str, content: str) -> str:
    enforce_path(path, "كتابة")
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"[تمت الكتابة]: {path}"


def dispatch(action: str, params: dict) -> str:
    """نقطة الدخول الوحيدة لتنفيذ أداة — تمر دايماً من validate_params + security."""
    valid = validate_params(action, params)
    try:
        if action == "run_shell":
            return run_shell(valid.cmd)
        if action == "read_file":
            return read_file(valid.path)
        if action == "write_file":
            return write_file(valid.path, valid.content)
        if action == "final_answer":
            return valid.answer
    except SecurityViolation as e:
        return str(e)
    return "[أداة غير مدعومة]"
