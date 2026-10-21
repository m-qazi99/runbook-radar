<p align="center"><a href="https://m-qazi99.github.io/runbook-radar/"><img src="docs/banner.svg" alt="Runbook Radar — interactive Python workspace by Muzammil Qazi" width="100%"></a></p>
<p align="center"><a href="https://m-qazi99.github.io/runbook-radar/"><strong>Launch live product ↗</strong></a> · <a href="docs/USER_GUIDE.md">User guide</a> · <a href="docs/API.md">API reference</a> · <a href="CONTRIBUTING.md">Contribute</a></p>
<p align="center"><img src="https://github.com/m-qazi99/runbook-radar/actions/workflows/tests.yml/badge.svg" alt="Python checks"><img src="https://img.shields.io/badge/version-2.1.0-b78b42" alt="Version 2.1.0"><img src="https://img.shields.io/badge/Python-3.11%2B-557465" alt="Python 3.11+"><img src="https://img.shields.io/badge/license-MIT-9a7c45" alt="MIT license"></p>

# Runbook Radar

Retrieve source passages from Markdown and compare BM25 with TF-IDF. An independent, open-source Python application by **[Muzammil Qazi](https://m-qazi99.github.io/profile/)**, with a browser workspace, native CLI, local API, synthetic examples and automated tests.

## What's new in 2.1

**Review Desk turns computed evidence into an inspectable handoff.** Evaluation label coverage, top-K misses, no-match guidance, and small-sample warnings. Filter priorities, check what you inspected, and export a Markdown handoff. The checks remain in memory and reset with each new experiment. No inputs are changed and no operational actions are executed.

[Release notes](CHANGELOG.md) · [Architecture](docs/ARCHITECTURE.md) · [Contributing](CONTRIBUTING.md) · [Project comparison](https://m-qazi99.github.io/project-guide/)

<a href="https://m-qazi99.github.io/runbook-radar/"><img src="docs/studio-preview.jpg" alt="Runbook Radar synthetic investigation workspace; version 2.1 adds Review Desk below the workspace" width="100%"></a>

## Try a complete workflow

Run the storage query → inspect term contributions → compare algorithms → inspect labeled evaluation → open Review desk → export the handoff.

The first screen is explicitly labeled **synthetic preview**. Choose **Run experiment** to compute your inputs using Python. The runtime downloads on first use; there is no analysis server or account.

## What the code does

Markdown headings delimit documents. Adjustable word windows and overlap create source-cited chunks. BM25 (k₁=1.5, b=0.75) and log TF-IDF cosine similarity rank the same collection. Per-term score contributions expose the ranking. Labeled questions produce mean reciprocal rank and Hit@K for each algorithm.

The new `src/review.py` derives deterministic priorities from the result, then adds `review-handoff.md` and `review-priorities.json`. JavaScript renders these Python findings; it does not reimplement the analytical rules.

## Run locally

Python 3.11+; no third-party Python packages required.

```bash
git clone https://github.com/m-qazi99/runbook-radar.git
cd runbook-radar
python server.py
```

Open http://127.0.0.1:8000. The UI uses the same browser worker as the public product; the local API runs native Python.

```bash
# Native Python, no browser runtime required
python src/cli.py < examples/studio.json

# Tests and native/browser source parity
python -m unittest discover -s tests -v
python scripts/check_site.py

# Regenerate the labeled preview after changing Python
python scripts/build_preview.py
```

See [API examples and request fields](docs/API.md). The legacy request in `examples/sample.json` remains supported; `workspace: "studio"` selects the advanced workspace.

## Repository map

| Path | Responsibility |
|---|---|
| `src/engine.py` | Stable request routing; preserves the original API |
| `src/lab.py` | Project-specific analytical engine |
| `src/review.py` | Deterministic priorities and handoff artifacts |
| `src/cli.py`, `server.py` | Native command line and loopback HTTP API |
| `docs/` | GitHub Pages app, pinned worker runtime and Python copies |
| `docs/review-desk.js` | Priority filters, inspection checklist and handoff export |
| `examples/` | Synthetic input fixtures |
| `tests/` | Engine, review-policy and regression tests |
| `scripts/` | Preview generation and deployment parity checks |

## Scope and limitations

Lexical search is not a generative assistant. It has no LLM, embeddings, or external API. Scores are not calibrated confidence. MRR uses the first chunk from the expected document; a tiny synthetic evaluation set is not a benchmark claim.

Inputs remain in the active tab. Initial runtime files come from jsDelivr and fonts from Google Fonts; no input is sent to these services. Inputs and snapshots are not automatically persisted. Exported experiments include their input; review before sharing. File contents are limited to 2 MB and CSV datasets to 10,000 rows.

Review priorities are deterministic prompts, not an LLM diagnosis. Checking every item does not certify correctness, privacy, safety or production readiness. The reviewed handoff records the visitor's checklist state; it is not an independent approval.

## Open-source participation

Start with [CONTRIBUTING.md](CONTRIBUTING.md), the [development guide](docs/DEVELOPMENT.md), and [roadmap](ROADMAP.md). Report reproducible bugs using synthetic inputs. Changes should include relevant policy-boundary tests and keep browser/native Python copies aligned. [MIT license](LICENSE); [security reporting](SECURITY.md).

**Technical areas:** BM25, TF-IDF cosine similarity, lexical retrieval, Markdown runbooks, MRR, Hit@K, source passages, Pyodide, WebAssembly, Web Workers, accessible UI, Python CLI, local HTTP API, test-driven maintenance.

Built with Codex assistance as independent portfolio work. Public examples do not establish employer deployment, client outcomes or production adoption.

[Live product](https://m-qazi99.github.io/runbook-radar/) · [Portfolio](https://m-qazi99.github.io/) · [All projects](https://m-qazi99.github.io/projects/) · [Contact](https://m-qazi99.github.io/contact/)
