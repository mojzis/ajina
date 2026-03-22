# Prompt 05 — Polish & Deploy

Use this prompt after everything is working to add final polish and set up deployment.

---

## Prompt

Read `PROJECT.md` for full context. The app is functionally complete. Now let's polish it and set up deployment.

### Frontend Polish

Review and improve the frontend for these specific scenarios:

1. **First visit experience**: When a user opens the page for the first time, it should feel welcoming. Consider a very brief, friendly intro line in Czech like "Klikni na kartičku a uč se anglicky!" (Click a card and learn English!) — but only on the first viewing of each week, and dismissable.

2. **Empty states**: What happens if JSON fails to load? Show a friendly message in Czech, not a blank page or error. Something like "Něco se pokazilo. Zkus to znovu." with a retry button.

3. **Loading**: Add a gentle loading state (maybe the cards fade in one by one with a short stagger, not all at once).

4. **Audio feedback**: When audio is playing, the speaker icon should pulse gently. When audio finishes, subtle visual confirmation.

5. **Card navigation**: After flipping to the English side and hearing the word, make it easy to go to the next card. Maybe a gentle "next" prompt appears after a few seconds.

6. **Revisiting cards**: In the grid view, maybe show a subtle visual difference for cards that have been viewed in this session (very light, not gamification — just a small dot or slight color shift).

7. **Week transitions**: When switching weeks, cards should fade out and new ones fade in — not a jarring replace.

### Performance

1. Lazy load images: only load images visible in viewport + 1 row ahead
2. Preload audio for the first 2 cards, then load on demand
3. Use the tiny base64 blur placeholders while images load
4. Total page weight for a 10-word week should be under 2MB
5. Test on throttled 3G connection — should be usable within 5 seconds

### GitHub Pages Deployment

> **NOTE:** The ESL project (`../esl`) has a working GitHub Actions CI/CD pipeline
> (`.github/workflows/test.yml`) and Docker deployment (`Dockerfile`, `deploy.sh`).
> Reference those for patterns, though this project's deployment is simpler (static site).

Set up the repo for GitHub Pages:

1. Create a `deploy.sh` script that:
   - Builds the site into `site/`
   - Creates/updates the `gh-pages` branch with just the `site/` contents
   - Pushes to origin
   - Prints the live URL

2. Add a simple GitHub Action (`.github/workflows/deploy.yml`) that:
   - Triggers on push to `main` (only when `site/data/` changes)
   - Deploys `site/` to GitHub Pages
   - This is just for convenience — manual deploy via script is the primary method

3. Make sure `site/` has a proper `CNAME` file if a custom domain is needed (leave as placeholder comment for now)

### Testing Checklist

Create a `TESTING.md` file with a manual testing checklist:

- [ ] Page loads on Chrome mobile
- [ ] Page loads on Safari iOS
- [ ] Page loads on older Android (Chrome 90+)
- [ ] Card grid shows all words with images
- [ ] Tapping a card opens detail view
- [ ] Czech audio plays automatically
- [ ] Tapping card/flip button flips to English side
- [ ] English audio plays after flip
- [ ] Speaker icon replays audio
- [ ] Swipe left/right navigates between cards
- [ ] Arrow keys work on desktop
- [ ] Escape closes detail view
- [ ] Week selector loads different weeks
- [ ] Back to grid from detail works
- [ ] Missing audio doesn't break anything
- [ ] Missing image shows placeholder gracefully
- [ ] Works in airplane mode after initial load
- [ ] Text is readable at arm's length on phone
- [ ] All touch targets are at least 48x48px
- [ ] No horizontal scroll on any screen size
- [ ] `prefers-reduced-motion` removes flip animation
