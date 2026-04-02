# Image Prompt Guide

The image model is great at concrete, visual nouns. For abstract words, greetings,
and phrases it needs a nudge — a **scene description** that tells it what to paint.

## When to add a scene prompt

**Leave it empty** — the model figures it out:
- Concrete nouns: `cat`, `dog`, `tree`, `coffee`, `chair`, `apple`
- Clear actions: `run`, `swim`, `eat`, `sleep`
- Colors, numbers, basic adjectives: `red`, `big`, `three`

**Add a scene prompt** — the model needs guidance:
- Greetings & social phrases: `good morning`, `thank you`, `goodbye`, `how are you`
- Abstract concepts: `happy`, `tired`, `hungry`, `love`, `friendship`
- Time expressions: `yesterday`, `tomorrow`, `weekend`, `always`
- Multi-word phrases: `I don't know`, `let's go`, `be careful`

## How to write a good scene

Describe **what to paint**, not what the word means. One clear image. Keep it short.

| Word | Bad scene | Good scene |
|------|-----------|------------|
| good morning | morning time | a person stretching their arms in bed, sunlight streaming through the window |
| thank you | gratitude | two people facing each other — one handing over a wrapped gift, the other receiving it with a smile |
| tired | being tired | a person slumped in a chair with heavy eyelids, head drooping |
| hungry | hunger | a person looking longingly at an empty plate, stomach visibly rumbling |
| be careful | caution | a child about to step on a banana peel, an adult reaching out to warn them |
| I don't know | not knowing | a person shrugging with both palms up and a puzzled expression |
| goodbye | farewell | two people waving to each other at an open front door |
| weekend | weekend | a family relaxing in a park on a sunny day — picnic blanket, no school bags |

## Rules

1. **One scene** — not a collage. The model draws one moment, one place.
2. **Describe people/objects/actions** — not emotions or abstractions directly.
3. **No text** — never ask for text in the scene; the prompt template already forbids it.
4. **Stays appropriate** — simple, clear, suitable for people with mental disabilities learning English.
5. **Commas OK** — the scene field is the last column, so commas inside are fine.

## Input file format

```
czech, english, pronunciation, image_prompt
```

The last field is optional. Omit it (or leave blank) for concrete words.

```
# concrete — no scene needed
kočka, cat, ket
káva, coffee, kofi

# abstract — scene helps
dobrý den, good morning, gud morning, a person stretching in bed as warm sunlight streams through the window
díky, thank you, tenk jů, two people facing each other — one handing a gift the other receives with a smile
nevím, I don't know, aj dont nou, a person shrugging with both palms up and a puzzled expression
```
