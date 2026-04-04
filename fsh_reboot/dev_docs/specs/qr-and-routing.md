# FSH URL Parameters & Routing Spec

## URL Parameters

| Param | Values | Default | Meaning |
|---|---|---|---|
| `src` | see below | — | Traffic source identifier |
| `v` | `nl`, `easy` | — | View preference |
| `f` | `0`, `1`, `2` | `0` | Force level for `v` |

## Force levels

| `f` | Behaviour |
|---|---|
| `0` | Use `v` only if no stored view (`localStorage` wins if set) |
| `1` | Use `v` for this pageview only, do not write to `localStorage` |
| `2` | Use `v` and write to `localStorage` as new site preference |

Routing logic:
```
f=0: target = localStorage.fsh_view ?? v ?? 'nl'
f=1: target = v ?? localStorage.fsh_view ?? 'nl'
f=2: localStorage.fsh_view = v; target = v ?? 'nl'
```

## localStorage

Key: `fsh_view`  
Values: `nl` | `easy`

## Source identifiers (`src=`)

> ❓ OPEN: agree and finalise this list

| Value | Source |
|---|---|
| `wall` | Physical Heritage Wall, Bouverie Street |
| `leaflet` | Printed leaflet |
| `poster` | Poster |
| `web` | Link from within the website |
| *(more TBD)* | |

---

## Open questions

- **Slug/URL structure** — agreed: flat, human-readable (e.g. `dr-johnson.html`). Numerical URLs (`115.html`) to redirect. Full slug list to be built from `index.html`.
- **`src=` values** — stub list above, needs sign-off.
- **Other views?** — any planned beyond `nl` and `easy`? (e.g. large-print, translated)
- **QR code generation** — tool/process for bulk-generating QR codes not yet decided.
- **Testing URL** — subfolder on current GitHub Pages repo vs. separate dev repo (TBD).
