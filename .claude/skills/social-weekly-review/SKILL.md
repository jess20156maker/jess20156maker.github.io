---
name: social-weekly-review
description: Review last week's Mulai Villa Instagram results, log them, and decide what to change. Use when the user says "social review", "how did last week's posts do", "log the Instagram numbers", "weekly social report", or pastes Instagram Insights figures.
---

# Social weekly review

1. Read `mulai-social-engine/strategy/goals.md`, `metrics/weekly.csv`, and last week's
   file in `queue/`.
2. Get last week's numbers. If the Postiz CLI is set up, run
   `postiz analytics:platform "$POSTIZ_INSTAGRAM_ID" -d 7`. Otherwise ask the user to paste
   from Instagram Insights: followers, reach, share of reach from non-followers, profile
   visits, link clicks, and saves and shares for each post. Ask separately for WhatsApp
   or website enquiries that mentioned Instagram, and any direct bookings. Do not estimate
   a number you were not given; leave the cell empty.
3. Append one row to `metrics/weekly.csv`.
4. Report, briefly:
   - Progress against the milestone table in goals.md: on track, ahead or behind.
   - Best and weakest post, with a reason grounded in the hook, format, pillar or timing.
   - Two or three specific changes for next week (for example: "two Lombok guides
     instead of one", "move Saturday's Reel to 19:00").
5. If one finding has held for three weeks running, propose a change to `config.json`
   (pillar weights or slot times) and make it only if the user agrees.
