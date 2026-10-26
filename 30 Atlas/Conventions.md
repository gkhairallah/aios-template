---
type: atlas
created: 2026-01-01
tags: [atlas, doctrine, meta]
---
# 🧱 AIOS Conventions — the nomenclature standard

The single source of truth for how notes are structured, so nothing drifts. Every template
follows this; when in doubt, match it. See also [[Filing Rules]].

## Frontmatter fields
| Field | Applies to | Values |
|---|---|---|
| `type` | every note | `daily-log` · `project` · `area` · `atlas` · `resource` · `decision` · `moc` |
| `status` | project | `active` · `on-hold` · `done` |
| `status` | decision | `proposed` · `decided` · `superseded` |
| `priority` | project | `high` · `medium` · `low` |
| `deadline` | project | `YYYY-MM-DD` |
| `milestones` | project (optional) | **list** of `YYYY-MM-DD — label` (prefix `🔴` = irreversible) |
| `area` | project | `"[[Area]]"` (optional functional grouping) |
| `review` | area | `weekly` · `monthly` · `quarterly` |
| `entity` | any note (optional) | **list** of your business slugs (e.g. `company-a`, `company-b`) + `shared`. See below. |
| `created` | evergreen notes | `YYYY-MM-DD` (project, area, atlas, resource, moc) |
| `date` | time-anchored notes | `YYYY-MM-DD` (daily-log, decision) |
| `source` | atlas, resource | free text / URL |
| `related` | any (esp. decision) | list of `[[links]]` |
| `tags` | every note | array; first tag = the type; **always the last field** |


## `deadline` vs `milestones` — one field for the alarm, one for the ladder
A project with several hard dates has only ever had **one** `deadline`. Set to the *final* date, every
earlier cliff hides in prose and nothing surfaces it until it has already passed.

**`deadline` = the next date with a consequence.** Not the last one. **Roll it forward** as each date
lands. Every existing query — Due in 14 Days, Overdue, Days Left — keys off this field and keeps
working unchanged, which is the point: the alarm stays single-valued and reliable.

**`milestones` = the whole ladder**, so rolling `deadline` forward never loses a date:
```yaml
deadline: 2026-09-30
milestones:
  - 2026-09-04 — vendor confirmation of receipt due
  - 2026-09-25 — decision must be firm
  - 2026-09-30 — 🔴 early-transition discount expires
  - 2026-12-31 — 🔴 platform end-of-life
```
- **Plain strings with a leading ISO date**, `—`-separated. Human-readable in the file, and `dataviewjs` parses the date off the front. Deliberately *not* nested objects: the ladder is read far more often than it is queried, and legibility in the note wins.
- **`🔴` marks irreversible** — a date that cannot be renegotiated once passed. Anywhere in the string.
- Past milestones **stay in the list.** It is the ladder, not a to-do list; ticking is not its job.
- The list is the source; a `📌 Current Focus` table restating it is optional and for reading.

**Decisions have no due-date field.** A decision that must be resolved by a date belongs to a project
whose `deadline`/`milestones` carry it. Do not invent a date field on `type: decision`.

## `entity` — the single business axis
Ties a note to a business. It is a **list**, so a note can belong to more than one. Define your
own slugs (one per business you run) and use them consistently:
- One business → `entity: [company-a]`
- Two businesses → `entity: [company-a, company-b]`
- Company-wide / applies to all (shared values, shared staff) → `entity: [shared]`
- **Personal / not business → leave blank.** Presence = business; absence = personal.

### 🔒 Personal stays personal: kept in the vault, kept out of work output
The vault is a whole-life second brain. Personal material (health, feelings, energy, family, home, money) belongs here and is never held back for privacy reasons, because the vault is private. If data is ever shared with a team, fork it into a separate vault rather than opening this one.

1. **Personal = blank `entity`.** A daily-log row whose Project/Area column says *Personal* or *Home*, or links to a personal note, is personal too. So are events from personal calendars and mail in the personal inbox.
2. **Work-facing output leaves it out.** That covers team meeting prep, drafts for anyone else, `find` answers to work questions, and anything that goes out through `gather` or `act`. Personal material appears there only if the owner explicitly asks.
3. **When unsure, leave it out.** A note that's missing an `entity` tag is treated as personal until it's tagged.
4. **Owner-only surfaces stay whole-life, but personal items get their own fold.** Morning briefs and day wraps put personal items inside a nested, collapsed `🏠 Personal` callout, so the parent can be expanded on a screen share while the personal fold stays shut. A work section may name a conflict neutrally ("12:00 conflict, see 🏠 Personal") without the details. **In the daily log itself**, personal entries go into one collapsed `> [!quote]- 🏠 Personal` callout directly below the Hourly Log table (callout-safe bullets, never table rows), not into the Hourly Log, Worked On or Evening Review.
5. **`Private/`** stays untouched unless the owner asks.

Query pattern (built into the company hubs): a note surfaces for a business if it names that
business **or** is `shared`:
```
WHERE contains(entity, "company-a") OR contains(entity, "shared")
```
An **area is a company hub** when its `entity` is a *specific* business; it's a *cross-company
function* when `entity: [shared]`.

### 🤐 `[candid:: …]` — the off-the-record aside
Vault entries are written for their owner, so they can say the true thing: that a vendor is slow, that a
call went badly, that a chore wasn't worth the time. Those asides are the reason the record is worth
keeping, and they are also the reason it cannot be read over a shoulder.

1. **Wrap the aside, not the fact.** `[candid:: …]` holds the opinion, the irritation, the private read. The fact it hangs off — the time, the outcome, the decision — stays outside the field and is never dropped.
2. **Stripped from any output that isn't the owner's own eyes.** Huddle and meeting prep, drafts for anyone else, `find` answers to work questions, anything going out through `gather` or `act`, and any request for a **discreet**, **sanitized** or **shareable** version. Strip the field and its contents, leave the sentence around it intact, and never paraphrase it back in.
3. **Independent of the 🏠 Personal fold.** A candid aside on a work row is stripped the same way; a personal row is still personal whether or not it carries one.
4. **When unsure, strip it.** A reader who was going to see it will ask.

## Standard section headers
- **Project:** 🎯 Outcome · 🔗 Canonical Sources · 📌 Current Focus · 🧠 Decisions · 📝 Notes · 🗒️ Log · 🔗 Related
- **Area:** 🎯 Standard · 🔗 Canonical Sources · 🚀 Active Projects · 🧠 Decisions · 📝 Notes · 🗒️ Log · 🔗 Related
- **Atlas:** 📄 Summary · 📝 Notes · 🔗 Related
- **Resource:** 🔗 Source · 📝 Key Points · 🔗 Related
- **Decision:** ❓ Problem · ⚖️ Options Considered · ✅ Decision · 💭 Reasoning · ⚠️ Tradeoffs · 📌 Follow-up · 🔗 Related
- **MOC:** 🗂️ Notes · 🔗 Related

## Rules
- **Every note ends with `## 🔗 Related`** — a bulleted list of `[[links]]`.
- **`🔗 Canonical Sources`** = link to where the real artifact lives (Git, SharePoint, etc.); never paste a duplicate.
- **`🧠 Decisions` and `🗒️ Log` are live Dataview** — self-populate; don't fill by hand.
- **Emoji headers everywhere**, one per header.

## 🔗 Cite a source, always deep-link it

**Standing rule: whenever a note draws on an email, the Canonical Sources entry must carry a
clickable deep link to that exact message — not just a description of it.** Sender, subject and date
identify a message; they don't get you back to it. Six months on, "the renewal email from the vendor" is a
search; a link is one click.

**Where to get the link:**

| Source | Link to use |
| --- | --- |
| Outlook / Microsoft 365 | the `webLink` field returned with the message (`https://outlook.office365.com/owa/?ItemID=…`) |
| Gmail | `https://mail.google.com/mail/u/0/#all/<messageId>` |
| Teams message | the `webUrl` on the message, or `https://teams.microsoft.com/l/message/<chatId>/<messageId>` |
| SharePoint / Coda / Quickbase | the canonical item URL — link it, never copy the contents in |

**Format:** `- **Outlook** — [*"Exact Subject Line"*](webLink), Sender → Recipients, YYYY-MM-DD H:MM AM TZ`

This applies to every skill that gathers — `gather`, `capture-note`, `vault-ops`, the daily brief.
If a link genuinely can't be obtained, say so in the note rather than silently leaving a bare
description.


## 🤖 Agent-authored messages carry attribution, always

**Standing rule: when an agent sends a message outward on my behalf through a connector that
authenticates as me, the message opens with an attribution line. No exceptions, no channel
exemptions.**

Write connectors run on **delegated auth** — Teams, Outlook, Slack, the help desk. The provider API
does not distinguish "I typed this" from "an agent acting as me posted this", so the message lands
under my name, my avatar, my read receipts, and the recipient has no way to tell. That is fine for a
draft I reviewed and sent; it is not fine for anything an agent composed and delivered on its own.

**The format:**

```
🤖 From <Name>'s Assistant

<message body>
```

Bold first line on its own, blank line, then the body. **Pick one string and never vary it** —
recognizability is the whole point, so it must not get reworded per channel or per agent.

**Applies to:** chat messages and channels, outbound mail, ticket replies, any comment an agent
posts into a shared surface. **Does not apply to:** a draft handed back for review and sent by hand,
since at that point the human is the author.

> [!warning]- ⚠️ Why this is a rule and not a nicety
> Learned on a first agent-posted chat message into a group thread of senior colleagues. The body opened with "this is an AI assistant writing" — but the client rendered the whole message under the **human's name and avatar**, so the only thing separating an agent post from a real one was a sentence a reader could skim past.
>
> **The failure mode is not embarrassment, it is authority.** A message that appears to come from a principal carries that principal's weight: a leadership channel reads a posted opinion as a decision. An agent-composed line about a customer, a price, or an incident, landing under their name with no marker, is one skim away from being actioned as though they had said it.
>
> Attribution inside the body is not sufficient. It has to be the **first thing rendered**, above the fold, before any content.

## ⏳ Snapshots vs Living Notes — the mutability rule

Every note is one of two things, and which one decides whether it may ever be edited after the day
it was written.

- **Snapshot** — a record of *what was true, or what I knew, at one moment*. Its value is that it is fixed. Frontmatter marker: **`date:`** (`daily-log`, `decision`).
- **Living note** — a projection of *what is true now*. Its value is that it is current. Frontmatter marker: **`created:`** (`project`, `area`, `atlas`, `resource`, `moc`).

The `date:` / `created:` split in the frontmatter table above is not cosmetic — **it is the
mutability flag.**

### The two obligations
1. **Never retro-edit a snapshot.** Not a generated daily brief, not an hourly log row, not a dated recap callout, not a decision's reasoning. It said what it said.
2. **Never let a living note go stale.** Status, dates, deadlines, owners, blockers and open questions must match reality *today*. A living note carrying last month's blocker is a defect, not history.

### Write-through — the clause that makes this work
**A snapshot and the living notes it affects are written in the same pass, never separately.**
Capturing a meeting recap into a hub and leaving the affected project's `📌 Current Focus` untouched
is worse than not capturing it at all: the new truth is now buried in a block you've forbidden
yourself to edit, while the note you actually read still says the old thing.

So every capture is two writes:
- the snapshot (dated block, daily log), **and**
- the living surfaces it changes — frontmatter (`status`, `priority`, `deadline`), `🎯 Outcome`, `📌 Current Focus`, `🔗 Canonical Sources`, and the `📝 Notes` bullets.

Superseded lines in `📌 Current Focus` get **removed or rewritten**, not stacked. Current Focus is
the one section with no history in it.

### The mixed cases
Dated `### YYYY-MM-DD — …` sections and dated callouts *inside* a living note are snapshots. The
note is living; those blocks are not. Append new ones; never revise old ones.

Conversely, two things inside `date:`-anchored notes are **living** and must stay current:
- **A decision's `📌 Follow-up` checkboxes** — a live task list. Tick them.
- **A decision's `status`** — `proposed → decided → superseded`, plus a `related` link to whatever superseded it. Superseding a decision means **a new decision note**, never a rewrite of the old one's `⚖️ Options Considered` or `💭 Reasoning`.

### Supersede and fold — never delete
When something is overtaken by events it is **moved and marked, never removed**. Superseded tracks,
retired plans, closed options and old decisions fold into a dated timeline under `📝 Notes`, flagged
with what superseded them and when.

**This is a hard rule, not tidiness.** The record of what we believed, when we believed it, and what
changed it **is evidence**. In a dispute — commercial or legal — the timeline *is* the argument. A
note showing only the current position cannot demonstrate that a decision was reasonable when it was
made, or that a counterparty's advice changed under us. Deleting a dead option destroys the proof
that it was ever live.

- **Decisions keep their own note.** Flip `status:` to `superseded`, add a `> [!info] ⛔ Superseded YYYY-MM-DD by [[...]]` callout at the top stating what replaced it and why, and leave it in `30 Atlas/Decisions`. Never rewrite its `⚖️ Options Considered` or `💭 Reasoning` — those are the record of the reasoning at the time, which is the whole point.
- **Effort-note content** — tracks, plans, focus items — folds into `📝 Notes` under a dated heading (`### Retired tracks`, `### Delivery timeline`), **verbatim**, with a note saying where it came from and when.
- **Where a chain of decisions exists**, index it in the effort note as a **decision timeline**: date · status · one line · link. The index carries the shape and the sequence; the decision notes carry the substance. Don't restate the reasoning in the index.

### Stale ≠ wrong — the only in-place correction allowed
| Case | Meaning | What to do |
| --- | --- | --- |
| **Stale** | Accurately recorded, since superseded by events | **Never touch it.** New truth → new dated block + update the living surfaces. |
| **Wrong** | Misrecorded what was true at the time — bad figure, wrong name, broken link, transcription error | **Correct in place, visibly.** A falsehood in the audit trail serves nothing. |

Never correct silently:
- Inline, small: `[corrected 2026-08-12: was "$2,500"]`
- Substantial: a `> [!failure]- Correction — YYYY-MM-DD` callout beneath the block.

### When they disagree, the living note wins
A snapshot that contradicts a project note isn't wrong — it's **old**. Read current status from the
living note, always. Snapshots answer a different question: *when did this happen, and what did I
know at the time?*

Retrieval consequence: **never answer "what's the status of X?" from `00 Calendar`.** Answer from the
effort note; cite the daily log only as evidence of timing, or of what was known then.

## ✅ Tasks — capture is dated, tracking is living

**A checkbox is mutable state; a daily note is immutable. Both cannot be true of the same
checkbox.** That contradiction is what this section resolves, and it resolves it the same way
§ ⏳ Snapshots vs Living Notes resolves everything else:

> **The daily note is where a task is *captured*. The owning effort note is where it *lives*.**

### The three rules
1. **Capture with a dated daily-note link, never a floating tag.** `- [ ] Call the vendor back [[YYYY-MM-DD]]` *(the actual date, e.g. `[[2026-03-14]]`)* — the date travels with the task, so it can age. Write it wherever you are: the daily note, an effort note, an area note. The link is what makes it show up in that day's capture list. **`#today` is retired**. It encoded intent, not a date, so it could never expire — a task tagged `#today` in July was still `#today` in September. Do not reintroduce it or any other undated task tag.
2. **Promote before the day closes, or accept that it is only history.** A task still sitting in a daily note is **captured but unowned.** Move it into the owning note's `📌 Current Focus` (project/area) or `📌 Follow-up` (decision) — that copy is the one that gets tracked, ticked and reviewed. Leave the daily-note line as the historical record of when it was raised; **don't maintain two live copies.**
3. **The rolling "what's open" view is a dashboard, not a daily note.** → [[Tasks Dashboard]]. A live query inside a `date:` note makes an immutable note render today's state, which breaks rule 1 of the mutability section. The daily note's task query is therefore **scoped to its own date and nothing else.**

### The query, and why it is scoped
```dataview
TASK
WHERE !completed AND (contains(text, this.file.name) OR file.path = this.file.path)
```
`this.file.name` is the note's own date, so each daily note matches **only tasks carrying its
date**, plus any checkbox written in the note itself. Reopening a note from three months ago shows
what *that day* captured — a snapshot, as intended.

**`length(text) > 2` is not optional.** The `🎯 Top 3 Today` scaffold is three **empty** `- [ ]`
boxes and Dataview parses every one as a task — typically **several times more blank placeholders than real tasks**. Without the filter, any task query touching `00 Calendar` is
~84% noise, which is how the first version of this section's own dashboard nearly recreated the
problem it was written to fix. **Carry the filter on every task query that reads a daily note.**

> [!warning]- ⚠️ Why the query is scoped — the failure this section exists to prevent
> A tempting first version is `TASK WHERE !completed AND contains(text, "#today")` — **no date filter and no file scope**, so every daily note renders the identical vault-wide list of every unchecked task ever tagged. A note from three months ago displays today's state.
>
> It fails twice over. An undated tag like `#today` **encodes intent, not a date, so it can never expire** — and because the view it produces is unusable, the habit quietly dies, usually within weeks.
>
> **The subtle cost is the one that matters.** Most entries in such a list turn out to be *echoes* of work already tracked properly on its own effort note. The few that aren't — genuine orphans with no owner anywhere — **hide inside that noise.** A bad task view doesn't just add clutter; it conceals the exact items nothing else is watching. That is the whole argument for rules 2 and 3.

### The one-time migration
Pre-doctrine checkboxes left sitting in old daily notes should **not** be ticked — ticking claims work
was done. Convert each to a **struck line carrying a dated disposition**, which removes it
from `TASK` queries while preserving what was written, per § Supersede and fold. Dispositions used:
**retired here** (already tracked on a living note), **promoted** (given an owner), **dropped**
(dead, and deliberately not promoted — if it returns it returns as a fresh capture).

**Use the same pattern for any future daily-note checkbox that needs closing out without being
done.** Never tick a box to silence it.

### Where a task is allowed to live
| Location | Live checkbox? | Why |
| --- | --- | --- |
| **Project / area `📌 Current Focus`** | ✅ Yes — the home | Living note. This is the tracked copy |
| **Decision `📌 Follow-up`** | ✅ Yes — the exception | Belongs to that decision and nowhere else |
| **Daily note** | ⚠️ Capture only | Snapshot. Fine on the day; promote it or it's just history |
| **Atlas / resource note** | ❌ No | Reference material doesn't own work |

### 👀 Mine vs Watching: ownership is a field, not a feeling
**A checkbox with no owner is the operator's. A checkbox with `[owner:: [[Person]]]` naming someone
else is a watch item:** the operator monitors it and raises it with that person; they do not do it.

```markdown
- [ ] Ship the release [[YYYY-MM-DD]]
- [ ] 👀 Vendor call invite [owner:: [[Teammate]]] [[YYYY-MM-DD]]
```

1. **Default is mine.** Only watch items carry `owner::`. The 👀 prefix is for scanning; the **field** is what queries read.
2. **Shared-mailbox items default to watch**, with the owner taken from a per-mailbox default-owner table, unless the operator is named on the thread.
3. **Escalation threshold:** flag after 5 business days without movement, 2 if customer-facing, unless the item carries its own `[escalate:: YYYY-MM-DD]`.
4. **Ticking:** tick when the **owner** closes it. When raised, append `[raised:: YYYY-MM-DD]`.
5. **Views:** the Tasks Dashboard shows *mine* (`!owner`) plus a **👀 Watching** panel grouped by owner, which doubles as the 1:1 agenda.
6. **Briefs and wraps split the output** into **🎯 Yours** and **👀 Watching, raise with…**.

## ↩️ Line wrapping — by context, because one rule does not cover every case

**The mistake this section corrects:** the vault was written as if "hard-wrap at ~100 chars" were a single global rule, and it is not. **Obsidian applies the setting that fixes hard-wrapping to *paragraphs only*.** Wrapping therefore renders correctly in some contexts and visibly broken in others — which is exactly how it presented: fixed in one place, broken in another, apparently at random. *(Learned the hard way — the symptom looks random until you realise the rule is per context.)*

**The rule is per context. Use this table, not a global habit.**

| Context | Hard-wrap? | Why |
| --- | --- | --- |
| **Plain paragraph** | ✅ Yes, ~100 chars | Joined into flowing text — *provided `strictLineBreaks` is ON*. Keeps git diffs line-level, which is the point of wrapping at all |
| **List item** (`-`, `1.`) | ❌ **Never — one line per item, however long** | 🔴 **`strictLineBreaks` does NOT apply inside list items.** Obsidian renders every newline in a list item as a `<br>` regardless of the setting. There is no setting that fixes this; not wrapping is the only fix |
| **Callout** (`>`) | ❌ **Never — one line per paragraph** | Two reasons: editing a wrapped `>` line leaves **orphan `>` characters** behind, and a bare empty line **terminates the callout** |
| **Table row** (`\|`) | ❌ Never | A row is one line by definition; wrapping breaks the table |
| **Fenced code** (```` ``` ````) | ➖ N/A | Line breaks are preserved verbatim and are usually meaningful |
| **YAML frontmatter** | ❌ Never | Not Markdown. `  - item` lists look like list items to naive tooling — see the tooling warning below |

### The setting that paragraphs depend on
**`Settings → Editor → Strict line breaks` must be ON.** With it **OFF — Obsidian's default** — every single newline renders as a visible `<br>`, so even paragraph wrapping breaks. **Obsidian is the outlier, not the vault:** CommonMark and GitHub's `.md` rendering both join single newlines.

Change it **in the UI**, not in `.obsidian/app.json` — Obsidian holds settings in memory and rewrites that file, so a file-level edit made while the vault is open gets clobbered. *(The AIOS Template ships with `"strictLineBreaks": true` so a fresh vault is correct before it is ever opened. Do not drop that key.)*

**With it ON, an intentional single break must be explicit** — `<br>` or two trailing spaces. Applies to things like an email sign-off (`Thanks,` / `Alex`), which otherwise collapses onto one line.

> [!warning]+ ⚠️ Hard-wrapping silently breaks wikilinks — the consequence nobody looks for
> A `[[Note Name]]` split across a wrap point is a **dead link**. It does not error, it does not show as unresolved in a useful way, and it will not appear in backlinks or Dataview — it simply is not a link any more.
>
> This is easy to create and very hard to notice — the link simply stops existing. **Never let a wrap point fall inside `[[ ]]`.** Worth an occasional grep: `\[\[[^\]]*\n[^\]]*\]\]`.

> [!danger]+ 🛠️ If you write tooling that reflows Markdown — two traps worth knowing before you start
> **1. Skip YAML frontmatter.** `  - acme` in frontmatter is indistinguishable from a Markdown list item by pattern alone. A reflow script that joins list continuations **will corrupt frontmatter**, merging `entity`, `created`, `related` and `tags` into one line. Emit everything up to and including the closing `---` untouched.
>
> **2. Verify invariants before writing, per file.** Snapshot frontmatter, headings, table-row count, fence count, callout lines, wikilink set and URL set; compare after; **refuse to write on any mismatch.** Such a guard catches frontmatter corruption, and it will also surface dead wikilinks — the link set changes when a join *repairs* one. **A refusal is information, not just a safety net: inspect it, don't override it blindly.**

## 🗂️ Collapsible Sections (Callouts)
Use foldable callouts to keep long notes scannable — collapse supplementary detail so the
skeleton of the note stays visible at a glance. Not every paragraph needs one; reserve callouts
for content that's genuinely long, supplementary, or worth visually flagging.

**Fold syntax:** `> [!type]- Title` collapses by default, `> [!type]+` expands by default, no
marker = static (not foldable). Only renders foldable in Reading View / Live Preview, not Source
mode.

**Pick the type by what the content *is*, not by habit:**

| Type | Use for |
| --- | --- |
| `note` | general aside, background context |
| `abstract` / `summary` / `tldr` | a summary block at the top of a long note |
| `info` | reference detail, supporting data |
| `todo` | pending action items embedded mid-note |
| `tip` / `important` | a key takeaway worth flagging |
| `success` / `done` | resolved items, completed sub-work |
| `question` / `faq` | open questions, unresolved items |
| `warning` / `caution` | risks, blockers, things to watch |
| `failure` / `missing` | known gaps or things that didn't work |
| `danger` / `error` | hard stops, critical risks |
| `bug` | known issues / defects |
| `example` | illustrative example, sample data |
| `quote` / `cite` | verbatim excerpt from a source |

Default long/supplementary content to **collapsed** (`-`); leave short, essential content
uncollapsed or outside a callout entirely. Custom types (like `[!doc]` for attachments, below)
are fine too — Obsidian folds any type, recognized or not.

### ⛔ Never hard-wrap inside a callout — one line per paragraph

**Rule: inside a `>` callout or blockquote, each paragraph, bullet or table row goes on ONE
unbroken line, however long. Let Obsidian soft-wrap it. Do not wrap at 100 characters the way we do
in ordinary body text.**

**Why — the editing bug this causes.** Every line inside a callout must start with `>`. So a
paragraph hard-wrapped across four lines isn't one paragraph, it's four `>`-prefixed lines that
merely *render* as one. Reading View joins them, which is why it looks fine and the problem is
invisible until you edit. The moment you backspace at the start of a continuation line to pull it up,
the text joins but that line's own `>` prefix is left behind as literal characters mid-sentence — so
every tidy-up costs an extra deletion. Hard-wrapping is what plants those stray `>` marks.

**Outside callouts this doesn't apply** — ordinary body text has no line prefix, so backspacing joins
cleanly and the existing ~100-character wrap is fine. The rule is specific to `>` content.

- ❌ `> **Why not Green.** The commercial signal was good, but three unresolved` `> items are exactly the kind of thing that turns into a stalled deal.`
- ✅ `> **Why not Green.** The commercial signal was good, but three unresolved items are exactly the kind of thing that turns into a stalled deal.`

Same rule for the **daily-note Hourly Log table** and any other table: a table row is one line. And
per § 📎 Attachments, always leave a genuinely blank line between consecutive callouts, or Obsidian
merges them into a single blockquote.


## Subfolder policy
- **Subfolder only by deterministic TYPE / FUNCTION**, never by fuzzy TOPIC.
- **Scale by MOCs + search + Dataview, not nested topic folders.** Navigate by `[[links]]`, Quick Switcher, and MOCs.
- **Dated notes scale by date subfolders** (Daily Notes format `YYYY/MM/YYYY-MM-DD`).
- **Business separation is the `entity` property + a MOC, never company folders.**

## 🏢 Internal domains
Email domains whose people count as **internal** — your own company plus any sister companies or close
partners who sit in your internal meetings. The meeting-recap step reads this list: a meeting with only
these domains is internal (recapped only when tagged `#recap`); any other attendee makes it external.
Keep the real list here in your vault, never in the shared skill.

- `example.com`
- `sister-company.example`

## 📎 Attachments
Files attach under a note's `## 📎 Attachments` section. **Two tiers — nothing is ever public/guessable:**
- **Private / sensitive** → `Private/attachments/` — local-only, never pushed or uploaded.
- **Secured (default)** → private R2 served via a **non-expiring signed URL** (not guessable, revocable, renders in Obsidian, portable). Until R2 + the Worker are set up, defaults to `attachments/` in the private repo (interim). Config: `.aios/attachments.json`. Sharing = hand over the signed URL. Setup: see the Secured R2 runbook.

### Embed pattern by format (secured tier)
Raw `![](url)` only renders images. Everything else that can render in-browser goes in a
**collapsed callout** so it doesn't blow up the note — click to expand:
```
> [!doc]- 📎 report.txt
> <iframe src="<signed URL>" width="100%" height="600"></iframe>
>
> [⬇ Download original](<signed URL>&dl=1)
```
- **txt** → iframe points straight at the signed URL (browser renders plain text natively).
- **pdf** → **not** an iframe. Obsidian's Electron shell has a confirmed, long-standing bug where `<iframe>` cannot render PDFs at all (blank frame) — this isn't fixable via headers, CORS, or the Worker, it's an Electron limitation. Use the **`external-pdf` community plugin** instead, which renders through Obsidian's own bundled PDF viewer rather than an iframe:
  ```
  > [!doc]- 📎 report.pdf
  > ```external-pdf
  > <signed URL>
  > title: report.pdf
  > height: 600px
  > ```
  >
  > [⬇ Download original](<signed URL>&dl=1)
  ```
  Plugin isn't in Obsidian's official directory yet — install via **BRAT** (Settings → Community
  plugins → Browse → install "BRAT" → BRAT settings → Add Beta plugin → repo
  `tenebrisnox/external-PDF-plugin`). It explicitly supports direct HTTPS URLs with query strings
  (its own docs cite Paperless-NGX-style authenticated links), so our signed URLs are a
  supported case, not a workaround.
- **docx / xlsx / pptx** → browsers can't render Office formats at all; point the iframe at Office Online's viewer instead, with the signed URL URL-encoded as `src`: `https://view.officeapps.live.com/op/embed.aspx?src=<url-encoded signed URL>`
- **csv** → don't embed — Chrome/Firefox force-download CSVs even with correct headers. Plain link: `[report.csv](<signed URL>)`.
- **images** → keep the plain `![](<signed URL>)` embed, no callout — already compact, not disruptive.

**Two spacing rules, non-negotiable — learned from a real broken render:**
1. **A bare `>` line between the embedded content (`<iframe>` or the fenced ` ```external-pdf ` block) and the download link, inside the same callout.** Both are block-level content that keeps consuming following lines until a blank line — skip this and the download link gets swallowed as literal text instead of rendering as a clickable markdown link.
2. **A genuinely blank line (no `>` at all) between one attachment's callout and the next**, when a note has more than one. Skip this and consecutive `>` lines merge into a single blockquote — the second attachment's `[!doc]-` header renders as inert text *inside* the first one's callout instead of starting its own, and everything after the first embed in that merged block breaks (for the same reason as rule 1, just worse).

**Download button:** all secured objects are stored `Content-Disposition: inline` so they render
in the viewer — appending `&dl=1` to the same signed URL tells the Worker to override that to
`attachment` for that one request, forcing a real download instead of an in-browser open. Don't
rely on the Office Online viewer's own built-in "Download a copy" — it's been unreliable with
signed/query-string URLs, hence the explicit link.

**Folding is a core Obsidian feature, not a plugin or specific to `[!doc]`.** The `-` right after
the callout type (`[!doc]-`) is what makes it foldable-and-collapsed-by-default; `+` would be
foldable-and-expanded; no marker = not foldable at all. `doc` itself is just an arbitrary label —
Obsidian doesn't ship a built-in `doc` callout type, it just falls back to a generic style for any
unrecognized type, folding included. Note: the fold only renders correctly in Reading View — raw
HTML inside a callout visually breaks in Live Preview/editing view. Not a bug, just how Obsidian
handles it.
