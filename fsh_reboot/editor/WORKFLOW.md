# Editing content — Working Copy guide

This guide explains how to update the website's homepage content using Working Copy on iOS.

---

## What you're editing

The homepage has five content blocks, each stored as a simple text file in the `fsh_reboot/editor/content_draft` folder:

- **hero.md** — the large banner at the top of the page
- **col1.md** — left column
- **col2.md** — middle column
- **col3.md** — right column
- **banner.md** — the book banner

For formatting guidance (bold, links, headings etc.) see `MARKDOWN.md` in this folder.

---

## Step 1 — Pull the latest version

Before editing, always make sure you have the latest version of the files.

In Working Copy, open the **fleetstreetheritage** repository and tap **Pull** to fetch any recent changes.

---

## Step 2 — Edit a file

1. In Working Copy, navigate to `fsh_reboot / editor / content_draft`
2. Tap the file you want to edit (e.g. `col1.md`)
3. Tap the **content icon** (the first of the three at the centre-bottom of the screen) to edit
4. Make your changes, you will notice that a little while later the file icon will turn orange and show 'modified'

---

## Step 3 — Commit your changes to content_draft to preview the results

When you're happy with your edits:

1. Tap the **Commit button** (speech bubble) at the top to open a commit sheet 
2. Tap the tick-boxes of each of the files you want to commit (or tap the **All** button if appropriate)
3. Write a short note describing what you changed (e.g. *"Updated hero and col1 intro text"*)
4. Making sure the **Push** switch is on, tap **Commit** to send your changes to GitHub

Once pushed, GitHub will automatically run the generator and produce a preview page. Check the [draft preview](index_draft.html) to see how your changes look before publishing.

---

## Step 4 — Tell Github to publish content_draft to the live site when ready

When you've checked the draft preview and everything looks right:

1. In Working Copy, navigate to `fsh_reboot / editor / content_draft`
2. Tap the **+** button to create a new file
3. Name it exactly: `PUBLISH` (all capitals, no extension)
4. Leave it empty and tap **Done**
5. Commit and push as in Step 3 (e.g. *"Publish content update"*)

GitHub will detect the `PUBLISH` file when you commit, copy your draft content to the live site, and delete the `PUBLISH` file automatically, ready for the next edits to happen. The live homepage will update shortly after.

---

## Things to know

- You can commit and push as many times as you like while drafting — nothing goes live until you create the `PUBLISH` file
- If you make a mistake after publishing, just edit the files again and publish again
- The `PUBLISH` file disappears automatically after publishing — that's normal
- Don't edit files in `fsh_reboot / content` directly — that folder is managed automatically
