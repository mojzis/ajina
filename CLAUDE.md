# Slovíčka

A static flashcard web app for learning English.
Each week, a teacher provides Czech–English word pairs. A Python build pipeline
turns them into a self-contained static site deployed on GitHub Pages.

## Architecture

- **Frontend:** Vanilla HTML/CSS/JS (no framework) — static site on GitHub Pages
- **Build pipeline:** Python scripts in `build/` — parse words, generate images, generate audio, assemble site
- **Image generation:** Replicate API with SDXL-lineart model (reused from `../esl`)
- **Audio:** edge-tts (pre-generated MP3s)
- **Sibling project:** `../esl` has shared patterns — image generation, caching, project setup

## Dev Commands

Uses [poethepoet](https://poethepoet.naber.io/) as task runner:

```bash
poe lint                     # ruff check
poe format                   # ruff format --check
poe type                     # ty check
poe test                     # pytest
poe check                    # all of the above
```

## Dependencies

**Always use `uv add <package>` to add dependencies — never edit pyproject.toml manually for deps.**

```bash
uv add <package>             # add a runtime dependency
uv add --group dev <package> # add a dev dependency
```

## Build Pipeline

```bash
uv run python build/build_all.py \
  --week 2026-W14 \
  --title "Zvířata" \
  --title-en "Animals" \
  --input input/week-2026-W14.txt
```

## Conventions

- `pathlib.Path` everywhere, no string concatenation for paths
- Type hints on all functions
- Use `argparse` for CLI scripts
- All paths relative to project root

### Python Symbol Navigation — `tyf`

This project has `tyf` — a type-aware code search that gives LSP-quality
results by symbol name. Use `tyf` instead of grep/ripgrep for Python symbol lookups.

- `tyf show my_function` — definition + signature (add `-d` docs, `-r` refs, `-t` test refs, or `--all`)
- `tyf find MyClass` — find definition location
- `tyf refs my_function` — all usages (before refactoring)
- `tyf members TheirClass` — class public API
- `tyf list file.py` — file outline

All commands accept multiple symbols — batch to save tool calls.
Run `tyf <cmd> --help` for options.

Use grep for: string literals, config values, TODOs, non-Python files.
