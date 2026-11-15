# Mulai Villa social engine

A small system for running Mulai Villa's Instagram: strategy, a weekly post queue that
Claude drafts, a human approval step, and a script that schedules approved posts.

```
strategy/goals.md          follower, enquiry and quality targets
strategy/brand-style.md    voice, visual style, post series, profile
strategy/content-system.md pillars, weekly rhythm, the weekly loop
config.json                cadence, pillar weights, copy rules
queue/<week>.json          the posts, one file per week
media/                     photos and videos (see media/README.md)
metrics/weekly.csv         one row of results per week
engine/engine.py           plan, validate, status, publish
```

## The weekly loop

```
python3 engine/engine.py plan 2026-W49     # create next week's slots
# ask Claude: "run the social weekly batch for 2026-W49"   (drafts every post)
python3 engine/engine.py status            # see the queue
# owner: add media, check facts, clear fact_check, set status to "approved"
python3 engine/engine.py validate          # brand-rule and completeness checks
python3 engine/engine.py publish           # dry run: shows exactly what would go out
python3 engine/engine.py publish --live    # schedules approved posts
```

Post statuses: `brief` (empty slot) → `draft` (Claude has written it) → `approved`
(a person has signed it off) → `scheduled` (sent to the scheduler). Only `approved`
posts are ever sent, and only if they pass validation.

## One-time setup for publishing

Publishing goes through [Postiz](https://github.com/gitroomhq/postiz-app), an
open-source scheduler (hosted or self-hosted), using its
[CLI](https://github.com/gitroomhq/postiz-agent).

1. Make the Instagram account a Business or Creator account linked to a Facebook Page.
2. Create a Postiz account and connect Instagram.
3. `npm install -g postiz`, then `postiz auth:login` (or set `POSTIZ_API_KEY`).
4. `postiz integrations:list`, then `export POSTIZ_INSTAGRAM_ID=<the Instagram id>`.

Until that is done, `publish` works in dry-run mode and the queue can be posted by hand:
each post has its caption, hashtags and shot brief ready to copy.

The `--live` path has been tested up to the point of calling Postiz, not against a real
Postiz account. Run the first live week with one post and check it in the Postiz calendar.

## Claude skills

In `.claude/skills/` at the repo root:

- `social-weekly-batch`: drafts a week of posts into the queue in the brand voice.
- `social-weekly-review`: logs last week's numbers and turns them into next week's changes.
