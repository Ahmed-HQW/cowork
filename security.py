# -*- coding: utf-8 -*-
"""
طبقة الأمان: حماية Root + فلترة الأوامر الخطيرة.
هادي الطبقة ما كتتعطلش من داخل الـ LLM — هي hard-coded فالكود.
"""
import os
import sys
from pathlib import Path
from config import FORBIDDEN_PREFIXES, ALLOWED_PREFIXES, DANGEROUS_PATTERNS


class SecurityViolation(Exception):
    pass


def check_path_allowed(path: str) -> bool:
    """يرجع True إذا المسار مسموح، False إذا محظور."""
    try:
        resolved = str(Path(path).expanduser().resolve())
    except Exception:
        return False

    for forb in FORBIDDEN_PREFIXES:
        if resolved == forb or resolved.startswith(forb.rstrip("/") + "/"):
            return False

    for allow in ALLOWED_PREFIXES:
        if resolved == allow or resolved.startswith(allow.rstrip("/") + "/"):
            return True

    # أي حاجة خارج المسموح ومش فـ المحظور الصريح => نرفضها بالدفو (deny by default)
    return False


def enforce_path(path: str, action: str = "access"):
    if not check_path_allowed(path):
        freeze_and_alert(path)
        raise SecurityViolation(f"🚫 محاولة {action} على مسار محمي: {path}")


def freeze_and_alert(path: str):
    """
    'يتفا direct / يتبلوك / يتجمد' — كيفما طلبت:
    نسجل الحادثة، نوقف أي عملية جارية مرتبطة، ونرفض بشكل قاطع.
    """
    msg = f"\n\033[41m\033[97m[SECURITY FREEZE] محاولة وصول لمسار محظور: {path} — تم إيقاف العملية.\033[0m\n"
    print(msg, file=sys.stderr)
    log_path = Path.home() / ".cowork" / "logs" / "security.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"BLOCKED ACCESS -> {path}\n")


def is_dangerous_command(cmd: str) -> bool:
    low = cmd.lower()
    return any(pat.lower() in low for pat in DANGEROUS_PATTERNS)


def confirm_dangerous(cmd: str) -> bool:
    """مربع أصفر [Y/n] قبل تنفيذ أي أمر خطير."""
    box = (
        "\n\033[43m\033[30m"
        f" ⚠  أمر محتمل الخطورة:  {cmd}\n"
        " تأكيد التنفيذ؟ [y/N] "
        "\033[0m"
    )
    answer = input(box).strip().lower()
    return answer == "y"
