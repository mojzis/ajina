# Testing Checklist

Manual testing checklist for the Slovíčka flashcard app.

## Browser Compatibility

- [ ] Page loads on Chrome mobile
- [ ] Page loads on Safari iOS
- [ ] Page loads on older Android (Chrome 90+)

## Core Functionality

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

## Error Handling

- [ ] Missing audio doesn't break anything
- [ ] Missing image shows placeholder gracefully
- [ ] Failed JSON load shows error message with retry button
- [ ] Works in airplane mode after initial load

## Polish & UX

- [ ] First visit shows intro banner ("Klikni na kartičku a uč se anglicky!")
- [ ] Intro banner can be dismissed and stays dismissed for the session
- [ ] Cards fade in one by one with stagger animation
- [ ] Speaker icon pulses while audio plays
- [ ] Speaker icon briefly turns green when audio finishes
- [ ] "Další slovíčko" prompt appears after flipping and hearing English word
- [ ] Visited cards show a subtle dot indicator in grid view
- [ ] Week switching fades out old cards and fades in new ones

## Accessibility

- [ ] Text is readable at arm's length on phone
- [ ] All touch targets are at least 48x48px
- [ ] No horizontal scroll on any screen size
- [ ] `prefers-reduced-motion` removes flip animation
- [ ] Keyboard navigation works (arrows, space, escape)
- [ ] Screen reader can navigate cards and controls

## Performance

- [ ] Images lazy-load (only visible + next row)
- [ ] Audio preloads for first 2 cards
- [ ] Page is usable within 5 seconds on throttled 3G
