# Content system

## Pillars and mix

| Pillar | Share | Job |
|---|---|---|
| The villa and its design | 30% | Desire: this is where you would be |
| Lombok, slowly | 25% | Reach and saves: useful to anyone planning Lombok |
| The people and the hospitality | 15% | Trust: who will look after you |
| Guest book | 15% | Proof: people like you loved it |
| Begin here (how to book) | 10% | Conversion: how to turn interest into dates |
| Mulai: to begin | 5% | Meaning: why the villa exists |

`engine.py plan` rotates pillars across the week in these proportions (set in `config.json`).

## Weekly rhythm (Lombok time)

| Day | Slot | Format |
|---|---|---|
| Mon | 12:00 | Story |
| Tue | 16:30 | Reel |
| Wed | 12:00 | Story |
| Thu | 16:30 | Carousel |
| Fri | 12:00 | Story |
| Sat | 15:00 | Reel |
| Sun | 16:30 | Photo |

16:30 in Lombok is early evening in eastern Australia and morning in Europe. Treat the
times as a starting guess and move them once Insights shows when followers are online.

## The weekly loop

1. **Monday: review.** Log last week's numbers, note the best and worst post and why.
2. **Monday: plan.** `engine.py plan <week>` creates next week's slots.
3. **Monday: write.** Claude drafts hooks, captions, hashtags and shot briefs for each slot
   (`social-weekly-batch` skill), using what the review learned.
4. **Tuesday to Thursday: capture.** Someone at the villa shoots to the briefs, or picks
   from the media library. Files go in `media/<week>/`.
5. **Friday: approve.** The owner reads each post, confirms the facts, clears `fact_check`,
   sets `status` to `approved`.
6. **Friday: schedule.** `engine.py validate` then `engine.py publish --live` sends the
   approved posts to the scheduler. Nothing unapproved can go out.
7. **Daily, 10 minutes:** reply to comments and DMs. This is the one part no tool should do
   for you: a DM is a guest at the door.

## Hashtags

Three to five per post, drawn from these sets, mixing one broad with specific ones.

- Place: lombok, lombokisland, visitlombok, lomboktrip, kutalombok or selongbelanak
  (use the one that matches the villa's real area)
- Villa: lombokvilla, villalombok, privatevilla, villadesign, tropicaldesign
- Travel style: slowtravel, honeymoonindonesia, indonesiatravel
- Culture: sasak

## What we do not post

Discounts and countdowns, stock imagery, AI-generated images of the villa, reposts
without permission, anything about a guest without consent, trend formats that do not
fit the voice.
