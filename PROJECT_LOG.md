# NFC Idea Finder: project log

> **What this file is.** The running diary of the project. Every step, decision, prompt and problem goes here, in order, so that at the end it can become the README of a public GitHub repo. Written simply enough for a curious 14-year-old.
>
> **How to use it.** Add a new entry every work session. Save screenshots in `docs/img/` and link them where the 📸 markers are.

---

## The idea in one paragraph

NFC is the tech that lets you pay by tapping your phone. It also works with tiny stickers (called **tags**) that cost less than €1. When you tap a tag with your phone, something happens: a website opens, your lights switch off, a timer starts. The problem: there are thousands of ideas online, scattered across videos and articles, and it is hard to find the ones that fit **you**. So this project is a website that asks you a few questions and then suggests NFC ideas for your exact situation, links you to the video (even the exact second) where someone explains it, and tells you which tag to buy.

## Who built it, and how

Built by **the user** (ICT engineering student), working together with AI the whole time:

- **Claude (chat and Claude Code, by Anthropic)**: planning, architecture, database design, writing prompts, cleaning data, and writing code with the user.
- **NotebookLM (by Google)**: reading all the source videos/articles and pulling ideas out of them.

Being open about this is part of the point: the repo shows how a person and AI tools can build something real together. the user makes the decisions; the AI proposes, explains and does the heavy lifting. Every AI output is checked by the user before it is used.

---

## Timeline

### Day 1: Saturday 26 September 2026

#### 1. The problem and first decisions

the user's starting point: *"It's very difficult to find ideas for NFC uses that are actually good for my specific case."*

Claude asked four questions before building anything. the user's answers:

| Question | Answer | Why it matters |
|---|---|---|
| Personal tool or public product? | **Public product**, maybe monetised later | Needs to be reliable, legal and nice to use |
| How are ideas matched to people? | **AI-assisted** | An AI reads the answers and picks/explains ideas |
| Start the database empty or from existing ideas? | **Seed it with ideas the user already had** | e.g. his "peek behind" idea: tap a box to see a photo of what's inside |
| Where to host it? | **Decide later** (maybe GitLab Pages + own domain) | Depends on how the AI part ends up working |

📸 *Screenshot: the four questions and answers.*

#### 2. Architecture: how the pieces fit

```
Visitor ──> Interview (web page) ──> Backend function ──> AI (LLM) ──> Tag matcher ──> Results page
                                          ^                                 ^
                                          |                                 |
                                   Database: sources, ideas, idea–source links, tag profiles
                                          ^
                                   the user curates it
```

📸 *Screenshot: the architecture diagram Claude drew in the chat.*

Explained simply:

- **Interview page.** A normal website with questions. Can live on a free static host.
- **Backend function.** A tiny program on a server. It exists for one big reason: the AI needs a secret key (like a password that costs money when used). If that key were inside the web page, anyone could copy it and run up a bill. So the key stays hidden on the server.
- **Pre-filter.** Before asking the AI, the backend picks ~20 ideas that roughly fit (e.g. "business" ideas for a café owner). Sending the whole database every time would be slow and expensive.
- **AI (LLM).** Reads your answers plus the ~20 candidates, ranks them and explains why each fits *you*. It also works out what your tag needs to survive (on metal? outdoors? iPhone?).
- **Tag matcher.** Turns those needs into a real tag recommendation plus a search term to buy it. **Important design choice:** the AI does *not* invent product names (AIs sometimes make things up). It only outputs needs; a fixed table written and checked by the user maps needs to tags.
- **Results page.** Ideas, who explained it (credit to the creator), a link to the exact second in the video, and the tag to buy.

#### 3. What the database looks like

Five tables:

1. **Sources**: one row per video, article or book. Title, link, platform, **creator name** (so they get credit), language.
2. **Ideas**: one row per idea, written in our own words. What it does, how it works, who it's for, where it's used, iPhone/Android, difficulty, cost, what the tag needs. For money-making ideas also: business model, who pays, startup cost.
3. **Idea–source links**: connects ideas to sources, with the **timestamp** (start second) where the idea is explained. One idea can come from many videos; one video has many ideas.
4. **Tag profiles**: a small, hand-checked buying guide (chip type, sticker/card/keyfob, works on metal, waterproof…) with a search term.
5. **Idea submissions**: ideas sent in by visitors (see step 5).

Why separate ideas and sources? The same idea ("guest wifi tag") appeared in **5 different videos**. Storing it once and linking it five times avoids duplicates and shows which ideas are popular.

Timestamp detail: YouTube links can jump to a second (`&t=134s`). TikTok and Instagram can't, so there we show "explained at 0:42" as text.

Copyright detail: we write summaries in our own words and **link** to creators; we never copy or re-upload their content.

#### 4. "Tell us new uses": visitor submissions

the user's idea: a small corner link on every page, and a bigger prompt on the results page ("Didn't see your use case? Tell us").

- Short form: idea (required), where you saw it (optional), name for credit (optional), email (optional).
- Submissions go into a **review queue**. Nothing appears on the site until the user approves it. Quality stays high.
- **Stopping bots.** Public forms get spammed by robots within days. Two defences:
  - a **honeypot**: an invisible form field. Humans don't see it, bots fill it in, and we throw those away;
  - **Cloudflare Turnstile**: a free, invisible "are you human?" check (no annoying picture puzzles).
- **Privacy (GDPR).** Finland is in the EU, so names and emails are personal data. Keep them optional, say what they're used for, delete emails once no longer needed.
- Later: the AI can pre-screen submissions (spot duplicates, suggest tags) so reviewing is fast.

#### 5. Landing page and entrepreneurs

- **Landing page.** One screen on a phone: a short hook ("Tap your phone. Make something happen."), one sentence with examples, and the **start button visible immediately** with "2 min, no signup". Everything else below the fold.
- **First question = intent.** "What do you want NFC for?"
  1. my personal life and home
  2. my job or workplace
  3. my business and its customers (reviews, menus, loyalty)
  4. starting a business around NFC

  the user's point: the site must also serve people who want to **make money** with NFC. Option 4 is for them. Their results show who the customer is, the business model and startup cost, never "earn €X per month" promises.

#### 6. Collecting the ideas: source search + NotebookLM

1. the user searched YouTube and elsewhere for NFC idea videos and added them to a **NotebookLM** notebook (24 sources: 22 videos, mostly English, 2 in Spanish, plus the book *NFC For Dummies*, 2016).
   📸 *Screenshot: the NotebookLM notebook with its sources.*
2. Claude wrote two prompts for NotebookLM (below). The trick was asking for **strict JSON** (a data format computers can read) with fixed field names, so the output could go straight into the database.
3. the user ran **step 1** once, then **step 2** in batches of ~5 sources. Why batches? With everything at once, NotebookLM cut answers short and mixed sources up.
   📸 *Screenshot: NotebookLM producing the JSON.*

<details>
<summary><b>Prompt 1: source inventory</b></summary>

```
List every source in this notebook as a JSON array. One object per source, with these fields:

- "source_no": number in the order you list them
- "title": the source's title
- "url": the original URL if you can see it, otherwise null
- "type": "video", "article" or "social_post"
- "platform": e.g. "YouTube", "TikTok", "Instagram", "blog", "Reddit"
- "creator_name": the channel, author or account name if stated in the source, otherwise null
- "language": e.g. "en", "fi", "es"

Rules: do not guess. If a value is not visible in the source, use null. Output only the JSON, no commentary.
```
</details>

<details>
<summary><b>Prompt 2: idea extraction (run per batch)</b></summary>

```
From the selected sources only, extract every distinct NFC use-case idea. If one source explains several ideas, create one object per idea. If the same idea appears in two sources, create one object per source (I will merge them later).

Output a JSON array. Each object has these fields:

- "idea_title": short name for the idea, max 8 words
- "summary": 1–2 sentences in your own words describing what it does and why it is useful. Do not copy sentences from the source.
- "how_it_works": short steps: what is written on the tag, what happens when tapped, which app or automation is needed
- "audience": array, any of "personal", "workplace", "business_customers", "nfc_as_business"
- "settings": array, e.g. "home", "car", "office", "shop", "restaurant", "warehouse", "events", "outdoors", "travel", "pets", "health"
- "goals": array, e.g. "automation", "share_info", "access", "reminder", "tracking", "marketing", "payments", "security", "accessibility"
- "phone_support": "any", "android_only", "iphone_only" or null
- "extra_app": app or tool needed, or null
- "difficulty": "easy", "medium" or "advanced"
- "cost_level": "under_5_eur", "5_to_50_eur", "over_50_eur" or null
- "tag_needs": { "form_factor", "on_metal", "waterproof", "rewritable", "secure_anti_clone", "chip_mentioned" }
- "business_model", "who_pays", "startup_cost_level": for money-making ideas only, otherwise null
- "source_title", "source_url", "creator_name"
- "timestamp": ONLY if the source explicitly shows it. Otherwise null. Never estimate.
- "anchor_quote": a short exact phrase from the source, max 12 words, from where this idea is explained
- "notes": anything uncertain, or null

Rules:
- Only include ideas actually described in the selected sources. Do not add your own ideas.
- If a value is not stated or clearly implied, use null rather than guessing.
- Write all text fields in English, even if the source is in another language. Keep "anchor_quote" in the source's original language.
- Output only the JSON, no commentary. If you run out of space, stop at a complete object and write CONTINUE on the last line.
```
</details>

**Why the "anchor quote"?** NotebookLM can't see video timestamps, so every timestamp came back empty (as expected). The anchor quote is an exact phrase from the video. With it, finding the exact second later takes seconds (search the video transcript for the phrase) instead of re-watching.

**Problems spotted in step 1 and how we handled them:**

| Problem | Fix |
|---|---|
| 3 videos were added to the notebook twice | Skipped the copies (24 → 21 unique sources) |
| All URLs empty | Will look them up from title + channel, then the user confirms |
| The book was loaded from a shadow-library file | Cite the book itself (publisher, ISBN), never that file |
| The book is from 2016 | Treat phone-compatibility info as possibly outdated |
| 2 Spanish videos | Asked NotebookLM to write in English, but keep quotes in Spanish |

#### 7. Cleaning the data (Claude + Python)

NotebookLM returned **152 idea entries** across 5 batches. Claude turned them into the database with a Python script (`scripts/build_db.py`):

- **Merged duplicates.** 152 raw entries → **78 ideas**. Example: "guest wifi" came from 4 videos; "leaving-home routine" from 6. All the sources are kept as links (**151 idea–source links**), so every creator still gets credit.
- **Sorted ideas by kind**, because not everything NotebookLM found is something a visitor can do with a sticker:

  | Kind | Count | Meaning |
  |---|---|---|
  | `diy` | 50 | You can do it with a tag + your phone |
  | `business` | 8 | A business uses it with customers |
  | `industry_example` | 9 | Real-world systems (hospitals, transit cards): inspiration only |
  | `product_feature` | 5 | NFC already built into a device (speakers, printers): no tag to buy |
  | `tip` | 6 | Advice, not an idea (e.g. "hide tags in books") |

- **Fixed errors the AI extraction made** (this is why a human + second AI check matters):
  - *"Store passwords or crypto wallet info on a hidden tag"* was listed as a security idea. It is the opposite: any phone with a free app can read a normal tag. Flagged: never recommend.
  - *"Add your door access card to your iPhone with Shortcuts"* (one video). Shortcuts can react to a card, but can't copy it or open a door with it. Flagged as likely misleading.
  - *Guest wifi tags* were marked "any phone". Android joins automatically; iPhones generally don't join wifi from a tag. Flagged to verify, with a QR-code fallback.
  - Door-unlock and garage ideas: added a security note. Never write an "unlock" link on the tag itself; let only *your* phone's automation react to it.
  - Many ideas were marked "iPhone only" just because the video used an iPhone. Added Android alternatives (NFC Tools, MacroDroid, Tasker).
- **36 ideas carry a review flag** for the user to check before anything is published.

Result files (`db/`): `sources.json` (21), `ideas.json` (78), `idea_sources.json` (151).

#### 8. Two more sources (evening)

the user added a Shortcuts video by **Stephen Robles** and the book *Near Field Communication (NFC) for Embedded Applications* (Agus Kurniawan, 2015).

- The video's 3 ideas were all already in the database (bedtime scene, grocery list, play music), so they became **extra links** to existing ideas, not new ideas. This is the merge system working as planned.
- The book added a new **kind** of idea: **maker projects**, where you build your own NFC reader with a Raspberry Pi or Arduino (a tap-in attendance logger and a prepaid card for a club kiosk). Great for people who like building things.
- Caught another AI mistake: NotebookLM called the PN532 a tag chip. It is actually the **reader**. Also flagged that a card's ID can be copied, so the prepaid-card idea needs secure cards and server-side balances.

Database now: 23 sources, 80 ideas, 156 links, 38 flagged.

#### 9. Should we use "Jev" for choosing ideas?

the user found **Jev** (by TypeSafe AI), a new kind of AI model launched on 21 September 2026. Unlike chatbots, it doesn't write text. It only returns a **choice, a score or a yes/no probability**. It is also very cheap: about $0.04 per million input tokens, with output free.

What we worked out:

- **Good fit for ranking.** "How well does idea X fit this visitor? Give a score" is exactly what Jev is built for. It is so cheap it could score all 80 ideas every time, so we might not even need the pre-filter.
- **Good fit for tag needs.** "Will this tag go on metal? Outdoors? Yes/no" are yes/no questions, so Jev could answer them too.
- **Not a fit for explanations.** Jev can't write "this fits you because…". Our idea summaries are already written, though, so the results page can show those. We only add a text-writing AI later if results feel too generic. Bonus: an AI that doesn't write text can't make things up.
- **Risks.** It is only a few days old, and its speed and accuracy claims aren't proven yet. The site the user first found (jevmodel.org) is an unofficial guide, so we use the official docs. There's no information on EU data storage yet, so we only send the visitor's quiz answers, never names or emails.
- **Decision:** test it, don't commit yet. When we prototype the matching, we'll run the same fake visitors ("test personas") through Jev and through a regular small AI model, then compare quality, speed and cost.

#### 10. New direction: local first, on a Raspberry Pi

the user's priority changed: first make it work **just for him, in a browser, at home**, and make it cool enough for his portfolio. Going public (domain, paying for other people's AI use) is decided later.

New setup:

```
Browser (laptop, same wifi) ──> Raspberry Pi 5: Web app ──> Matching engine ──> SQLite database
                                                                 │
                                                                 └──> Jev API (cloud, optional)
```

- **Everything runs on the Pi**: the web app, and the database as a single **SQLite** file.
- **Jev can't run on the Pi.** It's a closed model that only runs on its maker's servers, so the Pi calls it over the internet. Its free starter tokens are plenty for one person.
- **The matching engine has three options you can switch between:** (1) simple rules, with no AI, free and offline; (2) Jev; (3) later, maybe a small AI model running on the Pi itself. Comparing them becomes part of the project story.
- **Bonus:** if the rules engine is good enough, a public version could be a free static site with no AI costs at all.

📸 *Screenshot: the local architecture diagram.*

#### 11. First working version, built in one go

the user: *"Forget about slowly and tests. We can go fast."* So Claude built the whole first version in one session.

**Name (working title): Tapwise.**

What's inside:

- **Quiz**: 8 questions, one per screen. Single-choice answers move on by themselves. Every answer matches a field in the database (who it's for, where, what the tap should do, phone, smart home gear, how hands-on, tag conditions, free text).
- **Rules engine** (`app/engines/rules.py`): gives each idea points. It removes ideas that can't work (wrong phone, far too hard), subtracts points for ideas that need smart home gear you don't have, and adds points for matching places and goals, for words from your free text and for ideas explained by several creators.
- **Tag matcher** (`app/tags.py`): picks one of 10 hand-written tag types (`db/tag_profiles.json`) for each idea, plus a shopping list with copy-paste search terms.
- **Results**: top 8 ideas with why they fit, warnings, the business angle, the tag to buy, setup steps and every creator who explained it. Until real URLs are added, links open a YouTube search, and the anchor quote tells you what to listen for.
- **"Share an idea" form**: saved to SQLite, with a hidden honeypot field against bots.
- **Jev**: the engine switch exists; the Jev part is a placeholder until it's wired to the official API.
- **Runs on the Pi with Docker**, like n8n: `http://PI-LOCAL-IP:8080`, or through Tailscale from anywhere. See `RUN.md`.

Tested with fake visitors: a café owner got review tags, table menus and guest wifi, all with waterproof epoxy tags. An iPhone user who forgets vitamins got the pill tracker first. A maker got the Raspberry Pi attendance logger.

![Home](docs/img/10-app-home.png)
![Results for a café owner](docs/img/13-app-results-cafe.png)

Known weak spot: few business ideas in the data, so a café owner also sees a less relevant "for-sale sign" idea. More business sources will fix that.

#### 12. Version 2: ask about people's day, not about NFC

the user tested version 1 and spotted the big problem himself:

> *"What do you want NFC for?" → "Well, I don't know, that's why I'm here… what IS NFC for?"*
> *"Where would you use it?" → "No idea, what can it do in a car? Or an office?"*

The quiz asked people to already understand NFC, which is the very thing they come to find out. **New approach: ask about their everyday life, find the small annoyances, and connect those to NFC ideas.**

What changed:

- **"NFC in 20 seconds" intro** before the questions: a sticker, your phone reads it, something happens. That's all a visitor needs to know.
- **Questions about your day.** "First, a little about you" (desk job? car? kids? business?) decides which of the following screens appear: mornings, home, work, on the move, habits, business. Someone without a car never sees car questions.
- **A needs map (`db/needs.json`)**, the new heart of the project: 40 everyday annoyances ("I forget if I already took my vitamins", "Guests keep asking for the wifi password"), each linked to the ideas that solve it, with a short pitch written for that exact situation.
- **Free text works too.** "I can never find my keys" gets matched by keywords to the lost-and-found tag.
- **Results explain themselves**: *"You said you forget whether you already took your vitamins → Stick a tag on the bottle and tap it when you take one. Your phone keeps the record…"* Each card also says setup time, price and the tag to buy.
- **"Also popular with people like you"**: ideas they didn't ask for, but that fit their life.
- **"See what one tap can do"** on the home page: hand-picked examples per place (Home, Car, Desk, Health, Business) for people who just want to browse.
- **A logic fix**: for guest wifi, the *guests'* phones matter, not the owner's. So an iPhone owner still gets it, with a note.

Why this matters: the quiz no longer needs any NFC knowledge. It's a small version of what product designers do in user interviews: ask about behaviour and pain points, not about the solution.

Future Jev idea: turning someone's free text into needs ("which of these 40 annoyances does this sentence describe?") is exactly the kind of choice Jev is built for.

![Intro](docs/img/15-v2-intro.png)
![Mornings question](docs/img/16-v2-mornings.png)
![Results with explanations](docs/img/17-v2-results.png)

#### 13. Less text, more curiosity

the user's feedback on version 2: all cards open at once felt overwhelming. Changes:

- **One column, everything closed.** Each idea shows only a curiosity line ("Never wonder *did I take my pills?* again", "Movie night in one tap") plus setup time and price. Visitors open only what interests them.
- **"How to set it up" as a 4-step picture strip:** 🏷️ Get the tag → 📱 Set it up → 📍 Stick it → ✨ Tap. Step 2 changes with the visitor's phone: the Shortcuts app on iPhone, NFC Tools Pro or MacroDroid on Android, and NFC Tools for simple links.
- **Source icons:** each site's own favicon (YouTube, Reddit…) and 📖 for books.
- **Plain tag names** ("Basic NFC sticker" instead of "NTAG213"). The technical name only appears in the shop search term.
- **Clearer wording:** a keyfob can't record your voice; the phone does. A new intro card says "The tag is just a trigger".

![Results, closed](docs/img/19-v3-results-closed.png)
![One idea, opened](docs/img/20-v3-idea-open.png)

#### 14. 22 Reddit threads, and a branching quiz

the user searched Reddit (r/shortcuts, r/homeassistant, r/tasker, r/NFC, r/AutisticAdults…) and ran the same NotebookLM prompts: **239 raw idea entries** from 18 threads, this time with real links.

What happened to them (`scripts/batch_reddit.py`):
- **Every entry was sorted by hand**: linked to an existing idea, turned into one of **26 new ideas** (remember where you parked, did anyone feed the pet?, clock in and out, an emergency button, a treasure hunt, a care log…), or left out, with the reason written down (10 entries: e.g. "encrypted data" on a normal tag, hand implants, secret audio recording, copying game figures).
- **Credit goes to the right person.** On Reddit the idea often comes from a commenter, not whoever started the thread, so each link stores the commenter's name and the site shows "u/name". Deleted accounts are shown as "a member of r/…".
- **Popular ideas are now clearly popular**: "did I take my pills?" is explained by 9 people, which is useful for ranking.

Database now: **108 ideas (101 shown), 45 sources, 436 idea–source links, 74 everyday problems ("needs")**. The last 4 threads came in a second run (55 entries): 2 new ideas (check the pet cam as you leave; pay with a ring or keychain) and 3 more left out (copying game figures, a cider dispenser, cloning a work access card).

**The quiz became branching**, as planned in step 12's follow-up: screen 1 asks about your life, and each "world" only appears if it's relevant:

| World | Shown to |
|---|---|
| Mornings and evenings, At home, Out and about, Habits and health | everyone |
| With the kids / Your pets / Plants and garden | people with kids / pets / plants |
| Your smart home | people with smart gear |
| Work and study | desk workers, home office, students |
| In the car | drivers |
| Hobbies and fun | people with hobbies |
| About your business | business owners, or people who want to earn money with NFC |

A pet owner who drives now sees 7 short screens; a café owner sees a business screen that others never see.

![Branching quiz: hobbies screen](docs/img/21-v4-branching-hobbies.png)

---

## Open to-do list

- [ ] the user reviews the 43 flagged ideas
- [ ] Prototype matching: Jev vs. a small general AI model, on the same test personas
- [ ] Find the URL of each source (title + channel search), the user confirms
- [ ] Find timestamps using the anchor quotes (YouTube transcripts)
- [ ] Write the **tag profiles** table (the buying guide)
- [ ] Design the interview questions
- [ ] Prototype the AI matching with test answers, before building any UI
- [ ] Build the site; decide hosting
- [ ] Add more sources (the database is home-heavy; few business and workplace ideas yet)

## Before going public (checklist)

Visitor suggestions flow: pending → the user gets notified (n8n) → review on a password-protected admin page → approved ideas cleaned up like NotebookLM ones → published with "Suggested by …" credit if allowed.

- [ ] Lock `/api/suggestions` (currently readable by anyone who can reach the site, including emails)
- [ ] Admin review page behind a password (approve / reject / duplicate)
- [ ] Notification of new suggestions via n8n (already running on the Pi)
- [ ] Cloudflare Turnstile + rate limit per visitor on the suggestion form
- [ ] Privacy note next to the form (what is stored, why, for how long); delete emails after replying
- [ ] Daily backup of `nfc.db` off the Pi's SD card (submissions exist only there)
- [ ] HTTPS + a domain (or another host); decide who pays for AI usage (rules engine needs none)

## Screenshot checklist (for the README)

Save in `docs/img/` with these names:

- [ ] `01-first-questions.png`: the four scoping questions
- [ ] `02-architecture.png`: architecture diagram
- [ ] `03-notebooklm-sources.png`: the notebook with all sources
- [ ] `04-notebooklm-output.png`: NotebookLM producing JSON
- [ ] `05-database-sample.png`: a few ideas in the cleaned database
- [ ] later: interview page, results page, submission form, live site

## Lessons so far

1. **Ask questions before building.** Four answers on day 1 shaped the whole design.
2. **Don't let the AI invent product names.** The AI describes needs; a hand-checked table picks the product.
3. **Ask AI tools for structured data** (JSON with fixed fields), in small batches.
4. **AI extraction makes mistakes.** Some "ideas" were unsafe or wrong. Everything gets checked.
5. **Credit creators.** Link to them, name them, never copy their content.
7. **Test with a real person's eyes.** the user read "Capture an idea by voice" next to "You need: NFC keyfob", googled the keyfob and found no microphone. The phone does the listening; the tag only starts it. Fixed the wording and added an intro card: "The tag is just a trigger."
6. **New tools: test before trusting.** Check the official source (not a fan site), test on your own data, and compare against an alternative.
