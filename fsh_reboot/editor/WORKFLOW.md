# Editing content — Working Copy guide

This guide explains how to update the website's homepage content using Working Copy on iOS.

---

## What you're editing

In addition to the layout and the page listings (which are automatically generated), the homepage has five content blocks which can be edited.

The five content blocks are:

- **hero.md** — the large banner at the top of the page
- **col1.md** — left column
- **col2.md** — middle column
- **col3.md** — right column
- **banner.md** — the book banner

The website maintains [a draft](index_draft.html) of the homepage, which isn't shown to the public. This page can be edited, previewed, discussed and corrected until it's ready to be published as the new live homepage. 

This *draft* page is what you're editing. The five content blocks are each derived from a simple text file. These text files are stored in the `fsh_reboot/editor/content_draft` folder, which you have in your copy of the fleetstreetheritage repository.

Each block can contain text, images, links, or they can be removed completely by saving them without content. When these files are pushed to GitHub through the Working Copy app, the web server will automatically recognise them and create a new draft homepage, ready to become the live homepage when the time comes.


For formatting guidance (bold, links, headings etc.) see [markdown.html](markdown.html) in this folder.

---

## Step 1 — Pull the latest version

Before editing, always make sure you have the latest version of the files.

In Working Copy, open the **fleetstreetheritage** repository and tap **Pull** to fetch any recent changes.

---

## Step 2 — Edit a file

1. In Working Copy, navigate to `fsh_reboot / editor / content_draft`
2. Tap the file you want to edit (e.g. `col1.md`)
3. Tap the **content icon** (the first of the three at the centre-bottom of the screen) to edit
4. Make your changes, a little while later, the file icon will turn orange and show 'modified'

---

## Step 3 — Commit your changes to `content_draft` and preview the results

When you're happy with your edits:

1. Tap the **Commit button** (speech bubble) at the top to open a commit sheet 
2. Tap the tick-boxes of each of the files you want to commit (or tap the **All** button if appropriate)
3. Write a short note describing what you changed (e.g. *"Updated hero and col1 intro text"*)
4. Making sure the **Push** switch is on, tap **Commit** to send your changes to GitHub

Once pushed, GitHub will automatically run the generator and produce a new preview page, showing all your changes. Check the [draft preview](index_draft.html) to see how your changes look before publishing.

---

## Step 4 — When ready, tell GitHub to publish `content_draft` to become the new live homepage

When you've checked the draft preview, made all the changes you want to, and everything looks right:

1. In Working Copy, navigate to `fsh_reboot / editor / content_draft`
2. Tap the **+** button to create a new file
3. Name it exactly: `PUBLISH` (all capitals, no extension)
4. Leave it empty and tap **Done**
5. Commit and push as in Step 3 (e.g. *"Publish content update"*)

GitHub will detect the `PUBLISH` file when you commit, copy your draft content to the live site, and delete the `PUBLISH` file automatically, ready for the next set of changes when they are needed. The live homepage will update shortly after.

---

## Things to know

- You can commit and push as many times as you like while drafting — nothing goes live until you create the `PUBLISH` file
- If you make a mistake after publishing, just edit the files again and publish again
- The `PUBLISH` file disappears automatically after publishing — that's normal
- Don't edit files in `fsh_reboot / content` directly — that folder is managed automatically
