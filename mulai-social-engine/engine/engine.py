#!/usr/bin/env python3
"""Mulai Villa social engine: plan, validate, report on and publish the post queue.

  engine.py plan 2026-W48        create next week's empty slots from config.json
  engine.py validate [week]      check posts against the brand rules
  engine.py status [week]        show the queue
  engine.py publish [week]       dry-run: show what would be sent to Postiz
  engine.py publish [week] --live   schedule approved posts in Postiz

Only posts with status "approved" are ever published. Statuses:
brief -> draft -> approved -> scheduled. Standard library only.
"""
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "config.json").read_text())
QUEUE = ROOT / "queue"
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿]")


def week_files(week=None):
    files = sorted(QUEUE.glob("*.json"))
    if week:
        files = [f for f in files if f.stem == week]
        if not files:
            sys.exit(f"No queue file for {week} (run: engine.py plan {week})")
    return files


def load(path):
    return json.loads(path.read_text())


def save(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def pillar_rotation(n, offset):
    """Spread pillars across n slots in proportion to their weights, rotating weekly."""
    weights = {k: v["weight"] for k, v in CONFIG["pillars"].items()}
    total = sum(weights.values())
    credit = dict.fromkeys(weights, 0.0)
    # Carry credit forward from earlier weeks so small pillars come round in turn.
    out = []
    for i in range(offset * n + n):
        for k in credit:
            credit[k] += weights[k] / total
        pick = max(credit, key=credit.get)
        credit[pick] -= 1
        out.append(pick)
    return out[-n:]


def cmd_plan(week):
    if not re.fullmatch(r"\d{4}-W\d{2}", week or ""):
        sys.exit("Usage: engine.py plan YYYY-Www   (e.g. 2026-W48)")
    path = QUEUE / f"{week}.json"
    if path.exists():
        sys.exit(f"{path.name} already exists; edit it instead of re-planning.")
    year, wk = int(week[:4]), int(week[6:])
    feed = [s for s in CONFIG["weekly_slots"] if s["type"] == "post"]
    pillars = iter(pillar_rotation(len(feed), wk))
    posts = []
    for slot in sorted(CONFIG["weekly_slots"], key=lambda s: DAYS.index(s["day"])):
        day = dt.date.fromisocalendar(year, wk, DAYS.index(slot["day"]) + 1)
        posts.append({
            "id": f"{week}-{slot['day']}",
            "date": f"{day.isoformat()}T{slot['time']}:00{CONFIG['timezone_offset']}",
            "type": slot["type"],
            "format": slot["format"],
            "pillar": next(pillars) if slot["type"] == "post" else "",
            "series": "",
            "status": "brief",
            "hook": "",
            "caption": "",
            "hashtags": [],
            "media": [],
            "alt_text": [],
            "shot_brief": "",
            "fact_check": "",
        })
    save(path, {"week": week, "theme": "", "posts": posts})
    print(f"Created {path.relative_to(ROOT)} with {len(posts)} slots.")


def check(post):
    """Return (errors, warnings) for one post."""
    rules, errs, warns = CONFIG["rules"], [], []
    cap = post.get("caption", "")
    text = " ".join([cap, post.get("hook", "")])
    is_story = post["type"] == "story"
    ready = post["status"] in ("approved", "scheduled")

    if post["status"] != "brief":
        if not is_story and not cap.strip():
            errs.append("caption is empty")
        if len(cap) > rules["caption_max_chars"]:
            errs.append(f"caption is {len(cap)} chars (Instagram max {rules['caption_max_chars']})")
        elif len(cap) > rules["caption_target_max_chars"]:
            warns.append(f"caption is {len(cap)} chars (house style: under {rules['caption_target_max_chars']})")
        for phrase in rules["banned_phrases"]:
            if phrase.lower() in text.lower():
                errs.append(f'off-brand phrase: "{phrase}"')
        for marker in rules["unconfirmed_markers"]:
            if marker in text:
                errs.append(f'unconfirmed detail still in copy: "{marker}"')
        if len(EMOJI.findall(cap)) > rules["max_emoji"]:
            warns.append(f"more than {rules['max_emoji']} emoji")
        if "#" in cap:
            errs.append("hashtags belong in the hashtags list, not the caption")
        if not is_story:
            n = len(post.get("hashtags", []))
            if not rules["hashtags_min"] <= n <= rules["hashtags_max"]:
                errs.append(f"{n} hashtags (need {rules['hashtags_min']}-{rules['hashtags_max']})")
            if post.get("pillar") not in CONFIG["pillars"]:
                errs.append(f"unknown pillar: {post.get('pillar')!r}")
    if ready:
        media = post.get("media", [])
        if not media:
            errs.append("approved but no media attached")
        for m in media:
            if not (ROOT / m).is_file():
                errs.append(f"media file not found: {m}")
        if post["format"] == "carousel" and len(media) < 2:
            errs.append("carousel needs at least 2 media files")
        if post["format"] in ("reel", "photo", "story") and len(media) > 1:
            errs.append(f"{post['format']} takes one media file")
        if not is_story and len(post.get("alt_text", [])) != len(media):
            errs.append("alt_text needs one entry per media file")
        if post.get("fact_check", "").strip():
            errs.append("fact_check note not cleared (confirm the facts, then empty the field)")
    if post["status"] == "approved":
        if dt.datetime.fromisoformat(post["date"]) <= dt.datetime.now(dt.timezone.utc):
            errs.append("scheduled time is in the past")
    return errs, warns


def cmd_validate(week=None):
    failed = 0
    for path in week_files(week):
        for post in load(path)["posts"]:
            errs, warns = check(post)
            if errs or warns:
                print(f"{post['id']} [{post['status']}]")
                for e in errs:
                    print(f"  ERROR  {e}")
                for w in warns:
                    print(f"  warn   {w}")
            failed += bool(errs)
    print("All posts pass." if not failed else f"{failed} post(s) with errors.")
    return failed


def cmd_status(week=None):
    for path in week_files(week):
        data = load(path)
        print(f"\n{data['week']}  {data.get('theme', '')}")
        for p in data["posts"]:
            when = dt.datetime.fromisoformat(p["date"]).strftime("%a %d %b %H:%M")
            label = p.get("hook") or p.get("shot_brief") or ""
            print(f"  {when}  {p['format']:<8} {p.get('pillar', ''):<8} {p['status']:<9} {label[:60]}")


def run(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd[:2])} failed: {res.stderr.strip() or res.stdout.strip()}")
    return res.stdout.strip()


def cmd_publish(week=None, live=False):
    integration = os.environ.get(CONFIG["postiz_integration_env"], "")
    if live:
        if not shutil.which("postiz"):
            sys.exit("Postiz CLI not found. Install it: npm install -g postiz")
        if not integration:
            sys.exit(f"Set {CONFIG['postiz_integration_env']} (find it with: postiz integrations:list)")
    sent = skipped = 0
    for path in week_files(week):
        data = load(path)
        for post in data["posts"]:
            if post["status"] != "approved":
                continue
            errs, _ = check(post)
            if errs:
                print(f"SKIP {post['id']}: {'; '.join(errs)}")
                skipped += 1
                continue
            caption = post["caption"].strip()
            if post.get("hashtags"):
                caption += "\n\n" + " ".join("#" + h.lstrip("#") for h in post["hashtags"])
            when = dt.datetime.fromisoformat(post["date"]).astimezone(dt.timezone.utc)
            settings = json.dumps({"post_type": "story" if post["type"] == "story" else "post"})
            if not live:
                print(f"WOULD SCHEDULE {post['id']} at {when:%Y-%m-%d %H:%M} UTC "
                      f"({post['format']}, {len(post['media'])} media)\n{caption}\n")
                sent += 1
                continue
            try:
                urls = [json.loads(run(["postiz", "upload", str(ROOT / m)]))["path"] for m in post["media"]]
                cmd = ["postiz", "posts:create", "-c", caption, "-m", ",".join(urls),
                       "-s", when.strftime("%Y-%m-%dT%H:%M:%SZ"), "-i", integration,
                       "-t", "schedule", "--settings", settings]
                if post.get("alt_text"):
                    cmd += ["--alt", ",".join(a.replace(",", ";") for a in post["alt_text"])]
                post["postiz_response"] = run(cmd)[:500]
            except (RuntimeError, ValueError, KeyError) as exc:
                print(f"FAILED {post['id']}: {exc}")
                skipped += 1
                continue
            post["status"] = "scheduled"
            save(path, data)  # save after each post so a later failure never causes a double-post
            print(f"SCHEDULED {post['id']} at {when:%Y-%m-%d %H:%M} UTC")
            sent += 1
    verb = "scheduled" if live else "ready to schedule (dry run; add --live to send)"
    print(f"{sent} post(s) {verb}, {skipped} skipped.")
    return skipped


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    cmd, week = (args + [None, None])[:2]
    if cmd == "plan":
        cmd_plan(week)
    elif cmd == "validate":
        sys.exit(1 if cmd_validate(week) else 0)
    elif cmd == "status":
        cmd_status(week)
    elif cmd == "publish":
        sys.exit(1 if cmd_publish(week, live="--live" in sys.argv) else 0)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
