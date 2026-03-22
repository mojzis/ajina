# Build Workflow — Autonomous Execution

## How This Works

Each phase runs in its own subagent with fresh context. The parent reads
CLAUDE.md, finds incomplete phases, and launches them sequentially. Each
subagent reads its prompt file, implements everything, runs checks, and commits.
The parent updates the checklist and moves to the next phase.

## Phases

| # | Prompt File | Description |
|---|------------|-------------|
| 1 | `plans/PROMPT-01-setup.md` | Project scaffolding, pyproject.toml, CLAUDE.md |
| 2 | `plans/PROMPT-02-frontend.md` | Frontend template (HTML/CSS/JS) |
| 3 | `plans/PROMPT-03-build-pipeline.md` | Build pipeline (parse, audio, images, deploy) |
| 4 | `plans/PROMPT-04-image-generation.md` | Real image generation via Replicate API |
| 5 | `plans/PROMPT-05-polish-deploy.md` | Polish, performance, deployment |

## Subagent Prompt Template

For each incomplete phase, launch a subagent with this prompt:

```
You are executing Phase N of the slovicka project build.

Read these files for context:
- CLAUDE.md (project conventions, dev commands)
- plans/PROJECT.md (full project spec)
- plans/PROMPT-0N-<name>.md (this phase's detailed instructions)

Then:
1. Implement everything described in the phase prompt
2. Run `poe check` and fix any issues until it passes clean
3. Stage all changes and commit:
   git add -A && git commit -m "feat: phase N - <description>"

Do not ask for input. Make reasonable decisions and keep going.
If blocked by an external dependency (API key, etc.), implement
everything possible and note what needs manual setup.
```

## Decision Making

- If blocked, document the blocker in `plans/blockers.md` and continue
- Make reasonable decisions and document them
- Do not ask for input — keep going

## The Prompt

User says **"go"** and the parent orchestrator:

1. Reads `CLAUDE.md` → finds next `[ ]` phase
2. Launches subagent with the phase prompt
3. On completion, marks `[x]` in `CLAUDE.md`
4. Repeats until all phases are done

## Quick Reference

| Step | Who | What |
|------|-----|------|
| **Orchestrate** | Parent | Find next `[ ]` phase, launch subagent |
| **Read** | Subagent | Phase prompt + PROJECT.md + CLAUDE.md |
| **Implement** | Subagent | Write code per the prompt instructions |
| **Verify** | Subagent | `poe check` — fix until green |
| **Commit** | Subagent | `git add -A && git commit -m "feat: phase N - ..."` |
| **Update** | Parent | Mark `[x]` in CLAUDE.md |
| **Continue** | Parent | Launch next subagent immediately |
