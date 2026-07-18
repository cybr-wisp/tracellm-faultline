# tracellm-faultline

**An evaluation framework for measuring how reliably tool-using LLM agents detect and recover from corrupted tool outputs.**

Part of the [TraceLLM](https://github.com/cybr-wisp) project.

---

## Research question

> How reliably can tool-using LLM agents recover after receiving corrupted tool outputs, and what reliability–cost trade-offs are created by retry, critic, and verifier strategies?

## What this does

tracellm-faultline stress-tests tool-using LLM agents under controlled failure conditions. It injects corrupted outputs — malformed data, plausible but incorrect values, explicit errors, and missing fields — into synthetic tool environments, then measures whether agents detect the fault, recover correctly, or silently propagate bad information.

It compares four recovery strategies (baseline, retry, critic, and verifier) across multiple model providers, capturing full execution traces, cost breakdowns, and statistical reliability metrics for every run.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    CLI / API                         │
├──────────┬──────────┬───────────┬───────────────────┤
│ Configs  │  Runner  │  Tracing  │     Analysis      │
│  YAML    │  async   │  events   │  metrics, stats   │
├──────────┴────┬─────┴───────────┴───────────────────┤
│   Providers   │   Tools        │   Corruption       │
│  OpenAI       │   synthetic    │   fault injection   │
│  Ollama       │   sandbox      │   4 modes          │
│  Fake         │                │                    │
├───────────────┴────────────────┴────────────────────┤
│                   Storage (SQLite / Postgres)        │
├─────────────────────────────────────────────────────┤
│                   Dashboard (React + Vite)           │
└─────────────────────────────────────────────────────┘
```

## Installation

```bash
# Clone
git clone https://github.com/cybr-wisp/tracellm-faultline.git
cd tracellm-faultline

# Install with uv
uv sync

# Verify
uv run faultline --help
```

### Docker (full stack)

```bash
cp .env.example .env
docker compose up --build
```

## Usage

```bash
# List available tasks and providers
uv run faultline inspect

# Run an experiment
uv run faultline run configs/main-experiment.yaml

# Resume an interrupted experiment
uv run faultline run configs/main-experiment.yaml --resume

# Analyze results
uv run faultline analyze <experiment-id>

# Export traces
uv run faultline export <experiment-id> --format jsonl

# Replay a stored trajectory
uv run faultline replay <run-id>

# Perform a fresh model rerun
uv run faultline rerun <run-id>

# Launch API backend
uv run fastapi dev src/faultline/api/main.py
```

## Quality checks

```bash
uv run pytest
uv run mypy src
uv run ruff check .
uv run ruff format --check .
```

## Experiment design

- **12–20 synthetic tasks** across three domains: order support, scheduling, structured data analysis
- **4 corruption conditions:** clean output, explicit error, malformed/incomplete, plausible but incorrect
- **4 agent strategies:** baseline, bounded retry, critic, verifier
- **2 model sources:** one API model (OpenAI), one local model (Ollama)
- **5 repeated trials** per configuration
- **Primary metrics:** success, recovery, tool correctness, consistency, latency, token cost

## Project status

🚧 **In active development** — see [ROADMAP.md](ROADMAP.md) for milestones.

## License

[MIT](LICENSE)
