# Weekly Workflow — Quick Reference

Keep this handy. This is the 5-minute process to publish a new week of flashcards.

---

## 1. Get the word list from the teacher

She sends something like:
```
kočka, cat, ket
pes, dog, dog
```

Save it as: `input/week-2026-W14.txt`

(Use the ISO week number — check at https://www.epochconverter.com/weeks/)

## 2. Run the build

```bash
cd slovicka

python build/build_all.py \
  --week 2026-W14 \
  --title "Zvířata" \
  --title-en "Animals" \
  --input input/week-2026-W14.txt
```

This will:
- Parse the word list
- Generate placeholder images (or real ones if API is configured)
- Generate audio files
- Assemble the site

## 3. Review

Open `site/index.html` in your browser. Check:
- Do all cards show?
- Does audio play?
- Do images look right?

To regenerate a specific image:
```bash
python build/generate_images.py --week 2026-W14 --regenerate cat,dog
```

To regenerate audio:
```bash
python build/generate_audio.py --week 2026-W14 --force
```

## 4. Deploy

```bash
./build/deploy.sh
```

Done. The site is live.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Audio sounds weird | Try a different voice: `--voice-en en-US-JennyNeural` |
| Image doesn't match the word | Re-run with `--regenerate word-id` |
| Czech characters broken | Make sure the input file is UTF-8 |
| Edge-tts fails | Check internet connection; `pip install --upgrade edge-tts` |
| Site won't deploy | Check git remote is set: `git remote -v` |

---

## Pronunciation Guide for Teacher

When the teacher writes pronunciation, she should use Czech letters to approximate the English sound:

| English | Pronunciation | Notes |
|---------|--------------|-------|
| cat | ket | |
| dog | dog | |
| three | thrí | "th" can stay as "th" — the students know it's a special sound |
| fish | fiš | |
| house | haus | |
| bird | börd | or "bérd" — whatever sounds closest |
| chair | čér | |
| water | votr | |

This doesn't need to be IPA-perfect. It's a memory aid in letters they can read.
