# 🤝 Cowork

**Autonomous local AI agent — 100% offline, powered by Ollama + qwen2.5:0.5b**

A Claude Code–inspired agentic CLI that plans, uses tools, remembers context via local RAG, and runs multiple sub-agents in parallel — entirely on your machine, with no internet required.

> Built as part of the [Zunexa](https://zunexa.vercel.app) project ecosystem.

---

## ✨ Features

- **Autonomous planning** — breaks big goals into sequential sub-tasks and adapts when a step fails.
- **Tool use** — shell commands, file read/write, extensible tool registry with Pydantic-validated schemas.
- **Local memory (RAG)** — short-term conversation buffer + long-term vector memory via ChromaDB, using local embeddings (`nomic-embed-text`).
- **Multi-agent orchestration** — run specialized agents (coder / tester / docs) concurrently.
- **Claude Code–style TUI** — colored thinking tree, status bar with context-window usage, interactive diff viewer, `[Y/n]` confirmation for risky commands.
- **Strict security model** — hard-coded root/system path protection (`/root`, `/etc`, `/boot`, `/sys`, `/dev`, ...); any access attempt is logged and blocked.
- **Structured output** — Ollama `format: "json"` + Pydantic validation ensures tool calls are always well-formed before execution.

---

## 🧠 Architecture

```
cowork/
├── main.py            # REPL entrypoint — type `cowork` to launch
├── agent.py            # Core autonomous loop (plan → act → observe → retry)
├── orchestrator.py      # Parallel multi-agent runner
├── memory.py            # Short-term buffer + ChromaDB long-term vector memory
├── tools.py             # Tool registry (shell, file I/O) + Pydantic schemas
├── security.py          # Root protection & dangerous-command guard
├── system_prompt.py     # Claude-style forced system prompt (few-shot JSON)
├── ollama_client.py      # Thin wrapper around the Ollama HTTP API
├── bootstrap.py          # First-launch ingestion of your local data into RAG
├── ui.py                # Rich-based terminal UI
└── install.sh            # One-shot installer
```

---

## 📦 Requirements

- Debian/Ubuntu (or any Linux) — tested on Debian 13 XFCE
- Python 3.11+
- [Ollama](https://ollama.com) installed locally
- ~11GB RAM recommended (works on low-end CPUs like i3-4005U with quantized models)

---

## 🚀 Installation

```bash
git clone https://github.com/<your-username>/cowork.git
cd cowork

# pull the local models
ollama pull qwen2.5:0.5b
ollama pull nomic-embed-text

# install
chmod +x install.sh
./install.sh

# make sure ~/.local/bin is in your PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## ▶️ Usage

```bash
cowork
```

On first launch, Cowork ingests your local data directory into its vector memory (configurable in `config.py` via `TRAIN_SOURCE_DIR`) — without ever touching system/root paths.

### Slash commands

| Command | Description |
|---|---|
| `/design` | Switch to Plan Mode (plan without executing) |
| `/multi <goal>` | Run coder / tester / docs agents in parallel |
| `/bug` | Report an issue in the current task |
| `/compact` | Compact short-term memory |
| `/exit` | Quit |

---

## 🔒 Security model

Cowork **refuses by default** on any path that isn't inside your home directory or `/tmp`. Access attempts on `/root`, `/etc`, `/boot`, `/sys`, `/proc`, `/dev`, `/bin`, `/lib`, `/sbin` are blocked and logged to `~/.cowork/logs/security.log`. Potentially destructive shell commands (`rm -rf`, `dd`, `mkfs`, `sudo`, ...) require explicit `[Y/n]` confirmation before execution.

---

## ⚙️ Configuration

Edit `config.py`:

```python
MODEL_NAME = "qwen2.5:0.5b"   # swap for a bigger local model if your hardware allows
NUM_CTX = 8192                 # lower to 4096 on constrained RAM
MAX_PARALLEL_AGENTS = 3
```

---

## 🗺️ Roadmap

- [ ] Web browsing tool (local headless browser)
- [ ] LoRA fine-tuning option (optional, for stronger hardware)
- [ ] Textual-based full-screen TUI
- [ ] Plugin system for custom tools

---

## 🔗 Related

This project is part of the **[Zunexa](https://zunexa.vercel.app)** ecosystem.

## 📄 License

MIT — see [LICENSE](LICENSE).
