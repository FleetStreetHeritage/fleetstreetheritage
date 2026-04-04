# iOS Editor — UX notes (deferred)

## The problem

The editor currently exposes four distinct states a file can be in:

1. **Unsaved** — typed in editor, not saved to disk (`●` dot)
2. **Saved to draft** — on disk in `content_draft/`, not yet in git (`○` dot)
3. **Committed** — in git but not published (no indicator)
4. **Published** — in `content/`, live on the website

The actions map awkwardly onto these:
- **Revert** — reverts to state 2, but "revert to what?" is not obvious to the user
- **Commit** — moves 2→3, but nothing changes visibly; git is an implementation detail
- **Publish** — *intends* to trigger 3→4 but doesn't actually do it until Working Copy pushes; the gap between pressing Publish and the site updating is invisible

The `🔄 Editing / Saved / Live` cycle in the preview compounds this — three subtly different states that require understanding the whole pipeline to interpret correctly.

## Proposed direction

**Collapse the mental model.** The editor doesn't need to expose the git layer at all.

- **Save** stays — saves to disk, clear and immediate meaning
- **Commit + Publish** merge into a single **Submit** (or "Send to website") button:
  saves everything, writes the PUBLISH flag, opens Working Copy. One action, one intent.
- **Revert** becomes **Undo edits** — reverts to last save, the only meaningful safe point from an editor's perspective
- The preview cycle simplifies to **Draft / Live** (two states):
  - *Draft* = what's saved in `content_draft/`
  - *Live* = what's in `content/` (on the website now)
  - The "what I'm currently typing" state is just the default view — not worth naming separately
- Tab indicators collapse to a single `●` meaning "unsaved changes" — the saved/committed distinction is noise from the editor's perspective

## What this would require in code

- Remove the three-way cycle; replace with a two-way Draft/Live toggle
- Merge `_on_commit` and `_on_publish` into a single `_on_submit` handler
- Rename "Revert" button to "Undo edits"
- Tab `○` indicator removed; `●` is the only unsaved signal
- Consider: prompt when navigating away from a tab with unsaved changes

## Open question

Whether "Submit" / "Send to website" adequately communicates that the change isn't
instant — Working Copy still needs to be opened and a push made. Possibly a
confirmation dialog: *"This will publish your draft when you push in Working Copy."*
