# smartpull ⚡

[![CI](https://github.com/punvesh/smartpull/actions/workflows/ci.yml/badge.svg)](https://github.com/punvesh/smartpull/actions)
[![PyPI](https://img.shields.io/pypi/v/smartpull?label=PyPI&cacheSeconds=60)](https://pypi.org/project/smartpull/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](Dockerfile)

> **Stop guessing which LLM fits your GPU — SmartPull picks the best model automatically.**

SmartPull profiles your GPU in real-time and recommends the best Ollama model, quantization, and context window — so you get zero VRAM crashes and maximum performance on any hardware.

---

## 🎥 Demo

[![Demo](https://asciinema.org/a/REPLACE_ME.svg)](https://asciinema.org/a/REPLACE_ME)

> Record with `asciinema rec demo.cast` → upload with `asciinema upload demo.cast` → replace `REPLACE_ME` with your ID.

---

## 😫 The Problem

Running local LLMs is frustrating:

- Models crash mid-session due to VRAM overflow
- No guidance on which quantization fits your GPU
- Trial and error wastes 30+ minutes every time a new model drops
- Wrong context window = performance degradation or OOM errors

---

## ✅ The Solution

SmartPull automatically:

- Detects your GPU and real-time free VRAM
- Applies a 15% safety buffer to prevent Windows DWM swap
- Recommends the best model + quantization for your exact hardware
- Expands your context window using leftover VRAM headroom
- Generates a ready-to-use Ollama Modelfile in one command

---

## ⚡ Quickstart

```bash
pip install smartpull
smartpull build
```

Then copy and run the 3 ollama commands SmartPull prints. Done.

---

## 📟 Sample Output

```
PS C:\Users\you> smartpull build

⚙️  Running SmartPull analysis...

==================================================
  smartpull — Final Recommendation
==================================================
  GPU              : NVIDIA GeForce RTX 3050 Ti Laptop GPU
  Total VRAM       : 4.0 GB
  Usable VRAM      : 3.29 GB (after 15% buffer)

  ✅ Model          : qwen2.5-coder:3b
  ✅ Quantization   : Q4_K_S
  ✅ VRAM needed    : 2.54 GB
  ✅ Context window : 14,336 tokens  (expanded from 8,192)
  ✅ Headroom       : 768 MB
  ✅ Swap risk      : LOW
  ✅ ELO (approx)   : 1290

  Note: Strong coding model. Best quality in the 3-4.5GB window.
==================================================

📝 Generating Modelfile...
✅ Modelfile written to: C:\Users\you\Modelfile

==================================================
  smartpull — Run These Commands
==================================================

  # 1. Pull the model
  ollama pull qwen2.5-coder:3b

  # 2. Create optimized build
  ollama create smartpull-qwen2.5-coder-3b -f C:\Users\you\Modelfile

  # 3. Run it
  ollama run smartpull-qwen2.5-coder-3b

==================================================
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai) installed and running
- NVIDIA GPU with drivers installed

### Install

```bash
pip install smartpull
```

### Install from source

```bash
git clone https://github.com/punvesh/smartpull.git
cd smartpull
pip install -e ".[dev]"
```

### Full user flow

```
pip install smartpull
       ↓
smartpull build
       ↓
copy 3 ollama commands
       ↓
model running in under 5 mins
```

1. `smartpull build` — scans GPU, recommends model, writes Modelfile
2. `ollama pull <model>` — downloads the recommended model (~1–2 GB, one time)
3. `ollama create smartpull-<model> -f ./Modelfile` — creates optimized build
4. `ollama run smartpull-<model>` — start chatting

---

## 🖥️ Usage

| Command | Description |
|---|---|
| `smartpull scan` | Scan your GPU and print real-time hardware profile |
| `smartpull recommend` | Recommend the best model for your current usable VRAM |
| `smartpull build` | Generate a Modelfile and print the recommended Ollama commands |
| `smartpull matrix` | Print the full model-quantization reference matrix |

---

## ⚙️ How SmartPull Works

```
nvidia-smi
    ↓
Real-time free VRAM (not total)
    ↓
15% safety buffer applied
    ↓
Model matrix lookup (VRAM → model + quant)
    ↓
MoE active parameter check
    ↓
Dynamic context window scaling
    ↓
Jinja2 Modelfile generation
    ↓
ollama create → run
```

1. Queries `nvidia-smi` for current GPU memory and driver data
2. Converts raw VRAM into safe usable VRAM after 15% buffer
3. Matches usable VRAM to best model + quant in the SmartPull matrix
4. Adjusts for MoE active parameter behavior where needed
5. Expands context window when extra headroom is available
6. Generates an Ollama-compatible `Modelfile`

---

## 📊 Recommended Model Matrix

| Usable VRAM | Model | Quant | Safe CTX | Notes |
|---|---|---|---|---|
| < 1.8 GB | `gemma2:2b` | IQ4_XS | 2,048 | Lightweight local assistant |
| 1.8–2.8 GB | `gemma4:e2b` | IQ4_XS | 4,096 | Best sub-3GB balance for code |
| 2.8–4.5 GB | `qwen2.5-coder:3b` | Q4_K_S | 8,192 | Strong coding performance |
| 4.5–6 GB | `qwen2.5-coder:7b` | Q4_K_S | 16,384 | High context for larger workloads |
| 6–9 GB | `llama3.1:8b` | Q5_K_M | 32,768 | Balanced code + general tasks |
| 9 GB+ | `qwen2.5-coder:14b` | Q5_K_M | 32,768 | Premium local model experience |

---

## 📈 Performance

Benchmarked on **RTX 3050 Ti Laptop GPU (4 GB VRAM)** running `qwen2.5-coder:3b`:

| Metric | Result |
|---|---|
| VRAM usage | 2,953 / 4,096 MB — stable, zero drift |
| GPU utilization | 88–90% during inference |
| CPU swap | None — all layers in VRAM |
| Context window | 14,336 tokens (expanded by SmartPull) |
| Output quality | Production-grade code with type hints + docstrings |

**Live nvidia-smi during active inference:**

```
# gpu    fb      sm    mem
    0   2953MB   88%   48%   ← generating response
    0   2953MB   90%   50%   ← generating response
    0   2953MB    0%    0%   ← response complete, idle
```

VRAM locked solid at 2,953 MB throughout. No swap. No crashes.

---

## 🐳 Docker

```bash
docker build -t smartpull .
docker run --gpus all smartpull recommend
```

---

## 🛠️ Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
black .
flake8 .
```

**Project layout:**

```
smartpull/
├── hardware.py        ← nvidia-smi scraper
├── matrix.py          ← model matrix lookup
├── smartpull.py       ← core smart pull logic
├── modelfile_gen.py   ← Jinja2 Modelfile generator
├── cli.py             ← Click CLI
├── tests/             ← pytest unit tests
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

---

## 🔁 Release & CI

SmartPull uses GitHub Actions for:

- Formatting and lint checks (`black`, `flake8`)
- Multi-version test coverage (Python 3.10, 3.11, 3.12)
- Release-triggered PyPI publishing

When a `v*` tag is pushed, the publish workflow builds and uploads the package automatically.

---

## 🗺️ Roadmap

- [x] NVIDIA GPU support
- [x] Ollama Modelfile generation
- [x] MoE model awareness
- [x] Dynamic context window scaling
- [x] PyPI package
- [x] Docker support
- [x] GitHub Actions CI/CD
- [ ] Apple Silicon (MLX) support
- [ ] AMD ROCm support
- [ ] Claude Code bridge (auto-set `ANTHROPIC_BASE_URL`)
- [ ] Interactive model picker TUI
- [ ] Auto model matrix updates from remote JSON

---

## 🤝 Contributing

Contributions are welcome. If you want to add support for new hardware, extend the model matrix, or improve the CLI experience, please open a PR.

**Recommended process:**

1. Fork the repository
2. Create a feature branch
3. Run tests locally
4. Submit a PR with a clear description

---

## 📝 Known Notes

- Ollama may pull `Q4_K_M` by default instead of `Q4_K_S` — SmartPull's ctx and GPU settings still apply correctly either way
- Windows users: if `smartpull` is not recognized after install, add `C:\Users\<you>\AppData\Roaming\Python\Python3xx\Scripts` to your PATH
- `nvidia-smi` must be accessible — requires NVIDIA drivers installed

---

⭐ If SmartPull saves you time, please star the repo — it helps others find it!

---

## License

MIT © [Punvesh](https://github.com/punvesh)
