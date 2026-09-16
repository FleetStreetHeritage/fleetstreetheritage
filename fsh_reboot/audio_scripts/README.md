# Audio narration scripts

Source text for the audio narrations. One file per page, named by page
number: `142.txt`, `301.txt`, etc. (matching `num` in `data/pages.json`).

## File contents

Each `<num>.txt` contains the **body copy only** — the text the narrator
voice reads. Plain text, written for listening (spell out abbreviations,
drop visual references like "see diagram below").

The first line may be a provenance comment, stripped before synthesis:

    # source: master
    # source: extracted-from-pdf — review before publishing

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
