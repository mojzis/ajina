# Prompt 01 — Project Setup

Use this as the first prompt for Claude Code to scaffold the project.

---

## Prompt

Set up a new project called `slovicka` — a static flashcard web app for learning English, designed for people with mental disabilities.

Read `PROJECT.md` in this directory for the full context.

Create the following directory structure:

```
slovicka/
├── README.md              # Brief project description + how to run
├── requirements.txt       # Python dependencies (edge-tts, Pillow, etc.)
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

Do NOT build the actual functionality yet — just the skeleton with stubs. We'll implement each part separately.
