# Prompt 02 — Frontend Template

Use this prompt after the project is scaffolded (Prompt 01).

---

## Prompt

Read `PROJECT.md` for full context. Now implement the frontend template — the HTML, CSS, and JS that make up the flashcard app.

The app is a static single-page app. All data comes from JSON files fetched at runtime. The template files live in `templates/` and will be copied to `site/` by the build script.

### What to build

**`templates/index.html`** — Single HTML file that is the entire app.
- Proper meta tags (viewport, charset, og tags)
- `lang="cs"` on the root, with `lang="en"` on English text elements
- Links to `style.css` and `app.js`
- Semantic structure:
  - Header with app title ("Slovíčka" or similar friendly name)
  - Week selector (simple dropdown)
  - Card grid container
  - Card detail overlay (hidden by default)
- Preload hints for the first few images

**`templates/style.css`** — All styling, mobile-first.

Design requirements (see PROJECT.md for full design language):
- Background: warm cream (`#FFF8F0`)
- Cards: white, rounded corners (16px), subtle box-shadow
- Typography: use Google Fonts `Nunito` (friendly, rounded). Fall back to system sans-serif.
- Czech words: 28-32px, bold, dark warm gray
- English words: 28-32px, bold
- Pronunciation: 20px, italic, muted color
- Card grid: 2 columns on mobile (<600px), 3 columns on tablet+
- Card items in grid: show illustration (square, fills card width) + Czech word below
- Card detail: fullscreen overlay with centered card, max-width 400px
- 3D flip animation using CSS transforms (rotateY). The card has a front and back face.
- Flip transition ~0.6s ease
- Smooth fade-in for overlay
- Speaker icon button for audio replay (minimum 48x48px tap target)
- Navigation arrows (prev/next) on detail view, 48px minimum
- All interactive elements have hover/active states
- `prefers-reduced-motion`: replace flip animation with simple crossfade
- Week selector: simple, unobtrusive, at the bottom of the page
- A subtle decorative element — maybe a thin watercolor-style border or small leaf/flower SVG accent near the title

Specific card flip implementation:
```css
/* The card container needs perspective */
.card-scene { perspective: 800px; }

/* The card itself flips */
.card-flipper {
  transition: transform 0.6s ease;
  transform-style: preserve-3d;
}
.card-flipper.flipped { transform: rotateY(180deg); }

/* Front and back are positioned absolutely, backface hidden */
.card-front, .card-back {
  backface-visibility: hidden;
  position: absolute;
  width: 100%;
  height: 100%;
}
.card-back { transform: rotateY(180deg); }
```

**`templates/app.js`** — All interaction logic, vanilla JS.

Functionality:
1. On load: fetch `data/index.json`, determine current week, fetch that week's data
2. Render card grid from word list
3. Card click → open detail overlay showing Czech side
4. After ~1 second delay, play Czech audio automatically
5. Tap card / tap "flip" button → flip to English side
6. After flip, play English audio automatically after ~0.5s
7. Tap speaker icon → replay current side's audio
8. Prev/Next arrows or swipe to navigate between words
9. Close button or back gesture to return to grid
10. Week selector change → fetch new week data, re-render grid

Audio handling:
- Use `<audio>` elements, created dynamically
- Preload audio for current card + next card
- If audio fails to load, try browser `speechSynthesis` as fallback
- If all fails, just show the text (no error shown to user)

Touch/swipe:
- Simple swipe detection (touchstart/touchend, >50px horizontal movement)
- Swipe left = next card, swipe right = previous card
- Don't interfere with scroll on the grid view

State management:
- Simple object: `{ currentWeek, words, currentCardIndex, isFlipped, isDetailOpen }`
- No URL routing needed, but could use hash (#detail/2) for back button support

Important:
- The app must work well on older Android phones and iPads
- No `localStorage` (not needed)
- All text content comes from JSON, nothing hardcoded
- Console.log for debugging is fine but no alerts/confirms
- Keyboard support: Escape to close, Left/Right arrows to navigate, Space to flip

### Test with mock data

Create a `site/data/` directory with mock data files so the template can be tested:

`site/data/index.json`:
```json
{
  "current_week": "2026-W13",
  "weeks": [
    { "week_id": "2026-W13", "title": "Zvířata", "title_en": "Animals", "published": "2026-03-23", "word_count": 5 },
    { "week_id": "2026-W12", "title": "Barvy", "title_en": "Colors", "published": "2026-03-16", "word_count": 6 }
  ]
}
```

`site/data/week-2026-W13.json` — with the 5 animal words from the example.

For images: use placeholder colored rectangles (solid color SVGs or a tiny placeholder image generator in the build script). For audio: the app should handle missing audio gracefully.

Copy the completed templates to `site/` so the app can be tested by opening `site/index.html` directly in a browser.

### Quality bar

This needs to feel warm, calm, and inviting. Think: a patient, kind teacher made this by hand. Not: a developer threw a framework at it. Every interaction should feel gentle. No jarring transitions, no aggressive colors, no tiny text.

The code should be clean and well-commented. Someone maintaining this who isn't a developer should be able to understand what's happening.
