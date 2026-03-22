# Prompt 01 — Project Setup

Use this as the first prompt for Claude Code to scaffold the project.

> **NOTE:** The ESL project (`../esl`) uses UV as package manager, ruff for
> linting/formatting, ty for type checking, and has proven patterns for project
> setup. Follow the same conventions here (pyproject.toml with UV, ruff config,
> etc.) instead of requirements.txt + pip.

---

## Prompt

Set up a new project called `slovicka` — a static flashcard web app for learning English, designed for people with mental disabilities.

Read `PROJECT.md` in this directory for the full context.

**Also study `../esl/pyproject.toml`** for project setup conventions — use UV as the package manager, ruff for linting/formatting, and ty for type checking, matching the ESL project's approach.

Create the following directory structure:

```
slovicka/
├── CLAUDE.md              # Claude Code project instructions (see below)
├── README.md              # Brief project description + how to run
├── pyproject.toml         # Project metadata & deps (UV, matching ../esl conventions)
├── build/
│   ├── parse_words.py     # Stub: parse input/*.txt → JSON
│   ├── generate_images.py # Stub: generate images for word list
│   ├── generate_audio.py  # Stub: generate TTS audio
│   ├── build_site.py      # Stub: assemble site/ from templates + data
│   ├── build_all.py       # Orchestrator: runs all steps in sequence
│   └── deploy.sh          # Stub: deploy site/ to gh-pages
├── input/
│   └── example.txt        # Example word list with 5 animal words
├── site/                  # Will contain generated output (gitignored except data/)
├── templates/
│   ├── index.html         # Empty placeholder
│   ├── style.css          # Empty placeholder
│   └── app.js             # Empty placeholder
└── .gitignore
```

For each build script, create a proper Python file with:
- Argument parsing (argparse)
- Clear docstring explaining what it does
- Stub implementation that prints what it would do
- Proper error handling structure

The `build_all.py` orchestrator should accept `--week`, `--title`, `--title-en` arguments and call each step in sequence.

The example word list should contain:
```
kočka, cat, ket
pes, dog, dog
ryba, fish, fiš
pták, bird, börd
strom, tree, tríí
```

The `.gitignore` should exclude `site/assets/` and `node_modules/` but keep `site/data/`.

The `README.md` should be brief and practical — setup instructions, how to add a new week, how to deploy.

### Dev tooling in `pyproject.toml`

Add these as dev dependencies (matching `../esl/pyproject.toml`):
- `ruff` — linting and formatting
- `ty` — type checking (new, fast type checker from the ruff team)

Add ruff and ty configuration sections in `pyproject.toml` (copy patterns from `../esl/pyproject.toml`).

### CLAUDE.md

Create a `CLAUDE.md` file at the project root with instructions for Claude Code.

It must include:
- Project description (what slovicka is, who it's for)
- How to run the build pipeline
- Dev commands: `uv run ruff check .`, `uv run ruff format .`, `uv run ty check`
- Note that `../esl` is a sibling project with shared patterns (image generation, etc.)
- Key architectural decisions (static site, vanilla JS, Python build pipeline)
- Any conventions: pathlib.Path everywhere, type hints on all functions, etc.
- **Dependencies: always use `uv add <package>` — never edit pyproject.toml manually for deps**
- Include the `tyf` section below
- Include the **Build Progress** checklist below (for autonomous workflow)

#### Build Progress checklist

Include this section in `CLAUDE.md` so the autonomous workflow can track status:

```
## Build Progress

- [x] Phase 1 — Project Setup (plans/PROMPT-01-setup.md)
- [ ] Phase 2 — Frontend Template (plans/PROMPT-02-frontend.md)
- [ ] Phase 3 — Build Pipeline (plans/PROMPT-03-build-pipeline.md)
- [ ] Phase 4 — Image Generation (plans/PROMPT-04-image-generation.md)
- [ ] Phase 5 — Polish & Deploy (plans/PROMPT-05-polish-deploy.md)
```

Mark Phase 1 as complete since you're executing it right now. The autonomous
workflow (see `plans/BUILD-WORKFLOW.md`) uses this checklist to determine
which phase to execute next.

### Python Symbol Navigation — `tyf`

Include this section verbatim in `CLAUDE.md`:

```
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
```

---

Do NOT build the actual functionality yet — just the skeleton with stubs. We'll implement each part separately.
