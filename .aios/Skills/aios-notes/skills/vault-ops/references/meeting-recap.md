# Meeting Recap — turn a Teams transcript into a Call Summary

Loaded by the **day wrap** at its calendar step (`day-wrap.md` § 3e). Not a standalone command: a
recap is part of closing the day, and like everything else in the wrap it is **proposed, never
written straight into living notes**.

**The premise:** the operator used to open each meeting's Recap in Teams, download the transcript and
hand it over by hand. Every step of that is reachable from the calendar, so the wrap should arrive
with the summary already drafted.

---

## 1. Which meetings qualify

**External by default. Internal only when tagged.**

- **External** = at least one attendee outside the internal domains.
- **`INTERNAL_DOMAINS` live in the vault, not here:** `30 Atlas/Conventions.md` § 🏢 Internal domains.
  If that section is missing or empty, ask the operator once and propose adding it — never guess from
  the operator's own address alone. List **every** domain whose people sit in the operator's internal
  meetings (sister companies and close partners included): treating only the operator's own domain as
  internal classifies the standing team meeting as a customer call and recaps it every week.
  ⚠️ **The consequence, stated so it is not a surprise:** a meeting attended *only* by internal-domain
  people is **internal**, however substantive — a sister-company product sync or an internal commercial
  discussion is not recapped unless it carries `#recap`. A customer call stays external on the
  customer's presence, so an internal colleague joining it does not make it internal.

- **Internal meetings are recapped only when tagged `#recap`** in the invite subject or body. This
  mirrors a `#nocrm`-style opt-out filter if the vault already uses one (e.g. for a meeting-recording →
  CRM integration) — same idea, opposite polarity, so there is one tagging habit rather than two.
- Skip cancelled events, all-day blocks, and events the operator declined.
- A meeting with no transcript is **not** a failure: most meetings are not transcribed. Say nothing
  about it unless the operator's own log says the call mattered.

## 2. Getting the transcript — the exact chain

```
outlook_calendar_search   (the day's events)
  → read_resource  calendar:///events/{eventId}
      → field `meetingTranscriptUrl`
        → read_resource  meeting-transcript:///events/{token}?start=…&end=…
```

Pass `meetingTranscriptUrl` **verbatim**. It is an opaque base64url token plus the occurrence window;
do not rebuild it from the join URL, and keep `start`/`end` so a recurring series resolves to the one
occurrence.

**Two hard limits, both verified 2026-09-22 — recognise them instead of retrying:**

- 🔴 **`GraphAccessToTranscriptsDisabled`** — *"Graph API access to transcripts is disabled for
  this tenant."* A **tenant** setting that overrides app permissions and policy: the Entra grants alone
  are not enough, and reassigning an application access policy does not override it. Two settings
  matter, and **both should be on**:
  - **Graph access to transcripts.** Off → every transcript request returns `403`.
  - **Speaker attribution.** Off → transcript content comes back **with no speaker names**, which
    guts a recap: decisions cannot be attributed and quotes cannot be assigned. Enable it too.

  **Teams Admin Center — the reliable route, and it needs no PowerShell** (verified against Microsoft's
  own doc, 2026-09-22):
  Left navigation → **Meetings** → **Meeting settings** → under **Transcript API access**, toggle
  **Microsoft Graph access** to **On** → then select **Configure** and toggle
  **Include speaker attribution** to **On**. Attribution is a *sub-setting behind Configure*, easy to
  miss, and without it transcripts return with no speaker names.

  **PowerShell equivalent** (`MicrosoftTeams` module):
  ```powershell
  Set-CsTeamsMeetingConfiguration -EnableGraphTranscriptAccess true ``
    -EnableAttributedTranscripts true -Identity Global
  ```
  ⚠️ **`A parameter cannot be found that matches parameter name 'EnableGraphTranscriptAccess'` means
  the installed module predates the parameter — the cmdlet and parameter names are correct.** Both
  parameters are documented on `Set-CsTeamsMeetingConfiguration` (not `Set-CsTeamsMeetingPolicy`).
  Confirm with `(Get-Command Set-CsTeamsMeetingConfiguration).Parameters.Keys -match 'Transcript'`;
  fix with `Update-Module MicrosoftTeams`, then restart the session and `Connect-MicrosoftTeams`.
  **Do not chase the parameter name — use the Admin Center toggle instead.**

  **Report this once, name the Admin Center path, and carry on with the rest of the wrap** — never
  retry it per meeting.
- ⚠️ **Calendly-booked meetings return `onlineMeeting: null` and `meetingTranscriptUrl: null`.**
  Calendly writes its own link into Location, so Graph never attaches a Teams meeting object and there
  is nothing to fetch — the transcript exists only in the Teams Recap UI. **This disproportionately
  hits customer calls**, which are the ones most worth recapping. When a qualifying meeting comes back
  null, say so by name and note that its transcript is still a manual download, rather than reporting
  the meeting as having no transcript.

If `OnlineMeetingAiInsight.Read.All` is granted, it exposes Teams' own extracted action items and notes. Treat
anything from it as a **lead to verify against the transcript**, never as a finding in its own right.

## 3. What to produce

**One `· Call Summary` note per meeting**, filed in `30 Atlas/`, named
`<Subject or relationship> · Call Summary YYYY-MM-DD`. Model it on the existing ones — they are the
spec, and the shape that matters is that **headings are derived from what the meeting actually
decided**, not a fixed template. Frontmatter carries `type: atlas`, `date`, `entity`, and a `source:`
line naming the meeting, its real clock span, duration and who started transcription.

Then, into the wrap draft callout:

- **An hourly-log row** for the meeting, at its real time range, leading with the outcome.
- **Action items** — only where someone actually committed. Name the owner. An item with no owner is
  an open question, not a task; say so rather than assigning it.
- **Decisions** — a decision that will outlive the meeting earns its own `30 Atlas/Decisions/` note;
  one that only explains this meeting stays in the Call Summary.
- **Write-through edits** the meeting forces on living notes (§ 5 of the wrap).

## 4. Reading a transcript well

- **Quote verbatim where the phrase carries the decision.** Paraphrase loses the thing that makes the
  row worth reading in six months — a transcript is more defensible than a summary because it
  preserves what was said.
- **Read for the arc**, not turn by turn: what was asked, what was tried, what got settled, what was
  left open. A 48-minute call is a handful of rows, not fifty.
- **Attribute correctly.** Transcripts mis-assign speakers, especially on overlap and for phone
  participants. If a decisive line's speaker is uncertain, mark it *(speaker uncertain)* rather than
  putting words in someone's mouth.
- **Never infer a commitment from discussion.** "We should probably…" is not a decision. If the
  meeting ended without settling something that mattered, that absence **is** the finding.
- **The most valuable thing in a customer call is rarely the technical content.** Openings, offers and
  relationship signals outrank architecture — note them explicitly.
- Cross-check the clock against the calendar event and the meeting chat; transcripts start when
  recording starts, which is usually after the meeting did.
