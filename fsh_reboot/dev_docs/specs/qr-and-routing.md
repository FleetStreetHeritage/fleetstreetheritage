# FSH URL Parameters & Routing Spec

## URL Parameters

| Param | Values | Default | Meaning |
|---|---|---|---|
| `s` | two-letter code, see below | — | Traffic source identifier (was `src`, shortened 2026-09 to fit the QR character budget) |
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

## Source identifiers (`s=`)

Agreed 2026-09-17. Codes are two letters (keeps printed QR URLs short enough
to fit a fixed 37×37 symbol at high error correction). The generator expands
each code to its full label before it reaches any GA4 event — see
`SRC_LABELS` in `fsh_reboot/scripts/generate.py` — so reports read "Wall",
"Leaflet", etc. rather than raw codes. An unrecognised code is passed through
as-is (visible in GA as a literal code, rather than silently dropped), so a
new source can be used on print before its label is added here — just add it
to `SRC_LABELS` and this table together.

| Code | Label | Source |
|---|---|---|
| `wa` | Wall | Physical Heritage Wall, Bouverie Street |
| `lf` | Leaflet | Printed leaflet |
| `po` | Poster | Poster |
| `wb` | Web | External link to the site (social, search, another website) |
| `in` | Internal | Link from within the site itself |
| `bk` | Book | The Heritage of Fleet Street book |
| *(more TBD)* | | |

---

## Open questions

- **Slug/URL structure** — agreed: flat, human-readable (e.g. `dr-johnson.html`). Numerical URLs (`115.html`) to redirect. Full slug list to be built from `index.html`.
- **`s=` values** — table above agreed 2026-09-17; add new codes here as new source types arise.
- **Other views?** — any planned beyond `nl` and `easy`? (e.g. large-print, translated)
- **QR code generation** — tool/process for bulk-generating QR codes not yet decided.
- **Testing URL** — subfolder on current GitHub Pages repo vs. separate dev repo (TBD).
