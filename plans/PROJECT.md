# Slovíčka — English Flashcards for Assisted Learning

## What This Is

A static flashcard web app for people with mental disabilities who are learning English as part of a weekly course. Each week, a teacher provides a list of Czech–English word pairs. A build pipeline turns that list into a beautiful, self-contained static site deployed on GitHub Pages.

## Core Principles

1. **Simplicity over features.** No login, no progress tracking, no accounts. Open the page → see this week's words → tap a card → learn.
2. **Accessibility first.** Large touch targets, high contrast, no time pressure, clear audio, no complex gestures.
3. **Consistency.** Same layout, same interaction, same voice every time. Predictability builds confidence.
4. **Beauty that doesn't distract.** Lovely illustrations, warm colors, generous whitespace — but the design serves the learning, never competes with it.

---

## User Experience

### Landing Page

- A warm greeting / simple title
- Grid of cards showing this week's words — each card shows the **Czech word** + **illustration**
- Week selector at the bottom (dropdown or simple arrows) for revisiting past weeks
- Current week is always the default

### Card Detail (Fullscreen Overlay or Dedicated View)

**Czech side (shown first):**
- Large illustration (center)
- Czech word in large, clear type below
- Audio plays automatically after a short delay (~1s), saying the Czech word
- Clear "flip" button / tap anywhere to flip

**English side (revealed on tap):**
- Same illustration (smaller or at top, for continuity)
- English word in large type
- Phonetic pronunciation in Czech-friendly letters below (e.g., "ket" for "cat")
- Audio plays automatically, saying the English word
- "Back" / "Next" navigation

### Interaction Model

- **Tap to flip** (not timer-based). Users control the pace.
- **Tap to replay audio** on either side.
- **Swipe or arrow buttons** to move between cards.
- No scoring, no streaks, no gamification. Just calm learning.

---

## Data Format

Each week is a single JSON file: `data/week-YYYY-WNN.json`

```json
{
  "week_id": "2026-W13",
  "title": "Zvířata",
  "title_en": "Animals",
  "published": "2026-03-23",
  "words": [
    {
      "id": "cat",
      "czech": "kočka",
      "english": "cat",
      "pronunciation": "ket",
      "image": "cat.webp",
      "audio_cs": "cat_cs.mp3",
      "audio_en": "cat_en.mp3"
    }
  ]
}
```

There is also an index file: `data/index.json`

```json
{
  "current_week": "2026-W13",
  "weeks": [
    {
      "week_id": "2026-W13",
      "title": "Zvířata",
      "title_en": "Animals",
      "published": "2026-03-23",
      "word_count": 8
    }
  ]
}
```

---

## Architecture

```
Teacher sends word list (email / later: form)
        │
        ▼
┌─────────────────────────────────────────┐
│           BUILD PIPELINE (local)         │
│                                          │
│  1. Parse word list (CSV/text → JSON)    │
│  2. Generate images (image gen API)      │
│  3. Generate audio (edge-tts)            │
│  4. Build static HTML                    │
│  5. Deploy to GitHub Pages               │
└─────────────────────────────────────────┘
        │
        ▼
  GitHub Pages (static hosting)
        │
        ▼
  Users open the page on phone/tablet
```

### Directory Structure

```
slovicka/
├── README.md
├── build/                    # Build scripts
│   ├── parse_words.py        # Parse teacher's word list → JSON
│   ├── generate_images.py    # Call image gen API
│   ├── generate_audio.py     # Generate TTS audio files
│   ├── build_site.py         # Assemble final static site
│   └── deploy.sh             # Push to gh-pages branch
├── input/                    # Teacher's raw word lists
│   └── week-2026-W13.txt     # Simple format, see below
├── site/                     # Generated static site (output)
│   ├── index.html            # Main app (SPA-like)
│   ├── style.css
│   ├── app.js
│   ├── data/
│   │   ├── index.json
│   │   └── week-2026-W13.json
│   └── assets/
│       ├── images/
│       │   └── week-2026-W13/
│       │       ├── cat.webp
│       │       └── dog.webp
│       └── audio/
│           └── week-2026-W13/
│               ├── cat_cs.mp3
│               ├── cat_en.mp3
│               ├── dog_cs.mp3
│               └── dog_en.mp3
└── templates/                # HTML/CSS/JS source templates
    ├── index.html
    ├── style.css
    └── app.js
```

### Input Format (Teacher's Word List)

Simple text file, one word pair per line:

```
kočka, cat, ket
pes, dog, dog
dům, house, haus
strom, tree, tríí
```

Format: `czech, english, pronunciation`

If pronunciation is omitted, the build script should try to generate a reasonable Czech phonetic approximation (can be manual-reviewed).

---

## Relationship to ESL Project

The `../esl` project (ESL Worksheet Generator) shares several components that
should be reused rather than rebuilt:

| Component | ESL Location | Reuse Strategy |
|-----------|-------------|----------------|
| Image generation (Replicate API) | `esl/image_gen.py` | Port the API integration, prompt template, background removal |
| Image caching & lookup | `esl/image_lookup.py` | Port the caching pattern (filename convention, skip-existing) |
| Image resolution fallback | `esl/image_resolver.py` | Port the 3-tier fallback (cache → generate → placeholder SVG) |
| Project setup | `pyproject.toml` | Follow same conventions: UV, ruff, pyproject.toml |
| Linting/formatting | ruff config | Use same ruff setup |

Both projects share the same `REPLICATE_API_TOKEN` env var.

---

## Technical Decisions

### Audio: Pre-generated with edge-tts (not browser TTS)

**Why not browser `speechSynthesis`:**
- Czech voice availability is inconsistent across devices
- Voice quality varies wildly — some devices sound robotic
- Mobile Safari has known issues with auto-play of speech
- For users with disabilities, consistent experience is critical

**Approach:**
- Use `edge-tts` (free, MIT-licensed Python package) to generate MP3 files at build time
- Czech voice: `cs-CZ-VlastaNeural` (clear, warm female voice)
- English voice: `en-GB-SoniaNeural` or `en-US-JennyNeural` (clear, not too fast)
- Set speech rate to slightly slower than default (`--rate=-10%`)
- Audio files are small (~10-30KB per word), so total per week is negligible
- Fallback: if audio fails to load, show a "tap to hear" button that tries browser TTS

### Images: Generated via Replicate API (reuse from ESL project)

> **We already have a working image generation pipeline in `../esl`.**
> Reuse the Replicate API integration (`esl/image_gen.py`), background removal,
> and image caching (`esl/image_lookup.py`). Same `REPLICATE_API_TOKEN` env var.
> Model: `cuuupid/sdxl-lineart` — 512×512, 20 inference steps, guidance 9, K_EULER scheduler.

**Style prompt prefix (use consistently for all images):**
```
A lovely hand-drawn illustration in the style of a vintage natural history atlas.
Black ink contours with soft, warm watercolor fills. Clean white background.
Simple, charming, suitable for educational materials. Single subject, centered.
No text in the image.
Subject: [WORD]
```

- Generate at 512×512 via Replicate API with SDXL-lineart model
- Run background removal (flood-fill cleaning, same as ESL)
- Convert to WebP for smaller file size
- Cache generated images, skip existing on re-runs
- Store one set of images per week

### Frontend: Vanilla HTML/CSS/JS

**Why not React/Vue/etc:**
- Tiny app, no complex state
- Faster load times (critical on older devices these users may have)
- Easier to maintain by non-developers
- Static files = simple GitHub Pages deployment

**CSS approach:**
- CSS custom properties for theming
- CSS Grid for card layout
- CSS transitions for flip animation
- System font stack with a nice sans-serif fallback
- Mobile-first, works on phones and tablets

**JS approach:**
- Vanilla JS, no framework
- Fetch JSON data on load
- Simple state: current week, current card, flipped or not
- Audio via `<audio>` elements (preloaded)
- Touch events for swipe navigation

---

## Design Language

### Colors
- Background: warm cream/off-white (`#FFF8F0` or similar)
- Card background: white with subtle shadow
- Text: dark warm gray (`#2D2A26`), not pure black
- Accent: a soft teal or warm coral for interactive elements
- The cards themselves should feel like physical objects — rounded corners, subtle shadow

### Typography
- Primary: a rounded, friendly sans-serif (e.g., `Nunito`, `Quicksand`, or system default)
- Czech word: large (28-36px), bold
- English word: large (28-36px), bold
- Pronunciation: medium (20-24px), italic, slightly muted color
- Everything should be readable from arm's length on a phone

### Card Design
- Generous padding
- Illustration takes up ~60% of card height
- Flip animation: 3D card flip (CSS `transform: rotateY(180deg)`) with a gentle ease
- Audio indicator: small speaker icon, pulses when playing

### Layout
- Mobile-first grid: 2 columns on phone, 3 on tablet
- Card list items show: illustration + Czech word
- Detail view is fullscreen overlay with large card

---

## Accessibility Considerations

- All images have `alt` text (the Czech word on front, English on back)
- Audio controls are visible and tappable (not just autoplay)
- Touch targets minimum 48×48px
- Color contrast meets WCAG AA
- No animations that can't be paused
- `prefers-reduced-motion` respected
- Language attributes set correctly (`lang="cs"` / `lang="en"`)
- No reliance on color alone to convey information

---

## Weekly Workflow

1. Teacher sends word list via email
2. Save as `input/week-YYYY-WNN.txt`
3. Run: `python build/build_all.py --week 2026-W13 --title "Zvířata" --title-en "Animals"`
4. Review generated images (regenerate any that don't look right)
5. Review audio files (re-record manually if needed)
6. Run: `./build/deploy.sh`
7. Done — site is live

### Future: Teacher Self-Service

Later phase: a simple web form where the teacher can:
- Enter word pairs
- Preview generated cards
- Hit "publish"

This could be a simple admin page that commits to the repo via GitHub API, triggering a GitHub Action that runs the build pipeline.

---

## What's NOT in Scope (for now)

- User accounts / login
- Progress tracking / spaced repetition
- Multiple languages beyond CS→EN
- Offline mode / PWA (could add later)
- Teacher admin interface (later phase)
- Scoring or gamification of any kind
