# Day Wrap — reconstruct an unlogged day from its sources

Load this **only** when wrapping a day (`/aios-notes:today wrap`, "wrap up my day", "fill in
what I missed", or a scheduled evening run). Not for a normal `/log` entry.

**The premise:** the operator rarely has time to write the day up while living it. The job is to
reconstruct what happened from the trail the day left behind, then hand back a **draft to correct,
approve or reject** — never a blank page and never a question like "what did you do today?".

---

## 1. Establish the day

- The day is the **operator's local date**, not the runner's. A cloud runner is usually UTC while
  the operator often is not (e.g. US Pacific), so late-evening local work carries the *next* UTC date. Get the
  operator's timezone from the host, convert, and pick the daily note by the **local** date.
- Resolve the vault from `~/.aios/config.json` → `vaultPath`. Locate `00 Calendar/YYYY/MM/YYYY-MM-DD.md`.
  Create from `Templates/Daily Note.md` only if genuinely absent.
- **Sweep the whole local day, every time. Diff by topic, not by time.**
  A logged block covers one *project*, not one *hour* — a day whose log reads 9:30–16:00 solid can
  still hide six unlogged threads inside that window, because the rows only describe what the
  operator was heads-down on. Windowing the sweep from the last logged timestamp misses all of them.
  So: sweep 00:00 local to now, then drop anything the log already covers (§ 2). The cost of the
  wider sweep is a few extra tool calls; the cost of the narrow one is missing most of the day.

## 2. Read the note first — it is the diff baseline

Read the existing `## ⏱️ Hourly Log`, `## 🔗 Worked On Today` and any morning brief callout before
touching a single source. Everything the sweep finds is then classified as **already logged**,
**partially logged** (a row with no outcome), or **missing**. Only the last two reach the proposal.
A wrap that restates the morning brief is noise and will train the operator to stop reading it.

**Match on subject, never on clock time.** A finding is already logged only when an existing row is
*about the same thing*. A row that overlaps it in time but concerns a different project is not
coverage — file the finding, and let the two rows sit at the same hour. Real days interleave.

## 2a. The quiet-day gate — and what must never gate it

A scheduled wrap may legitimately decide a day was quiet and stop: no draft, no notification. But
**the gate decides what gets looked at, so a cheap gate on the wrong signal silently deletes whole
days.** The failure is not theoretical: a Sunday that shipped nine releases with
no commit, no sent mail and no chat message was gated out as "quiet" by a three-check gate that
asked only *were there commits or messages?*

**The operator's deep work lands as FILES, frequently with nothing else attached all day.** So:

- **The changed-file probe (§ 3a pass 1) is the FIRST gate check and may never be demoted or
  skipped.** It is an mtime listing, not a folder inventory — one `find` per root, no file reading.
  It is cheap. It is also the only check that can see uncommitted work.
- **A dirty working tree is work.** `--no-optional-locks status --porcelain` on the repos the probe
  named, with the changed files' mtimes inside the window, counts as activity with zero commits.
- Commits, sent mail and chat are *additional* checks, never the whole gate. They are dense when
  present and silent by default.

Before judging the probe's output, discard known machine noise: `.DS_Store`, `*.xcuserstate` and
other IDE window state, the vault's `.obsidian/**`, the vault's own `00 Calendar/**` note for today
(the morning brief writes it unattended), and anything the vault's `vault backup:` commit touched.
If anything real survives, **the day is not quiet** — go to the full sweep.

⚠️ **A probe that cannot run is a failed gate, not a quiet day.** GNU `find -printf` fails silently
on macOS under `2>/dev/null`; BSD `stat -f` fails on Linux. An empty sweep and a broken sweep look
identical from the output, so confirm which `find` you are on before trusting emptiness, and report a
broken probe as a failure rather than reporting a successful empty run.

## 3. Sweep the sources, in this order

Resolve capability-first (see the `gather` skill) — use whatever this session actually has, never a
fixed tool list. Ordered by yield, highest first:

**a. Changed files in the connected folders — do this first, and do it in two passes.**
The roots are the operator's work folders — typically a repos folder and a synced working-docs folder
(e.g. **`~/REPOS`** and **`~/COWORK`**, the latter a symlink into iCloud Drive; in a Cowork VM both mount under `$HOME/mnt/`). This is the single highest-yield source
and the one nothing else replaces: deep work leaves files, not messages. Sweep **only what changed** —
never inventory the folders.

**Pass 1 — mtimes, to find out *where* the day happened.**

```
for ROOT in ~/REPOS/ ~/COWORK/; do   # trailing slash required: ~/COWORK is a symlink into iCloud Drive
  find "$ROOT" -type f -newermt 'YYYY-MM-DD HH:MM' \
    -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/.next/*' \
    -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/.venv/*' \
    -not -path '*/__pycache__/*' -not -name '*.log' \
    -print0 2>/dev/null | xargs -0 stat -f '%Sm %N' -t '%Y-%m-%d %H:%M' | sort
done
```

⚠️ **`stat -f` above is the macOS/BSD form, and it is deliberate.** `find -printf` is a GNU extension:
on macOS it fails, and with `2>/dev/null` it fails *silently* and prints nothing, so the sweep reports
an empty day instead of an error. On a Linux runner `-printf '%TY-%Tm-%Td %TH:%TM  %p\n'` is fine.
**Check which `find` you are on before trusting an empty result** — a sweep that finds nothing and a
sweep that cannot run look identical from the output.

⚠️ **`-newermt` reads the *shell's* timezone**, and a cloud runner is UTC while the operator usually
is not. For US Pacific, local midnight is **07:00 UTC** (PDT) or **08:00** (PST) — convert, or the sweep silently
starts seven hours late and the morning vanishes. Pin the offset for free: the vault's own backup
commits carry **local** time in the message (`vault backup: YYYY-MM-DD HH:MM:SS`) against a UTC commit
date.

**Pass 2 — git, on *every* repo pass 1 touched.** This is where most of the value is, and it is the
easy step to under-run: a repos root often holds **dozens of repos**, so scanning only the two or three already in
mind will miss whole threads. **Let pass 1 name the set, then scan all of them.**

```
git -C <repo> log --since='<local start>' --until='<now>' \
  --date=format-local:'%m-%d %H:%M' --pretty='%ad | %h | %s'
git -C <repo> log -1 --pretty='HEAD: %h %s'
git -C <repo> --no-optional-locks status --porcelain
```

⚠️ **Every git command that writes leaves a lock this session cannot remove. Plan for it.**

In a sandboxed session, deletes are blocked inside connected folders, so git **creates its lock
files, writes them, and cannot unlink them**. The stale lock then blocks the *operator's* own git in
their own terminal until someone deletes it by hand. This is not specific to `git status` — it is
true of anything that takes a lock.

- **Reads: use `--no-optional-locks`.** A plain `git status` takes `.git/index.lock` and strands it,
  blocking `git add` and `git commit` afterwards. `--no-optional-locks` is a genuinely read-only
  status and takes no lock. An evening wrap that scans dozens of repos with a plain `git status` seeds a
  landmine in every one of them, every night. `log`, `diff`, `show` and `rev-parse` are safe.
- **Writes: `commit`, `add`, `tag`, `checkout`, `merge`, `gc` — these need the real lock, so they
  belong to the operator, not to the wrap.** Propose them; do not run them. A wrap never commits.
- **If the operator explicitly asks for a commit, clear the locks in the same turn.** A commit
  strands `.git/HEAD.lock` (which blocks every later ref update — the next commit fails with
  `Unable to create '.git/HEAD.lock': File exists`), `.git/objects/maintenance.lock`, and orphan
  `.git/objects/??/tmp_obj_*` blobs. Request delete permission for the connected folder root
  (`device_request_delete_permission`), remove exactly those paths, and **verify** — create and
  delete a throwaway tag in each repo touched, rather than assuming the cleanup worked. Say so in
  the report. *(Found 2026-09-25: three repos committed from a sandbox, three stranded HEAD.lock
  files, each one primed to fail the operator's next commit.)*
- **Never delete anything else under `.git/`.** Only `*.lock` at the paths above and
  `tmp_obj_*` under `objects/??/`.

Commit messages are the densest source in the entire sweep — they carry the outcome, the version and
often the reason, already written by the operator. A release commit closes a row on its own.
`status --porcelain` shows what was left in flight, but **check the mtimes of those files before
calling them today's work**: a long-lived dirty tree is normal and is often documented as deliberate
in the repo's own handoff.

Then read the touched files themselves — a build runbook's change log, a plan's open-items checklist,
a session handoff — for *what was decided*, not just *what was edited*. Project folders whose mtimes
cluster into a block are one work session; the span between first and last mtime is the time range.
Cross-check one mtime against a timestamped message about the same artifact to confirm the clock.

**Known noise — never file these as work:** `.DS_Store`, `*.xcuserstate` and other IDE window state,
`.obsidian/workspace.json`, `.claude-active-session` (an open session, not an edit), and the vault's
own `vault backup:` commits. IDE state earns at most one line as **weak** evidence a project was
*opened* — never as evidence it was worked on.

**If the vault lives inside a scanned root**, its note mtimes are real signal — they show what was captured
and when — while its backup commits are machine noise. And **a quiet docs folder is normal, not a
failed sweep**: say "nothing changed there" rather than silently omitting it.

**b. Sent mail, then received mail.** Sent mail is the operator's own actions and is denser per
message than the inbox. In the inbox, keep decisions, approvals, commitments, signature/payment
completions and anything closing an item the note already flagged as open. Drop vendor marketing,
digests and routine platform notices.

**c. Chat (Teams/Slack).** Read threads for their **arc** — what broke, what was tried, what the
resolution and root cause were — not message by message. A 40-message debugging thread is one log row.

**Paging is the trap here, not rate-limiting.** Graph chat search returns **newest-first** and offsets
run out long before the day does — three pages typically reach only early afternoon, which silently
drops the morning and every meeting room. Do **not** just accept that and declare partial coverage.
**Re-query with a moving `beforeDateTime` window** — take the oldest `createdDateTime` you received and
pass it as the next call's `beforeDateTime`, repeating until you reach local morning. Each window
restarts the offsets, so three or four narrow calls cover a whole day where paging one query cannot.
Only after that, if results are still truncated, say so and name the hour you actually reached.

**d. Text messages (iMessage) — the operator's real-world logistics land here, nowhere else.**
Vendors, trades, the shop, family — the outcome of an errand is usually a text and is in no mailbox,
ticket or repo. Read the Messages database directly; it is the reliable path:

```
sqlite3 "$HOME/Library/Messages/chat.db" "
SELECT datetime(m.date/1000000000 + strftime('%s','2001-01-01'),'unixepoch','localtime') AS t,
       CASE m.is_from_me WHEN 1 THEN 'ME' ELSE coalesce(h.id,'?') END AS who,
       replace(substr(coalesce(m.text,''),1,240), char(10),' ')
FROM message m LEFT JOIN handle h ON m.handle_id=h.ROWID
WHERE datetime(m.date/1000000000 + strftime('%s','2001-01-01'),'unixepoch','localtime') >= '<local start>'
  AND m.text IS NOT NULL AND length(trim(m.text))>0
ORDER BY m.date;"
```

⚠️ **Compare the timestamp as a local-time string, as above.** Wrapping the bound in
`strftime('%s', ..., 'utc')` silently returns zero rows — it looks like "no texts today" rather than a
bad query, which is the worst possible failure for a sweep.

The iMessage MCP's `get_unread_imessages` also works and needs no arguments, but it returns only
*unread* messages, so it misses anything the operator has already read — which is most of what matters.
**`search_contacts` on that server hangs** (verified 2026-09-24, three attempts, no response in 60 s):
do not call it, and do not read its hang as the whole server being unavailable or as a missing macOS
permission. Messages reads fine. Resolve a number to a person from the vault or from context instead.

**Known noise:** 2FA codes, bank alerts, delivery notifications, political and marketing spam. File a
text only when it carries an outcome, a commitment or a change of plan.

**e. Ticket/issue systems,** usually reachable through their notification mail if no connector is live.

**f. Calendar — name the meetings, bound the blocks, and recap the ones that qualify.**
The calendar bounds the blocks the other sources reveal. It is also the entry point to **meeting
transcripts**: an event carries a `meetingTranscriptUrl`, so a meeting that was transcribed can be
summarised without anyone downloading anything. **External meetings are recapped by default; internal
ones only when tagged `#recap`.** Procedure, eligibility rules, the two hard limits and the output
shape: **`references/meeting-recap.md`** — load it when the day had a qualifying meeting, not
otherwise.

**g. Claude Code CLI transcripts — reachable, but narrow.** A local-filesystem MCP (Desktop
Commander and similar) typically allows `~/.claude`, even though the plain device shell does not,
because the shell only sees explicitly connected folders. `~/.claude/history.jsonl` is the cheap
entry point: one line per prompt with `timestamp`, `project` (the repo cwd) and `sessionId`, so a
filter on today's timestamps says which repos had CLI sessions and when, and
`~/.claude/projects/<slug>/` holds the transcripts themselves. Read a transcript only when
`history.jsonl` shows activity today; use it to name what was worked on, not to quote the operator
back to themselves.

### Known limits — do not waste calls rediscovering these
- **Cowork sessions leave no readable transcript.** Only Claude Code CLI writes to `~/.claude`
  (see step g); the Cowork app's own history is not on disk anywhere reachable. For an operator whose
  day runs through Cowork, `history.jsonl` will be stale and the real record is the **output artifacts
  on disk** (step a). Reconstruct from those and say plainly that no session transcript was read.
- Local scratch outside the connected folders is invisible to the device shell. Absence of a file is
  not absence of work.
- **On a scheduled run, check the task actually has folders attached.** A device-bound task with an
  empty folder list still fires and still reports success, but can reach nothing and writes no draft.
  Folders cannot be added after a task is created — the task has to be recreated with them listed.

## 4. Turn the sweep into rows

- One row per **coherent block of work**, not per artifact or message. Merge a thread, its files and
  its follow-up mail into a single row with a real time range.
- Lead with the outcome, not the activity. *"Patch regression closed out — decision: install the OOB
  update on the weekend wave"* beats *"discussed patching"*.
- Quote the operator and others **verbatim** when a phrase carries the decision. Paraphrase loses the
  thing that makes the row worth reading in six months.
- Carry the markers the vault already uses: 🟢 win, ⛔ blocked/lost time, ⚠️ open risk, ✅ closed.
- Put every row in **chronological order** among the rows already there.
- **Close out open-ended rows.** A row ending `2:45 PM →` with no outcome is the most valuable thing
  the wrap can fix — append what actually happened.
- Link the effort in the Project/Area column. If no effort note exists for something real, say so and
  offer to create one; do not force-fit it into an adjacent project.

### 4a. Split mine from watching
Before proposing rows, classify every finding as **mine** or **👀 watching**, per the vault's
Conventions § 👀 Mine vs Watching. A finding from a shared mailbox, or a thread the operator is only
copied on, is a watch item with the owner from the vault's per-mailbox default-owner table, unless the
operator is named or acted themselves. Hourly-log rows record what the operator **did** (including
raising something with an owner); watch items go into the proposal as
`- [ ] 👀 … [owner:: [[Person]]] [[YYYY-MM-DD]]`, grouped by owner, with anything past its threshold
(5 business days, 2 customer-facing, or its own `escalate::` date) flagged **escalate**. Never
present a watch item as a task for the operator to go do.

### 4b. Fold the personal (Conventions § 🔒 Personal stays personal)
The wrap is whole-life, so personal findings are **logged, not dropped**: health, energy, how the
operator is feeling, family, home, the car, personal money, and anything from a blank-`entity` note
or a personal calendar or inbox. But the operator screen-shares daily notes, so personal content
never goes into the visible sections.
- **Promoted rows:** personal entries do **not** become Hourly Log table rows, Worked On bullets, or
  Evening Review lines. They go into one collapsed callout directly **below** the Hourly Log table,
  in callout-safe bullets (§ 8 rules apply):
  ```
  > [!quote]- 🏠 Personal
  > **HH:MM · Outcome-first summary** → [[Personal note]]
  > **Evening:** wins / blockers / how the day felt, personal side only
  ```
  One fold per day. Append to it if it already exists, never create a second.
- **Drafts:** inside an unattended `🌙 Wrap draft`, personal findings go into a nested
  `> > [!quote]- 🏠 Personal` fold at the end of the draft.
- **Collisions:** a work row may name a clash neutrally ("12:00 conflict, see 🏠 Personal") without
  saying what it is.
- **Unsure?** Treat it as personal and fold it. A note with no `entity` is personal until tagged.

## 5. Write-through is mandatory

Per § ⏳ Mutability. A wrap that only fills the daily log has done half the job. In the same pass,
surface every finding that changes a **living** note — `status`, `deadline`, `🎯 Outcome`,
`📌 Current Focus`, `🔗 Canonical Sources` — and include those edits in the proposal.

## 6. Flag the repeatable, and flag what you cannot resolve

- **Watch for SOP material.** A vendor limit hit for the second time, an incident whose diagnosis
  order would help next time, a process that ran correctly end to end — these belong in an Atlas/SOP
  note, not buried in a daily log. Name them under `Extract → PARA/Atlas` and say so out loud. The
  operator's standing instruction is that this is exactly what gets lost while handling the day.
- **Never invent a time or a cause.** Where the evidence conflicts (a runbook dated today but files
  stamped three hours earlier), write the row with the conflict marked inline in italics and ask.
  A wrong timestamp silently written is worse than a gap.

## 7. Propose, then write

Show **what / where / why** — the rows, the section each lands in, and the evidence behind each —
and write only on approval, per § Safety. Attended runs: the full proposal in chat.

## 8. Unattended / scheduled runs

A scheduled evening run has nobody to approve it, and the approval rule still holds. So:

- **Do not write into the log tables.** Write the whole draft into a single collapsed callout placed
  directly above `## ⏱️ Hourly Log`:

  ```
  > [!todo]- 🌙 Wrap draft — generated YYYY-MM-DD HH:MM, not yet approved
  > <proposed rows, worked-on bullets, evening review, open questions>
  ```

- ⚠️ **Callout-safe markdown only — no tables, no `#` headings inside the callout.** Obsidian's Live
  Preview does not render a pipe table or an ATX heading inside a callout; both come out as raw
  markdown, and everything after them in the note reads as broken. That silently ruins the one
  artifact an unattended run produces. Use only what a callout reliably renders: `>` prefixed bold
  labels, bullets, nested bullets (4 spaces after `> `), inline `code`, links and `[[wikilinks]]`.
  A proposed hourly-log row therefore goes in as a bullet, not a table row:

  ```
  > **HH:MM–HH:MM · 🟢 Outcome-first summary** → [[Effort]]
  >     - evidence, quote, commit hash
  ```

  Section breaks inside the callout are **bold lines**, never `###`. Every line of the callout —
  including blank ones — starts with `>`; one truly blank line ends it.
- **Verify before reporting success.** After writing, re-read the note and check that no line between
  the callout's first line and its terminating blank line is missing its `>` prefix, and that the
  callout contains no line matching `^> \|` or `^> #{1,6} `. Confirm the diff touched only the
  callout — the log tables must show zero deletions.
- One draft per day. If the callout already exists, **replace** it rather than appending a second.
- Leave the open questions in the draft rather than guessing them.
- On the next attended session, promoting the draft into the real sections is a normal approved edit,
  and the callout is removed in the same pass.
- A wrap for a **prior** day is retro-editing a snapshot. Do not rewrite its existing rows; add the
  reconstruction under a `> [!note]- Reconstructed YYYY-MM-DD` callout and leave the original record intact.
