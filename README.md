# smartpull ⚡

[![CI](https://github.com/punvesh/smartpull/actions/workflows/ci.yml/badge.svg)](https://github.com/punvesh/smartpull/actions)
[![PyPI](https://img.shields.io/pypi/v/smartpull)](https://pypi.org/project/smartpull/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](Dockerfile)

> **SmartPull automatically selects the best Ollama model for your GPU, quantization, and VRAM — so you never waste time guessing.**

---

## Why SmartPull?

Local model runtimes like Ollama and LM Studio are fantastic — until your GPU runs out of memory.
SmartPull solves that problem by turning real-time VRAM data into a safe, battle-tested Ollama model recommendation.

- No more guessing which quant works for your GPU
- No more swap-induced stalls
- No more manual model tuning for every new card

SmartPull is ideal for:

- developers using low-end GPUs
- engineers optimizing local coding assistants
- anyone running Ollama on a laptop or desktop with limited VRAM

---

## Quickstart

```bash
pip install smartpull
smartpull build
```

Then follow the generated Ollama commands.

### Sample output

```bash
🔍 Scanning hardware...
  GPU     : NVIDIA GeForce RTX 3050 Ti Laptop GPU
  Driver  : 566.07
  OS      : Windows
  VRAM    : 4.0 GB total
  Used    : 0.0 GB (OS + apps)
  Free    : 3.9 GB
  Buffer  : 594 MB (15% safety)
  Usable  : 3.3 GB ✅

✅ Model          : qwen2.5-coder:3b
✅ Quantization   : Q4_K_S
✅ VRAM needed    : 2.54 GB
✅ Context window : 14,336 tokens
✅ Headroom       : 768 MB
✅ Swap risk      : LOW

📝 Generating Modelfile...
✅ Modelfile written to: D:\smartpull\Modelfile

# 1. Pull the model
ollama pull qwen2.5-coder:3b

# 2. Create optimized build
ollama create smartpull-qwen2.5-coder-3b -f D:\smartpull\Modelfile

# 3. Run it
ollama run smartpull-qwen2-coder-3b
```

---

## Install

Install from PyPI:

```bash
pip install smartpull
```

Install from source:

```bash
git clone https://github.com/punvesh/smartpull.git
cd smartpull
pip install -e ".[dev]"
```

---

## Usage

| Command | Description |
|---|---|
| `smartpull scan` | Scan your GPU and print the real-time hardware profile |
| `smartpull recommend` | Recommend the best model for your current usable VRAM |
| `smartpull build` | Generate a Modelfile and print the recommended Ollama commands |
| `smartpull matrix` | Print the full model-quantization reference matrix |

---

## How SmartPull Works

1. Query `nvidia-smi` for current GPU memory and driver data
2. Convert raw VRAM into safe usable VRAM after a 15% buffer
3. Match usable VRAM to the best model + quant in the SmartPull matrix
4. Adjust for MoE active parameter behavior where needed
5. Expand the context window when extra headroom is available
6. Generate an Ollama-compatible `Modelfile`

---

## Recommended Model Matrix

| Usable VRAM | Model | Quant | Safe CTX | Notes |
|---|---|---|---|---|
| < 1.8 GB | `gemma2:2b` | `IQ4_XS` | 2,048 | Lightweight local assistant |
| 1.8–2.8 GB | `gemma4:e2b` | `IQ4_XS` | 4,096 | Best sub-3GB balance for code |
| 2.8–4.5 GB | `qwen2.5-coder:3b` | `Q4_K_S` | 8,192 | Strong coding performance |
| 4.5–6 GB | `qwen2.5-coder:7b` | `Q4_K_S` | 16,384 | High context for larger workloads |
| 6–9 GB | `llama3.1:8b` | `Q5_K_M` | 32,768 | Balanced code + general tasks |
| 9 GB+ | `qwen2.5-coder:14b` | `Q5_K_M` | 32,768 | Premium local model experience |

---

## Docker

Build the image:

```bash
docker build -t smartpull .
```

Run recommendation with GPU access:

```bash
docker run --gpus all smartpull recommend
```

---

## Development

Set up the repository for local development:

```bash
pip install -e ".[dev]"
pytest tests/ -v
black .
flake8 .
```

Project layout:

- `smartpull/` — core package modules
- `tests/` — unit test coverage
- `pyproject.toml` — package metadata and tooling
- `README.md` — project overview and docs

---

## Release & CI

SmartPull includes GitHub Actions for:

- formatting and lint checks
- multi-version test coverage
- release-triggered PyPI publishing

When a `v*` tag is pushed, the publish workflow builds and uploads the package automatically.

---

## Contributing

Contributions are welcome. If you want to add support for new hardware, extend the model matrix, or improve the CLI experience, please open a PR.

### Recommended process

1. Fork the repository
2. Create a feature branch
3. Run tests locally
4. Submit a PR with a clear description

---

## License

MIT © [Punvesh](https://github.com/punvesh)
