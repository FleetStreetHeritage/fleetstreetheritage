# Audio narration scripts

Source text for the audio narrations. One file per page, named by page
number: `142.txt`, `301.txt`, etc. (matching `num` in `data/pages.json`).

## File contents

Each `<num>.txt` contains the **body copy only** — the text the narrator
voice reads. Plain text, written for listening (spell out abbreviations,
drop visual references like "see diagram below").

Lines starting with `#` are comments, stripped before synthesis. Two have
special meaning:

    # source: master
    # source: extracted-from-pdf — review before publishing

records where the text came from, and

    # do-not-narrate

anywhere in the file tells the audio generator to skip the page entirely
(no MP3, so the page's audio player stays hidden). Use it for maps,
diagrams, and list/directory pages that read poorly aloud. Delete the
line to enable narration for that page.

Lines like

    # check: possible caption/heading, verify in body — "…"

are automated review pointers: the quoted fragment may be an image
caption or visual heading that survived text extraction and would sound
odd read aloud. Search the body for it, fix or remove it (or decide it's
fine), then delete the check line. They are advisory only — the
generator ignores them like any other comment.

## Intro and signoff (announcer voice)

`_intro.txt` and `_signoff.txt` hold the shared framing read by a second
"announcer" voice on every page. Placeholders are filled per page:

- `{title}` — the page title
- `{num}`   — the page number

The audio generator (planned: `scripts/generate_audio.py`) will synthesise
intro + signoff with the announcer voice and the body with the narrator
voice, then join them into one `docs/dev/audio/<num>.mp3`. Any page whose
MP3 exists automatically gets the audio player on its web page.

## Editing

These files are the authoritative narration text — edit freely; the
generator only re-synthesises pages whose text has changed. Master text
(as used to create the artwork) takes precedence over PDF-extracted text.
