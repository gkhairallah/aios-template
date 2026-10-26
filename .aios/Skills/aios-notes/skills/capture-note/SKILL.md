---
name: capture-note
description: Create a properly-structured AIOS/Obsidian note from a plain-language instruction. Use when the user says "make a note", "capture this", "add this to my vault", "add to my second brain", "log this in Obsidian", "create a project/area/decision/knowledge note", or wants to file an idea, meeting takeaway, decision, or reference into their AIOS vault. Classifies the note via the Filing Rules, drafts it per the vault Conventions, suggests links, asks only about genuine gaps, and writes it after approval.
unlisted: true
---

# Capture Note

Turn a plain-language instruction into a correctly-filed AIOS note. Make the filing decisions FOR
the user, ask only what cannot be inferred, and never write a file without explicit approval.

## When to use
Trigger whenever the user wants to capture something into their AIOS / Obsidian vault: a note,
idea, decision, meeting takeaway, project or area update, or reference material. Typical phrases:
"make a note…", "capture this…", "add this to my second brain…", "log this…", or the `/note` command.

## Step 1 — Load the conventions (the source of truth)
Before drafting, load the vault's own rules so the note matches exactly:
1. **Resolve the vault fast:** read `~/.aios/config.json` and use its `vaultPath` directly — do **not** search the filesystem. If that file is missing, ask the user for the vault location (or have them run `/aios-init`) and save it there for next time. The vault is the folder containing `30 Atlas/` and `Templates/`.
2. Read `30 Atlas/Conventions.md` and `30 Atlas/Filing Rules.md` from the vault. These are authoritative — mirror them verbatim.
3. If they are missing (a brand-new vault), fall back to the bundled copies in `references/conventions.md` and `references/filing-rules.md`.

Never invent frontmatter fields or section headers — reproduce exactly what the conventions define.

## Step 2 — Classify (Filing Rules cascade — first YES wins)
Determine the note's `type` and destination folder:
- Just happened / fleeting thought → append to **today's daily log** in `00 Calendar/` (do not create a standalone note).
- WORK, has a done-state → `type: project` → `10 Efforts/`
- WORK, ongoing standard/responsibility → `type: area` → `10 Efforts/` (a *business hub* → `10 Efforts/Companies/`)
- KNOWLEDGE the user authored → `type: atlas` → `30 Atlas/`
- KNOWLEDGE collected from elsewhere → `type: resource` → `40 Resources/`
- A decision → `type: decision` → `30 Atlas/Decisions/`
- A map/hub of links → `type: moc` → `30 Atlas/MOCs/`

Tie-breakers: torn between Work and Knowledge → choose **Knowledge**. Still unsure → propose the daily log.

## Step 2.5 — Find the right home (append vs. new note)
Before drafting a *new* note, check whether this belongs in an *existing* one — avoid creating trivial one-liner notes:
1. Search the vault for notes on the same subject (title match, shared tags/`entity`, related links, the relevant company hub or project).
2. Choose the best home:
   - **Append to an existing note** when the content extends it (a new instruction for an existing module, a fact about an existing project) — propose *which* note and *which* section (usually `📝 Notes`, or a relevant heading). Insert it in place rather than making a standalone note.
   - **Create a new note** only when it's a durable, standalone topic with no good existing home.
   - **Daily log** when it's fleeting and not yet durable.
3. Present the recommendation ("append to [[X]] under Notes" vs. "new note") and let the user choose. When a clear home exists and a standalone note would be trivial, default to appending.

## Optional — gather supporting context
If the note would clearly benefit from company context (a meeting note, a project/decision that
touches email, SharePoint, or Teams) **and** connectors are available, **offer** to pull it via the
`gather` skill before drafting — ask first, keep it targeted; never auto-search. Fold what you find
into the draft (link SharePoint docs; distill emails/Teams; add calendar context).

## Step 3 — Draft the note (or the addition)
Build from the matching file in `Templates/` plus the Conventions:
- **Frontmatter:** set `type` and every field that applies to that type (status/priority/deadline/area for projects; review for areas; date for decisions and daily logs; created for evergreen notes; `entity` as a **list** when it belongs to a business; `tags` last, with the type as the first tag).
- **Body:** use the exact section headers the conventions specify for that type.
- **Canonical-source doctrine:** if the real artifact lives elsewhere (Git, SharePoint, a URL, Quickbase), **link it** under `🔗 Canonical Sources` and summarize — never paste a duplicate. If the source is a chat/conversation, distill the substance so the note stands alone without it.
- **Suggested links:** search the vault (existing note names, the relevant company hub, related efforts, people) and propose `[[links]]` under `🔗 Related`. Suggesting a link whose target doesn't exist yet is fine.
- **Title:** the note's name; the H1 and the filename match.

## Step 3.5 — Spot embedded decisions (confirm, don't just ask)
While drafting, scan the input and the draft body for decision-shaped statements — a real choice
made among alternatives, not just a fact or task. Signals: "chose/decided/opted for X over Y",
"instead of", "rather than", "in order to avoid", a stated tradeoff, "zero regression by
construction," a named alternative that was rejected or deferred. A plain status update or a task
("email the vendor") is not a decision — don't manufacture one that isn't there.

For each one found:
1. Draft a compact `type: decision` note from `Templates/Decision.md` — infer Problem / Options /
   Decision / Reasoning / Tradeoffs from context. A one-line Options/Tradeoffs is fine for a small,
   already-obvious call; don't pad it out to look more deliberated than it was. Leave `Follow-up`
   empty unless the input names one.
2. Set `related:` to link back to the project/area/atlas note being created or amended, and add the
   matching `[[Decision Title]]` link under that note's own `🔗 Related`.
3. Keep the full narrative in the parent note's body too (Step 3's draft) — the Decision note is an
   index entry that feeds the `🧠 Decisions` Dataview, not a replacement for the story.

Show every spotted decision alongside the main draft in Step 5's single approval pass — never a
separate round-trip per decision, and never an open question like "was this a decision?". Propose it
concretely ("this also reads like a decision — I'll file it as [[Title]], ✅/❌?") so the user is
confirming a concrete draft, not authoring one from scratch.

## Step 4 — Interview for the gaps (genuine unknowns only)
Infer everything you reasonably can from the instruction. Then ask the user ONLY about fields you
cannot infer and that matter — grouped into one concise round. Common gaps:
- Which business does this belong to (`entity`), or is it personal (leave blank)?
- Deadline and priority? (projects)
- Should the substance live in the note, or just link out to the source?
- Any specific notes or people to link?

Skip any question the instruction already answers. Do not interrogate — a couple of targeted questions, not a form.

## Step 4.5 — Write-through (mandatory, per Conventions § ⏳ Snapshots vs Living Notes)
A capture is **two writes, not one**. Before presenting the draft, work out what the new information
makes *false* elsewhere:
1. **The snapshot** — the new note, dated block, or daily-log entry. Immutable once written.
2. **The living surfaces it changes** — on every `created:` note this capture touches: frontmatter
   (`status`, `priority`, `deadline`), `🎯 Outcome`, `📌 Current Focus`, `🔗 Canonical Sources`, and
   the `📝 Notes` bullets.

Superseded `📌 Current Focus` lines are **removed or rewritten, never stacked** — that section holds
no history. A resolved blocker, a changed owner, a passed date, a closed dependency: delete it, don't
append beneath it.

Present both parts in the **same approval** (Step 5) — the snapshot and every living-surface edit,
each with its destination. Never edit an existing dated block to reflect new events; if a *past*
snapshot was factually misrecorded (not merely superseded), correct it visibly with
`[corrected YYYY-MM-DD: was "X"]` or a `> [!failure]- Correction — YYYY-MM-DD` callout, and say so.

## Step 5 — Approve, then write
1. Show the **complete** drafted note (frontmatter + body) and the destination path.
2. If Step 3.5 spotted any embedded decisions, show each Decision-note draft directly beneath the
   main note **in this same message** — one combined approval, not sequential prompts.
3. **Explain your reasoning** — briefly state *why* for each significant decision (type, append-vs-new home, entity, key links). This transparency is intentional while the workflow is being tuned; it can be shortened or removed later by editing this line.
4. Wait for explicit approval; apply any requested edits (including dropping a spotted decision the user disagrees with).
5. On approval, write the file(s) into the correct folder(s) using each note's title as the filename (`.md`), **and apply the Step 4.5 living-surface updates in the same pass**. Confirm where it will surface (e.g. dashboards, the company cockpit, the `🧠 Decisions` Dataview on the parent note).

Never write before approval.

## Notes
- One note per idea — don't over-split. Fleeting thoughts stay in the daily log until they earn a durable identity.
- A submitted note can spin off zero, one, or several Decision notes — spotted automatically per Step 3.5, always shown for confirmation before writing, never invented from nothing.
- Leave `🧠 Decisions` and `🗒️ Log` Dataview blocks exactly as the template has them — they self-populate; don't hand-fill.
- Respect `Private/` — never place notes there unless asked, and don't read it for link suggestions unless asked.
- Filename rule: match the H1 title; avoid characters that break links.

## References
- `references/filing-rules.md` — fallback copy of the decision cascade.
- `references/conventions.md` — fallback copy of the frontmatter + section-header standard.
