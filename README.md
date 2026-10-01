# Tapwise: NFC ideas, reviewed by Jev + Claude

**This repo is really about one thing: a human staying in the AI loop and picking the right model for each job, with numbers to back every choice.** The vehicle is a small website, Tapwise, that suggests everyday NFC tag ideas that fit your life and lets visitors add their own.

The headline choice: visitor ideas are checked for duplicates by **[Jev](https://docs.typesafe.ai)**, a new kind of AI model from TypeSafe that doesn't write text at all. It only answers typed questions with calibrated probabilities. For this job it scored as well as Claude Opus 5 on unseen tests, at **about 1/175th of the cost**. Claude still does what Jev can't: judging whether an idea is real and safe, and writing it up nicely.

Built by the user together with Claude (Anthropic), NotebookLM (Google) and Jev (TypeSafe). Work in progress, private for now.

![Home](docs/img/10-app-home.png)

## Which model does what, and why

| Job | Model | Why this one | Measured |
|---|---|---|---|
| **Is a visitor's idea already in the bank?** | **Jev** (TypeSafe) | A decision, not a text. Jev returns probabilities your code can branch on, and only charges for input ($0.042 per million tokens). | **23/23** right on unseen ideas · 0.7 s · **$0.0003 per idea** |
| Is a new idea real and safe? Write it up for the site | Claude Sonnet 5 | Needs judgement *and* good writing, which Jev can't do. Haiku 4.5 was cheaper but rejected a good idea in testing. | 15/15 right on unseen ideas · 3.8 s · $0.008 per idea |
| Fallback if Jev is unavailable: everything in one call | Claude Opus 5 | Does the whole review alone, very accurately, but costs the most. | 23/23 · $0.046 per idea |
| Pull ideas out of 40+ videos and Reddit threads | NotebookLM | Built for reading many sources at once and citing them. | every idea checked by hand |
| Match quiz answers to ideas | **no AI**: simple rules | Fast, free, offline, predictable. Not every job needs a model. | |
| "Is this already in the bank?" hint while typing | **no AI**: word overlap | Instant and free; a hint, not a decision. | |
| Plan the project and write the code | Claude (Claude Code) | the user decides; Claude proposes, explains and builds. | |

Every visitor idea goes through this pipeline:

```
visitor idea ──> Jev: duplicate?  ──yes──> filed as a duplicate (no Claude call: $0.0003)
                     │ no
                     v
                 Claude Sonnet 5: real and safe? ──no──> rejected
                     │ yes
                     v
                 written up, credited to the visitor, live in the bank (≈ $0.008)
```

Every decision is listed on the admin page with the reason and an **Undo** button.

## Why Jev, and how we made it work

Jev is a "System One" model: you send it a *state* (some text) and typed *questions* (choose one option, give a score, or is this true?), and it answers each with probabilities and a confidence. It's built for fast, structured decisions, and the pricing reflects that. the user wanted to try something this new on a real task rather than just read about it.

**First try: not good enough.** One Jev question per idea ("which existing idea is this the same as?") got **20/24**. It called some genuinely new ideas duplicates ("lending books" matched "cleaning rounds", wine bottles matched "3D printer spools"). With the AI approving ideas automatically, that would quietly throw away good suggestions. Claude Opus 5 got 24/24.

**Second try: two steps, small questions** (following Jev's own advice to ask atomic questions and combine them in code):

1. **Shortlist:** one Choice question over the whole bank picks the 3 closest ideas.
2. **Side by side:** the new idea and each shortlisted idea go in together, and Jev answers two yes/no questions: *is it the same idea, just worded differently?* and *does it solve the same everyday problem?*
3. **Plain code decides:** it's a duplicate if step 1 picked it with ≥ 50% and both answers agree (≥ 0.5), or if both answers alone are very sure (≥ 0.8).

**Testing it honestly.** We kept two separate sets of made-up ideas ([`scripts/review_cases.py`](scripts/review_cases.py)): a **dev** set for tuning, and a **holdout** set written *before* any tuning and scored only once, at the end, so the final numbers aren't flattered by fixes made while looking at them. Holdout ideas use informal wording, typos, and "near misses" that look like an existing idea but aren't.

| On the holdout set | Correct | Cost per idea | Time |
|---|---|---|---|
| **Jev**, two steps | **23/23** | **$0.00026** | 0.7 s |
| Claude Opus 5, everything in one call | 23/23 | $0.046 | 3.4 s |

Same accuracy on this test, about **175× cheaper** for each duplicate. A new idea also needs Claude to write it up, which makes it about 6× cheaper overall. Small numbers either way for a hobby site, but the pattern holds at any scale. Run the tests yourself: [`scripts/eval_review.py`](scripts/eval_review.py).

**Honest limits.** 23 test ideas is a small test, and one dev case turned out to be genuinely debatable (we moved it to "borderline" and say so in the log). Jev reads questions literally. And it can't write, which is why Claude stays in the pipeline.

## More

- **The whole story, step by step** (every decision, mistake and lesson): [PROJECT_LOG.md](PROJECT_LOG.md)
- **How to run it** (Raspberry Pi + Docker): [RUN.md](RUN.md)
- **The AI review code:** [`app/ai_review.py`](app/ai_review.py)
