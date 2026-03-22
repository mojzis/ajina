# Prompt 03 — Build Pipeline

Use this prompt after the frontend template is working (Prompt 02).

---

## Prompt

Read `PROJECT.md` for full context. Now implement the build pipeline that turns a teacher's word list into a deployable static site.

### `build/parse_words.py`

Parses the teacher's input file into structured JSON.

Input format (`input/week-YYYY-WNN.txt`):
```
kočka, cat, ket
pes, dog, dog
```

Each line: `czech, english, pronunciation`

The script should:
1. Read the input file
2. Clean whitespace, skip empty lines and lines starting with `#`
3. Generate a slug/id from the English word (lowercase, alphanumeric + hyphens)
4. Create the week JSON file at `site/data/week-{week_id}.json`
5. Update `site/data/index.json` (create if missing, add/update this week's entry, set as current)
6. Print a summary of what was parsed

Arguments:
- `--input` — path to the text file
- `--week` — week ID like `2026-W13`
- `--title` — Czech title for the week
- `--title-en` — English title for the week

Handle edge cases: duplicate words, special characters in Czech (ž, ř, č etc.), missing pronunciation column (leave empty, to be filled manually).

### `build/generate_audio.py`

Generates MP3 audio files for all words in a week using `edge-tts`.

For each word, generate two files:
- `site/assets/audio/week-{week_id}/{id}_cs.mp3` — Czech word
- `site/assets/audio/week-{week_id}/{id}_en.mp3` — English word

Configuration:
- Czech voice: `cs-CZ-VlastaNeural`
- English voice: `en-GB-SoniaNeural`
- Rate: `--rate=-15%` (slightly slower for clarity)
- Volume: `+0%` (default)

The script should:
1. Read the week JSON file
2. For each word, generate both audio files using `edge-tts`
3. Skip files that already exist (unless `--force` flag is passed)
4. Update the JSON with audio file paths
5. Print progress and any errors

Arguments:
- `--week` — which week to generate audio for
- `--force` — regenerate even if files exist
- `--voice-cs` — override Czech voice
- `--voice-en` — override English voice

Install edge-tts: `pip install edge-tts`

### `build/generate_images.py`

Generates illustrations for each word using the Replicate API.

> **NOTE:** The ESL project (`../esl`) already has a working image generation system.
> Study `../esl/esl/image_gen.py` and `../esl/esl/image_lookup.py` and reuse their
> patterns: Replicate API with SDXL-lineart model, background removal, caching.
> See `PROMPT-04-image-generation.md` for full details on the reuse strategy.

For the initial scaffold (this prompt), implement a **dual-mode** version:
1. Read the week JSON file
2. `--mode placeholder` (default): Generate a 512×512 SVG placeholder
   - Soft pastel background color (different per word, generated from hash of word)
   - The word centered in a handwriting-style font
   - Saved as `site/assets/images/week-{week_id}/{id}.webp`
3. `--mode api`: Use Replicate API (same approach as `../esl/esl/image_gen.py`)
   - Model: `cuuupid/sdxl-lineart` (512×512, 20 steps, guidance 9, K_EULER)
   - Background removal via flood-fill cleaning
   - Reads `REPLICATE_API_TOKEN` from env var
   - Caches generated images, skips existing unless `--force`

```python
STYLE_PREFIX = """A lovely hand-drawn illustration in the style of a vintage natural history atlas.
Black ink contours with soft, warm watercolor fills. Clean white background.
Simple, charming, suitable for educational materials for children.
Single subject, centered, no text in the image."""

prompt = f"{STYLE_PREFIX}\nSubject: {word['english']}"
```

4. Update the JSON with image paths

Arguments:
- `--week` — which week
- `--force` — regenerate
- `--mode` — `placeholder` (default) or `api`
- `--regenerate` — regenerate specific words only (e.g. `--regenerate cat,dog`)

### `build/build_site.py`

Assembles the final static site.

1. Copy `templates/index.html`, `templates/style.css`, `templates/app.js` → `site/`
2. Verify all referenced assets exist (images, audio)
3. Print a report: which words have complete assets, which are missing something
4. Optionally open `site/index.html` in browser for preview (`--preview` flag)

### `build/build_all.py`

Orchestrator that runs everything in sequence.

```
python build/build_all.py --week 2026-W13 --title "Zvířata" --title-en "Animals" --input input/week-2026-W13.txt
```

Steps:
1. Parse words
2. Generate images (placeholder by default)
3. Generate audio
4. Build site
5. Print summary with link to preview

Add a `--skip-images` and `--skip-audio` flag for quick iteration on the frontend.

### `build/deploy.sh`

Simple shell script that:
1. Checks that `site/` exists and has content
2. Uses `gh-pages` npm package or `git subtree push` to deploy `site/` to the `gh-pages` branch
3. Prints the GitHub Pages URL

### Quality expectations

- All scripts should have clear error messages
- Use `rich` or simple colored prints for terminal output (progress bars, tables)
- Each script should be runnable independently
- All paths should be relative to the project root
- Use `pathlib.Path` throughout, not string concatenation
- Type hints on all functions
