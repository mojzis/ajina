# Prompt 04 — Image Generation

Use this prompt when you're ready to connect real image generation (replacing the placeholder SVGs).

---

## Prompt

Read `PROJECT.md` for full context. Now implement the real image generation in `build/generate_images.py`.

### Image Style

All images must share a consistent visual style. This is the most important thing — the cards should feel like they come from the same illustrated book.

**Style brief:**
- Hand-drawn illustration style, like a vintage natural history atlas or a beloved children's encyclopedia
- Black ink outlines/contours, confident but not rigid
- Soft watercolor fills — warm, saturated but not garish
- Clean white or very light background (so it works on the white card)
- Single subject, centered, with a bit of breathing room
- Charming and warm, not clinical or cartoonish
- No text in the image whatsoever
- Suitable for adults with disabilities — not childish, but friendly and clear

**Prompt template:**
```
A hand-drawn illustration in the style of a vintage natural history atlas.
Black ink contours with soft watercolor fills in warm, natural colors.
Clean white background. Single centered subject. No text.
Charming and clear, suitable for an educational card.
Subject: a [ENGLISH_WORD]
```

For abstract concepts (colors, actions), adapt the subject:
- Colors: "a watercolor swatch of [COLOR]" or "a [COLOR] butterfly"
- Actions: "a person [DOING THE ACTION]" in the same style
- Household items: straightforward illustration

### Implementation

Update `generate_images.py` to:

1. Accept an `--api-key` argument or read from `NANOBANANA_API_KEY` env var (or whatever the image gen service requires — adapt as needed)
2. For each word:
   - Construct the prompt using the template above
   - Call the image generation API
   - Save the result as PNG, then convert to WebP using Pillow (`quality=85`)
   - Target size: 512×512px
3. Add a `--review` mode that generates images and opens them in a grid (simple HTML page) for manual review before committing
4. Add a `--regenerate cat,dog` flag to regenerate specific words only
5. Save the raw API prompt used for each image in a sidecar file (`{id}.prompt.txt`) for reproducibility

### Fallback

If the API is unavailable or fails:
- Log the error clearly
- Keep the placeholder SVG
- Mark the word as "needs image" in the build report

### Image Post-Processing

After generation:
- Convert to WebP (Pillow)
- Ensure dimensions are exactly 512×512 (crop/pad if needed)
- Optimize file size (target: under 100KB per image)
- Generate a tiny blurred placeholder (32×32, base64) for lazy loading in the frontend
