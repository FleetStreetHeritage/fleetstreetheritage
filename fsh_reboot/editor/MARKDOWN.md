# Markdown reference

Quick guide to the formatting supported in content files.

---

## Headings

```
# Large display heading
## Small section heading
```

Use `#` for a large bold heading (e.g. a big number or title).
Use `##` for a smaller uppercase section label.

---

## Paragraphs

Just write text. Leave a blank line between paragraphs.

```
This is the first paragraph.

This is the second paragraph.
```

---

## Bold and italic

```
**this is bold**
*this is italic*
```

---

## Links

```
[link text](https://example.com)
```

---

## Bullet lists

```
- First item
- Second item
- Third item
```

---

## Images

```
![description of image](filename.jpg)
```

The image file must exist in the images folder.

Linked image (tapping opens a URL):

```
[![description](filename.jpg)](https://example.com)
```

---

## Layout and style

Wrap content in `<div class="...">` and `</div>` to apply a style. Available classes:

- `center` — centre-align the content
- `jumbo` — very large yellow text, for a big number or display word
- `small` — smaller text, useful for captions
- `accent` — yellow text for emphasis
- `muted` — dimmed text for secondary content
- `box` — draws a bordered box around the content

Classes can be combined, e.g. `<div class="center small">`.

Example — a centred caption beneath an image:

```
![description](image.jpg)

<div class="center small">
Caption text here
</div>
```

Example — a callout box:

```
<div class="box">
Tickets available now — see the events page for details
</div>
```

---

## Notes

- Links in the banner and columns will appear yellow and underlined
- Leave the file empty if you don't want that block to appear on the page
