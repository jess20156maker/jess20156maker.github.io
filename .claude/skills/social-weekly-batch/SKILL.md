---
name: social-weekly-batch
description: Draft a week of Mulai Villa Instagram posts into the social engine queue. Use when the user says "plan next week's posts", "run the social weekly batch", "write this week's content", "fill the queue", or names a week like 2026-W49 for social content.
---

# Social weekly batch

Draft every slot in one week's queue file for Mulai Villa's Instagram. You write; the
owner approves. Never set a post to `approved` yourself and never run `publish --live`
unless the user asks for that in this conversation.

## Steps

1. Read, in `mulai-social-engine/`: `strategy/brand-style.md`,
   `strategy/content-system.md`, `config.json`, the last two files in `queue/` (to avoid
   repeating hooks, series and shots), and the last rows of `metrics/weekly.csv` (to do
   more of what worked).
2. If the week's file does not exist, run `python3 engine/engine.py plan <week>`.
3. Ask the user, in one message, only for what you cannot know: anything happening at
   the villa that week (guests who gave photo permission, weather, an event, open dates
   to mention), and which media already exists. If they do not answer, proceed with
   evergreen ideas.
4. Give the week a one-line `theme`. Fill each slot:
   - `series`: one from the series table in brand-style.md, matching the slot's pillar.
   - `hook`: the first line, also the on-screen text for Reels and the carousel cover.
   - `caption`: follows the caption rules. Stories may leave it empty.
   - `hashtags`: 3 to 5, no `#`, from the sets in content-system.md.
   - `shot_brief`: precise enough for a non-photographer with a phone. Format, ratio,
     length, each clip or slide in order, sound, cover.
   - `fact_check`: every claim about the villa, team, inclusions, prices or places that
     a person must confirm before posting. Leave empty only if there are none.
   - `status`: `draft`.
5. Run `python3 engine/engine.py validate <week>` and fix every error and warning.
6. Show the user the week as a short table (day, format, series, hook) and list the
   facts to confirm and the shots to capture.

## Quality bar

- One idea per post. Specific, sensory, true. If a line could describe any villa, cut it.
- Do not invent details: bedroom counts, staff names, distances, prices, inclusions.
  Write around them or put the question in `fact_check`.
- Across the week: no repeated opening word, no two posts with the same closing line,
  at least one post built to be saved and one built to be shared.
- If `anthropic-skills:write-like-a-human` or the `mulai-villa-brand:brand-voice` skill
  is available, apply it to the captions.
