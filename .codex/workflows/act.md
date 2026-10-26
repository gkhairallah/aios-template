# Act on an external system

Use this wrapper when the user asks for something to CHANGE outside the vault —
add or update a row, page, ticket, or issue; post a chat message; draft or send mail —
whether the tool comes from a first-party connector or a gateway that fronts many
toolkits at once.

The authoritative workflow is `.aios/Skills/aios-notes/skills/act/SKILL.md`. Read and
follow it. Retain in full: the capability check (does this session actually have a write
tool?), the preflight resolution (discover, confirm the connection, pin the account,
resolve the target by id, read current state before an update), the approval card shown
before every write, and the requirement for explicit approval in this conversation — with
a second confirmation for anything irreversible, customer-facing, or financial. Do not
reproduce or bypass its rules.

Reads belong in `.codex/workflows/gather.md`; that route never writes outward and hands
off here instead.
