# Filing Rules — the AIOS decision procedure (fallback copy)

> Prefer the vault's own `30 Atlas/Filing Rules.md` when present. This is the fallback.

Two axes, three yes/no questions, first-YES-wins.

## The cascade (first YES wins)
| # | Question (objective) | Goes to |
|---|---|---|
| 0 | Just happened / just occurred to me? | `00 Calendar` (daily log) |
| 1 | **WORK** — can I mark it **DONE** and stop? | `10 Efforts` · `type: project` |
| 2 | **WORK** — ongoing **standard I maintain**, no end? | `10 Efforts` · `type: area` |
| 3 | **KNOWLEDGE** — I **authored** it? | `30 Atlas` · `type: atlas` |
| 4 | **KNOWLEDGE** — I **collected** it (external ref)? | `40 Resources` · `type: resource` |
| 5 | Done / dead / dormant? (lifecycle, not a category) | `90 Archives` |

Also: a **decision** → `30 Atlas/Decisions` · `type: decision`; a **map/hub** → `30 Atlas/MOCs` · `type: moc`;
a **business hub** area → `10 Efforts/Companies` · `type: area`.

## Bright lines (not vibes)
- **Project vs Area** → does a done-state exist? Finish and stop = project; maintain forever = area.
- **Atlas vs Resources** → did I write it or collect it? My words = Atlas; someone else's material = Resources.
- **Work vs Knowledge** → something to do/uphold, or something to know?
- **Snapshot vs Living note** → does it carry `date:` or `created:`? `date:` = fixed record of a moment, never retro-edited. `created:` = projection of now, never allowed to go stale. See Conventions § Mutability.

## Tie-breakers
- Torn between Work and Knowledge → it's **Knowledge**.
- Torn between Atlas and Resources → **Atlas** if any of my own words are in it, else Resources.
- Still torn → leave it in the daily log. Non-promotion is a valid state.

## Principles
- **One door for capture:** never file at capture; the daily log takes everything; promote later only if it earns a durable identity.
- **Folders are weak; `type` + `[[links]]` are strong** — retrieval is by search, links, and Dataview, so a misfile costs nothing.
