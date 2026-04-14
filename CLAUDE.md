# Slovíčka

A static flashcard web app for learning English.
Each week, a teacher provides Czech–English word pairs. A Python build pipeline
turns them into a self-contained static site deployed on GitHub Pages.

## Architecture

- **Frontend:** Vanilla HTML/CSS/JS (no framework) — static site on GitHub Pages
- **Build pipeline:** Python scripts in `build/` — parse words, generate images, generate audio, assemble site
- **Image generation:** Replicate API with Google Imagen 3 model
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

## Image Generation Notes

Imagen 3 gotchas, learned the hard way:

- **Never use `child`/`children`/`kids`/`kawaii`** in templates or `image_prompt`s — the safety filter trips even on benign uses. Say `people`, `friends`, `person`.
- **Never put the target word in `image_prompt`** — the model renders it as hand-lettered text instead of depicting it. Describe the scene only.
- **Use concrete scenes** for abstract words (`two friends greeting on a sidewalk`, `a hand giving a thumbs-up`); the template handles the word reference.
- **Be explicit about colors** — "warm, natural" → brown sepia. The `merry` variant lists colors (sky blue, sunny yellow, fresh green, coral pink) for vivid output.
- **Test prompt changes via `generate_preview.py`** (strict abort). The production `generate_images.py` silently falls back to placeholders, only surfacing in a `WARNING:` summary.
- **`parse_words.py` reuses existing image filenames** via `preserve_existing_images()` — don't bypass it, or the random-suffix reshuffle orphans every previously generated webp.

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
