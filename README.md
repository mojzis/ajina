# Slovíčka

A static flashcard web app for learning English as part of a weekly course.

## Setup

```bash
uv sync
```

## Add a new week

1. Save the teacher's word list as `input/week-YYYY-WNN.txt`:
   ```
   kočka, cat, ket
   pes, dog, dog
   ```

2. Run the build:
   ```bash
   uv run python build/build_all.py \
     --week 2026-W14 \
     --title "Zvířata" \
     --title-en "Animals" \
     --input input/week-2026-W14.txt
   ```

3. Preview by opening `site/index.html` in a browser.

4. Deploy:
   ```bash
   ./build/deploy.sh
   ```

## Dev

```bash
uv run ruff check .      # lint
uv run ruff format .     # format
uv run ty check          # type check
```
