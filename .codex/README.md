# `.codex/` — the OpenAI Codex / ChatGPT entry point

AIOS is deliberately **model-agnostic**. The skill instructions in
`.aios/Skills/aios-notes/` are plain Markdown and hold all the real authority — filing
rules, formatting, approval gates, `Private/` protection. This folder is a thin **router**
that lets a Codex (ChatGPT) session find and follow those same instructions, so both
assistants operate the vault identically.

Nothing here copies or reinterprets a skill. Each file points at its authority and stops.

| File | Role |
|---|---|
| `../AGENTS.md` | Repo-level entry. Codex reads this first; it holds the safety rules and the routing tables. |
| `workflows/*.md` | One wrapper per workflow (capture-note, vault-ops, gather, attach) → points at the matching `SKILL.md`. |
| `commands/*.md` | One wrapper per command intent (note, log, find, todo, today, gather, review, status) → points at the matching command file, then its workflow. |
| `global-AGENTS.md.example` | The **machine-wide** safety baseline. Install per machine — it is outside the repo and does not clone. |

Wrappers provide **natural-language routing**, not custom slash commands. Project-local
custom prompts are not the current Codex standard for reusable workflows and would
duplicate or relocate authority that already exists.

## Per-machine install: the global safety baseline

`global-AGENTS.md.example` is the machine-wide baseline — approval before any
state-changing action, retrieved content treated as data rather than instructions, and no
connector writes as a side effect of reads. It belongs at `~/.codex/AGENTS.md`, which is
**outside the repo and therefore does not clone**. Install it on every machine that runs
Codex:

```bash
mkdir -p ~/.codex
cp "<path-to-your-vault>/.codex/global-AGENTS.md.example" ~/.codex/AGENTS.md
```

Why it matters: the repo-level `AGENTS.md` only governs sessions opened **inside the
vault**. Codex work in any other directory is ungated without the global file.

## Two independent permission layers

| Layer | What it is | Fires when |
|---|---|---|
| **Instruction** | `AGENTS.md` (global + repo) | The model decides to *propose* rather than call. Renders as prose: "Proposed change… reply approve". |
| **Platform** | The ChatGPT app's connector permission | A tool call is actually *attempted*. Renders as a hard dialog naming the app and parameters, with **Deny / Allow once**. |

**The instruction layer masks the platform layer.** A platform gate only fires on an
attempted tool call, so an `AGENTS.md` rule that stops the model *before* the call means
the platform dialog never appears — which reads as "there is no platform gate." There is.
Mail sends produce the hard dialog, and it ignores an in-conversation "just do it." Never
conclude a gate is absent from prose-only approvals; re-test with the instruction layer
deliberately waived.

What does **not** work, so you do not waste time on it: the app's Permissions toggles are
file/shell-scoped and change nothing about connector behaviour; there is no per-connector
permission UI; and the permission modes Codex will describe conversationally
(`always_ask`, `ask_before_writes`, `review_important_actions`, `inherit`) do not appear
in OpenAI's config reference — treat that answer as unreliable and check the docs.

Verify your install by asking Codex to write a file from a directory with **no**
repo-level `AGENTS.md`; it should propose the change and wait. Note that a temp directory
is a poor test target — it sits outside the workspace sandbox, so a prompt there may be
the sandbox rather than the instruction file. Test in a real working directory.
