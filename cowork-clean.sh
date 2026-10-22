#!/usr/bin/env bash
# مسح كاش Cowork بالكامل (vectordb + cache + logs + checkpoints)
set -e
COWORK_DIR="$HOME/.cowork"

echo "[*] مسح $COWORK_DIR/cache $COWORK_DIR/vectordb $COWORK_DIR/logs ..."
rm -rf "$COWORK_DIR/cache"/* "$COWORK_DIR/vectordb"/* "$COWORK_DIR/logs"/* 2>/dev/null || true
rm -f "$COWORK_DIR/.ingest_checkpoint.json" "$COWORK_DIR/.bootstrapped" "$COWORK_DIR/job_status.json"

echo "✅ تم مسح الكاش بالكامل."
