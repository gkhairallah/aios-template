---
description: Take an action in a connected external system (Coda, Zoho, Linear, chat, mail…) — always shown as an approval card first
---

Use the **act** skill. Input: $ARGUMENTS

Capability check first — does this session have a gateway (`COMPOSIO_SEARCH_TOOLS` /
`COMPOSIO_MULTI_EXECUTE_TOOL`) or a first-party write tool? If neither, say so plainly and offer the
closest alternative; never imply an action happened.

Then resolve before proposing: discover the tool, confirm `has_active_connection`, pin the account
alias, resolve the target by id (not name), and read current state for an update. Show the full
approval card — action, via/tool, account, target, exact JSON arguments, changes, effect,
reversibility — and **wait for explicit approval**. Escalate to a second confirmation for anything
irreversible, customer-facing, or financial.

Execute only the approved payload (gateway calls go through `COMPOSIO_MULTI_EXECUTE_TOOL`; the array
parameter is `tools`). Report the result with a link, then offer to log it in the vault and apply
write-through to any living surfaces the action changed.

Never write as a side effect of a read — that's `gather`'s job, and it hands off here.
