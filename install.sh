#!/usr/bin/env bash
# تثبيت Cowork على Debian 13 XFCE
set -e

INSTALL_DIR="$HOME/.cowork/app"
mkdir -p "$INSTALL_DIR"
cp -r ./*.py "$INSTALL_DIR"/

echo "[*] تثبيت الاعتماديات (بيئة افتراضية محلية)..."
python3 -m venv "$HOME/.cowork/venv"
source "$HOME/.cowork/venv/bin/activate"
pip install --upgrade pip -q
pip install -q rich requests pydantic chromadb

# أمر cowork فالـ PATH
BIN_PATH="$HOME/.local/bin/cowork"
mkdir -p "$HOME/.local/bin"
cat > "$BIN_PATH" <<EOF
#!/usr/bin/env bash
source "$HOME/.cowork/venv/bin/activate"
exec python3 "$INSTALL_DIR/main.py" "\$@"
EOF
chmod +x "$BIN_PATH"

# تسخين الموديل فـ الرام مسبقاً (keep_alive) لسرعة الإطلاق
if command -v ollama >/dev/null; then
  echo "[*] تسخين qwen2.5:0.5b فـ الذاكرة..."
  ollama run qwen2.5:0.5b "" --keepalive 60m >/dev/null 2>&1 || true
fi

echo "✅ تم التثبيت. تأكد أن \$HOME/.local/bin فـ الـ PATH، بعدها اكتب: cowork"
