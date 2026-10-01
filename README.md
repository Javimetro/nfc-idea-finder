# Tapwise: NFC ideas, reviewed by Jev + Claude

**This repo is really about one thing: a human staying in the AI loop and picking the right model for each job, with numbers to back every choice.** The vehicle is a small website, Tapwise, that suggests everyday NFC tag ideas that fit your life and lets visitors add their own.

The headline choice: visitor ideas are checked for duplicates by **[Jev](https://docs.typesafe.ai)**, a new kind of AI model from TypeSafe that doesn't write text at all. It only answers typed questions with calibrated probabilities. On 228 test ideas it decides most duplicates on its own, at **about 1/175th of Claude Opus 5's cost**, and every duplicate it filed alone was right (77/77 on the unseen sets). When it isn't sure, it hands over to Claude. Claude also does what Jev can't: judging whether an idea is real and safe, and writing it up nicely.

Built by the user together with Claude (Anthropic), NotebookLM (Google) and Jev (TypeSafe). Work in progress, private for now.

![Home](docs/img/10-app-home.png)

## Which model does what, and why

| Job | Model | Why this one | Measured |
|---|---|---|---|
| **Is a visitor's idea already in the bank?** | **Jev** (TypeSafe) | A decision, not a text. Jev returns probabilities your code can branch on, and only charges for input ($0.042 per million tokens). | **70–71 of 71** unseen ideas right · when sure, **77/77** right · 0.6 s · **$0.0003 per idea** |
| Jev thinks it's a duplicate but isn't sure (~14% of duplicates) | Claude Sonnet 5 | A second opinion only where it's needed ("confidence routing"). Rescues new ideas that merely *look* like an existing one. | part of the Claude call below |
| Is a new idea real and safe? Write it up for the site | Claude Sonnet 5 | Needs judgement *and* good writing, which Jev can't do. Haiku 4.5 was cheaper but rejected a good idea in testing. | 15/15 right on unseen ideas · 3.8 s · $0.008 per idea |
| Fallback if Jev is unavailable: everything in one call | Claude Opus 5 | Does the whole review alone, very accurately, but costs the most. | 23/23 · $0.046 per idea |
| Pull ideas out of 40+ videos and Reddit threads | NotebookLM | Built for reading many sources at once and citing them. | every idea checked by hand |
| Match quiz answers to ideas | **no AI**: simple rules | Fast, free, offline, predictable. Not every job needs a model. | |
| "Is this already in the bank?" hint while typing | **no AI**: TF-IDF word matching | Instant and free; a hint, not a decision. | right idea shown for 120 of 145 test duplicates (83%) |
| Plan the project and write the code | Claude (Claude Code) | the user decides; Claude proposes, explains and builds. | |

Every visitor idea goes through this pipeline:

```
visitor idea ──> Jev: already in the bank?
                  │
                  ├─ yes, and sure ──────────────> filed as a duplicate (no Claude call: $0.0003)
                  │
                  ├─ maybe (not sure) ──┐
                  └─ no ────────────────┤
                                        v
                 Claude Sonnet 5: really a copy? real and safe?
                  ├─ copy ──> filed as a duplicate
                  ├─ junk or unsafe ──> rejected
                  └─ new ──> written up, credited to the visitor, live in the bank (≈ $0.008)
```

Every decision is listed on the admin page with the reason and an **Undo** button.

## Why Jev, and how we made it work

Jev is a "System One" model: you send it a *state* (some text) and typed *questions* (choose one option, give a score, or is this true?), and it answers each with probabilities and a confidence. It's built for fast, structured decisions, and the pricing reflects that. the user wanted to try something this new on a real task rather than just read about it.

**First try: not good enough.** One Jev question per idea ("which existing idea is this the same as?") got **20/24**. It called some genuinely new ideas duplicates ("lending books" matched "cleaning rounds", wine bottles matched "3D printer spools"). With the AI approving ideas automatically, that would quietly throw away good suggestions. Claude Opus 5 got 24/24.

**Second try: two steps, small questions** (following Jev's own advice to ask atomic questions and combine them in code): a shortlist question over the whole bank, then each likely match side by side with the suggestion. That got 23/23 on a small unseen test, but a much bigger test showed it still let too many duplicates through.

**Third try (live now): "does it already cover it?"**

1. **Shortlist:** one Choice question over the whole bank: *which existing idea already covers this suggestion, so adding it would repeat it?*
2. **Side by side:** each likely match (≥ 45% in step 1) next to the suggestion, one yes/no question: *does the existing idea already cover it, even if the suggestion is one specific example of it?*
3. **Plain code decides:** a duplicate if step 2 says ≥ 55%. Both steps must agree.
4. **Confidence routing:** Jev files a duplicate on its own only when it's very sure (step 1 ≥ 95% and step 2 ≥ 80%). Otherwise Claude, which is called for new ideas anyway, gets Jev's suggested match and makes the final call.

**How we found it: a lab, and tests we didn't peek at.** [`scripts/jev_lab.py`](scripts/jev_lab.py) asks Jev every candidate question once (3 shortlist wordings, 7 side-by-side questions) and saves the raw answers ([`scripts/lab_results/`](scripts/lab_results/)). Then hundreds of decision rules are tried on the saved answers for free. The test ideas ([`scripts/review_cases_big.py`](scripts/review_cases_big.py)) were written and committed to git **before** any tuning on them:

| Test set | What's in it | Used for |
|---|---|---|
| TUNE | 100 ideas: reworded duplicates of every bank idea, new ideas, other languages, typos | tuning only |
| TEST | 82 other ideas, same mix | scoring once the rule was frozen |
| NEAR | 46 ideas aimed at the weak spot: new ideas that *look like* a bank idea, and "one specific example" duplicates | choosing between the final versions (the rule for choosing was written down first) |

| Duplicate check | TUNE | TEST (unseen, 3 runs) | NEAR (unseen) | Cost per idea |
|---|---|---|---|---|
| Second try | 86/89 | 66/71 | 36/46 | $0.00026 |
| **Third try** | **89/89** | **70–71/71** | **40/46** | **$0.00030** |
| Third try, Jev alone when sure | | **50/50** filed right | **13/13** filed right | |

Jev's answers vary a little from run to run (one TEST case sits right at the threshold), so we report all three runs. The weak spot is honest and known: on NEAR, 5 of 26 look-alike new ideas looked like duplicates to Jev, e.g. "office coffee machine tells facilities it needs descaling" vs "remember when you last cleaned something". None of those 5 were "sure", so routing sends them all to Claude instead of throwing them away. Run it yourself: [`scripts/eval_review.py`](scripts/eval_review.py) (`dupes`, `route`).

**Honest limits.** These are made-up test ideas written by us, not real visitors yet. The "sure" bar (95% / 80%) was picked after seeing NEAR. Claude's second opinion on unsure duplicates is built and wired up but hasn't been measured yet (that needs a short Claude test run). Jev reads questions literally, and it can't write, which is why Claude stays in the pipeline.

## What it costs: Jev vs Claude

AI models charge per **token** (roughly ¾ of a word): once for what they read (input) and once for what they write (output).

**The price lists** (US dollars per million tokens, October 2026):

| Model | Reading (input) | Writing (output) |
|---|---|---|
| **Jev** (TypeSafe) | **$0.042** | **free** (it only returns short answers, no text) |
| Claude Haiku 4.5 | $1 | $5 |
| Claude Sonnet 5 | $2 | $10 |
| Claude Opus 5 | $5 | $25 |

Reading costs about **24× less with Jev than with Haiku**, Claude's cheapest model, and **119× less than with Opus**. Jev also charges nothing for its answers.

**One duplicate check, measured** (average over the test ideas):

| | Tokens read | Tokens written | Cost | Time |
|---|---|---|---|---|
| **Jev** (shortlist + side-by-side check) | ~7,200 | answers only (free) | **$0.00030** | 0.6 s |
| Claude Opus 5 (the whole bank in one prompt) | ~8,300 | ~150 | $0.046 | 3.4 s |

Both models read about the same amount, because both have to look at the whole idea bank. The difference is almost entirely the **price per token**: same accuracy on our test, **about 175× cheaper**.

**Per 1,000 visitor ideas**, assuming half are duplicates:

| Setup | Cost |
|---|---|
| Claude Opus 5 does everything | **$46** |
| Today's setup: Jev checks all 1,000; Claude Sonnet 5 handles the 500 new ones plus the ~70 duplicates Jev isn't sure about | **≈ $4.60** (Jev $0.30 + Sonnet $4.30) |
| The duplicate check on its own: Jev vs Opus 5 | **$0.30** vs $46 |

What's left of the bill is Claude doing what Jev can't: judging whether an idea is real and safe, and writing it up. For that we picked the cheapest Claude that passed the test (Sonnet 5; Haiku 4.5 was cheaper but rejected a good idea).

**What building and testing this cost** (1 October 2026, all test runs together): about **$2.50 on Claude**, most of it Opus 5 runs used as the comparison baseline, and about **$0.50 on Jev** for roughly 12 million tokens: the whole lab, every tuning run and every test run.

Prices change; check [Anthropic's pricing](https://www.anthropic.com/pricing) and [TypeSafe's models page](https://docs.typesafe.ai/models) for current ones. Costs here are calculated from the token counts our test scripts recorded.

## More

- **The whole story, step by step** (every decision, mistake and lesson): [PROJECT_LOG.md](PROJECT_LOG.md)
- **How to run it** (Raspberry Pi + Docker): [RUN.md](RUN.md)
- **The AI review code:** [`app/ai_review.py`](app/ai_review.py)
