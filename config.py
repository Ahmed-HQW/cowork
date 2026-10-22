"""
Cowork - إعدادات النظام
========================
"""
import os
from pathlib import Path

# ====== Ollama ======
OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "qwen2.5:0.5b"
EMBED_MODEL = "nomic-embed-text"   # لازم تدير: ollama pull nomic-embed-text
NUM_CTX = 2048                      # i3-4005U ضعيف — 2048 كافي وأسرع بزاف من 8192
TEMPERATURE = 0.3
NUM_THREAD = 2                       # i3-4005U عندو 2 core/4 threads — نخلو core واحد حر للنظام

# ====== المسارات ======
HOME = Path.home()                                  # مثلا /home/ahmed
COWORK_DIR = HOME / ".cowork"                        # كلشي ديال الأداة هنا
CACHE_DIR = COWORK_DIR / "cache"
DB_DIR = COWORK_DIR / "vectordb"
MEMORY_DIR = COWORK_DIR / "memory"
LOG_DIR = COWORK_DIR / "logs"
TRAIN_SOURCE_DIR = HOME / "zunexa-data"               # مصدر الـ fine-tune الأولاني

for d in (COWORK_DIR, CACHE_DIR, DB_DIR, MEMORY_DIR, LOG_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ====== حماية الـ Root (غير قابلة للتعطيل) ======
FORBIDDEN_PREFIXES = [
    "/root", "/etc", "/boot", "/sys", "/proc", "/dev",
    "/var/lib", "/usr/lib", "/lib", "/lib64", "/sbin", "/bin",
]
# المسموح بيه فقط: دار المستخدم + /tmp
ALLOWED_PREFIXES = [str(HOME), "/tmp"]

# ====== أوامر خطيرة تحتاج تأكيد [Y/n] ======
DANGEROUS_PATTERNS = [
    "rm -rf", "rm -r", "mkfs", "dd if=", ":(){ :|:& };:",
    "chmod -R 777 /", "chown -R", "> /dev/sda", "shutdown",
    "reboot", "kill -9 1", "systemctl stop", "systemctl disable",
    "passwd", "userdel", "deluser", "sudo", "su -",
]

MAX_PARALLEL_AGENTS = 3   # عدد الـ sub-agents اللي يخدمو فنفس الوقت (مقيّد بالـ i3/11GB)
