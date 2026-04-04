#!/usr/bin/env python3
# build 7
"""
FSH Content Editor — Pythonista iOS app
Edit and preview content markdown files for the Fleet Street Heritage website.

Stored in fsh_reboot/ios/editor.py in the repo.
Open the repo root folder in Pythonista, then run this file.
"""

import ui
import re
import sys
import threading
import webbrowser
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).resolve().parent.parent.parent
CONTENT_DIR = REPO_ROOT / 'fsh_reboot' / 'content'
TEMPLATE    = REPO_ROOT / 'fsh_reboot' / 'template' / 'index_evolution.html'
IMAGES_DIR  = REPO_ROOT / 'docs' / 'dev' / 'images'
SCRIPTS_DIR = REPO_ROOT / 'fsh_reboot' / 'scripts'

sys.path.insert(0, str(SCRIPTS_DIR))
import content as cnt
md_to_html = cnt.md_to_html

# ── Content files ─────────────────────────────────────────────────────────────
FILES  = ['hero',  'banner', 'col1',  'col2',  'col3']
LABELS = ['Hero',  'Banner', 'Col 1', 'Col 2', 'Col 3']

FSH_BLUE   = '#254760'
FSH_YELLOW = '#FFFF66'


# ── Validation ────────────────────────────────────────────────────────────────

def validate_text(filename, text):
    errors = []
    for m in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', text):
        src = m.group(2)
        if src.startswith('http'):
            continue
        if not (IMAGES_DIR / Path(src).name).exists():
            errors.append(f'Image not found: {src}')
    if text.count('[') != text.count(']'):
        errors.append(f'Unbalanced brackets')
    if len(re.findall(r'\]\(', text)) != len(re.findall(r'\]\([^)]*\)', text)):
        errors.append('Unclosed link parenthesis')
    return errors


def validate_all(texts):
    return {name: errs for name, text in texts.items()
            if (errs := validate_text(name, text))}


# ── HTML helpers ──────────────────────────────────────────────────────────────

COL_CSS = """
body {
  font-family: Arial, Helvetica, sans-serif;
  font-size: 0.9rem;
  line-height: 1.6;
  background: #254760;
  color: #fff;
  padding: 1rem;
  margin: 0;
}
h2.col-title {
  font-size: 3.5rem;
  font-weight: bold;
  line-height: 1;
  color: #FFFF66;
  margin-bottom: 0.25rem;
}
h2.col-heading {
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #FFFF66;
  margin-bottom: 0.5rem;
}
p  { margin-bottom: 0.6rem; }
a  { color: #FFFF66; text-decoration: underline; }
ul { list-style: none; margin-top: 0.5rem; font-size: 0.85rem; }
img { display: block; width: 100%; max-width: 220px; height: auto; margin-bottom: 0.75rem; }
"""


def abs_images(html):
    def replace(m):
        src = m.group(1)
        if src.startswith(('http', 'file')):
            return m.group(0)
        return f'src="{(IMAGES_DIR / Path(src).name).as_uri()}"'
    return re.sub(r'src="([^"]+)"', replace, html)


def col_preview_html(text):
    body = md_to_html(text) if text.strip() else '<p style="color:#aaa">(empty)</p>'
    return abs_images(
        f'<html><head><meta name="viewport" content="width=device-width">'
        f'<style>{COL_CSS}</style></head><body>{body}</body></html>'
    )


def full_page_html(texts):
    if not TEMPLATE.exists():
        return '<html><body><p>Template not found.</p></body></html>'
    def block(name, open_tag, close_tag):
        inner = md_to_html(texts.get(name, ''))
        return f'{open_tag}{inner}{close_tag}' if inner.strip() else ''
    html = (TEMPLATE.read_text(encoding='utf-8')
            .replace('<!-- GA_ID -->',        'GA-PREVIEW')
            .replace('<!-- HERO_BLOCK -->',   block('hero',   '<div class="hero">',        '</div>'))
            .replace('<!-- BANNER_BLOCK -->', block('banner', '<div class="book-banner">', '</div>'))
            .replace('<!-- COL_1 -->',        md_to_html(texts.get('col1', '')))
            .replace('<!-- COL_2 -->',        md_to_html(texts.get('col2', '')))
            .replace('<!-- COL_3 -->',        md_to_html(texts.get('col3', '')))
            .replace('<!-- VOLUME_SECTIONS -->',
                     '<p style="color:rgba(255,255,255,0.4);font-size:0.8rem;text-align:center">'
                     '(page listing not shown in preview)</p>'))
    return abs_images(html)


# ── Editor ────────────────────────────────────────────────────────────────────

class FSHEditor(ui.View):

    def __init__(self):
        self.current_idx    = 0
        self.original_texts = {}   # texts as last saved to disk
        self.texts          = {}   # current in-editor texts
        self.needs_commit   = False
        self.show_original  = False
        self._preview_timer = None
        self._touch_start   = None

        self._load_all_files()
        self._build_ui()

    # ── File I/O ──────────────────────────────────────────────────────────────

    def _load_all_files(self):
        for name in FILES:
            path = CONTENT_DIR / f'{name}.md'
            t = path.read_text(encoding='utf-8') if path.exists() else ''
            self.original_texts[name] = t
            self.texts[name] = t

    @property
    def current_file(self):
        return FILES[self.current_idx]

    def _is_dirty(self, name=None):
        name = name or self.current_file
        return self.texts[name] != self.original_texts[name]

    def _save_all(self):
        for name in FILES:
            if self._is_dirty(name):
                path = CONTENT_DIR / f'{name}.md'
                path.write_text(self.texts[name], encoding='utf-8')
                self.original_texts[name] = self.texts[name]
        self.needs_commit = True
        self._update_buttons()
        self._update_seg_labels()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        self.background_color = '#1a3450'

        # Segmented control
        self.seg = ui.SegmentedControl()
        self.seg.segments = LABELS[:]
        self.seg.selected_index = 0
        self.seg.tint_color = FSH_YELLOW
        self.seg.action = self._on_segment
        self.add_subview(self.seg)

        # Original toggle button (sits above editor)
        self.btn_orig = ui.Button()
        self.btn_orig.title = 'Original'
        self.btn_orig.font = ('Helvetica Neue', 12)
        self.btn_orig.background_color = '#0f2030'
        self.btn_orig.tint_color = '#888'
        self.btn_orig.corner_radius = 4
        self.btn_orig.action = self._on_toggle_original
        self.add_subview(self.btn_orig)

        # Preview
        self.preview = ui.WebView()
        self.preview.scales_page_to_fit = True
        self.add_subview(self.preview)

        # Editor
        self.editor = ui.TextView()
        self.editor.font = ('Menlo', 13)
        self.editor.background_color = '#0f2030'
        self.editor.text_color = '#e8e8e8'
        self.editor.autocorrection_type = False
        self.editor.autocapitalization_type = ui.AUTOCAPITALIZE_NONE
        self.editor.delegate = self
        self.add_subview(self.editor)

        # Validation bar
        self.val_bar = ui.Label()
        self.val_bar.font = ('Helvetica Neue', 11)
        self.val_bar.number_of_lines = 0
        self.val_bar.hidden = True
        self.add_subview(self.val_bar)

        # Toolbar: Save | Revert | Preview page | Commit
        btn_specs = [
            ('Save',         self._on_save,    FSH_BLUE,  '#fff'),
            ('Revert',       self._on_revert,  '#5a2020', '#fff'),
            ('Preview page', self._on_preview, FSH_BLUE,  FSH_YELLOW),
            ('Commit',       self._on_commit,  '#1a6e32', '#fff'),
        ]
        self.btn_save   = None
        self.btn_revert = None
        self.btn_commit = None
        self.buttons = []
        for i, (label, action, bg, fg) in enumerate(btn_specs):
            b = ui.Button()
            b.title = label
            b.background_color = bg
            b.tint_color = fg
            b.corner_radius = 6
            b.action = action
            self.add_subview(b)
            self.buttons.append(b)
            if label == 'Save':    self.btn_save   = b
            if label == 'Revert':  self.btn_revert = b
            if label == 'Commit':  self.btn_commit = b

        self._load_current()
        self._update_buttons()
        self._refresh_preview()

    def layout(self):
        w, h   = self.width, self.height
        pad    = 8
        seg_h  = 36
        btn_h  = 40
        orig_h = 28
        val_h  = 0

        self.seg.frame = (pad, pad, w - pad*2, seg_h)

        # Validation bar
        if self.val_bar.text and not self.val_bar.hidden:
            val_h = 44
        self.val_bar.frame = (0, h - btn_h - pad - val_h, w, val_h)

        # Toolbar
        n     = len(self.buttons)
        btn_w = (w - pad * (n + 1)) / n
        for i, b in enumerate(self.buttons):
            b.frame = (pad + i * (btn_w + pad), h - btn_h - pad, btn_w, btn_h)

        # Content area
        content_y = pad + seg_h + pad
        content_h = h - content_y - btn_h - val_h - pad*2

        landscape = (w > h) and (self.current_file != 'hero')

        if landscape:
            half = (w - pad * 3) / 2
            preview_x, preview_y = pad, content_y
            preview_w, preview_h = half, content_h
            orig_x = pad*2 + half
            editor_x, editor_y = pad*2 + half, content_y + orig_h + pad
            editor_w = half
            editor_h = content_h - orig_h - pad
        else:
            half = (content_h - orig_h - pad*2) / 2
            preview_x, preview_y = pad, content_y
            preview_w, preview_h = w - pad*2, half
            orig_x = pad
            editor_x = pad
            editor_y = content_y + half + orig_h + pad*2
            editor_w = w - pad*2
            editor_h = half

        self.preview.frame  = (preview_x, preview_y, preview_w, preview_h)
        self.btn_orig.frame = (orig_x, preview_y + preview_h + pad, 90, orig_h)
        self.editor.frame   = (editor_x, editor_y, editor_w, editor_h)

    # ── Segment labels ────────────────────────────────────────────────────────

    def _update_seg_labels(self):
        self.seg.segments = [
            f'{LABELS[i]} ●' if self._is_dirty(FILES[i]) else LABELS[i]
            for i in range(len(FILES))
        ]

    # ── Button states ─────────────────────────────────────────────────────────

    def _update_buttons(self):
        dirty = self._is_dirty()
        self.btn_save.alpha   = 1.0 if dirty else 0.35
        self.btn_save.enabled = dirty
        self.btn_revert.alpha   = 1.0 if dirty else 0.35
        self.btn_revert.enabled = dirty
        self.btn_commit.alpha   = 1.0 if self.needs_commit else 0.35
        self.btn_commit.enabled = self.needs_commit
        # Original toggle: only meaningful when dirty
        self.btn_orig.tint_color = FSH_YELLOW if (dirty and self.show_original) else \
                                   '#aaa'      if dirty else '#444'

    # ── Content switching ─────────────────────────────────────────────────────

    def _load_current(self):
        self.show_original = False
        self.editor.text = self.texts[self.current_file]

    def _on_segment(self, sender):
        self.texts[self.current_file] = self.editor.text
        self.current_idx = sender.selected_index
        self._load_current()
        self.layout()
        self._refresh_preview()
        self._show_validation()
        self._update_buttons()

    def _navigate(self, delta):
        """Move to adjacent file — called by swipe."""
        self.texts[self.current_file] = self.editor.text
        self.current_idx = (self.current_idx + delta) % len(FILES)
        self.seg.selected_index = self.current_idx
        self._load_current()
        self.layout()
        self._refresh_preview()
        self._show_validation()
        self._update_buttons()

    # ── Swipe to navigate ─────────────────────────────────────────────────────

    def touch_began(self, touch):
        self._touch_start = touch.location

    def touch_ended(self, touch):
        if not self._touch_start:
            return
        dx = touch.location[0] - self._touch_start[0]
        dy = touch.location[1] - self._touch_start[1]
        if abs(dx) > 60 and abs(dx) > abs(dy) * 1.5:
            self._navigate(1 if dx < 0 else -1)
        self._touch_start = None

    # ── Original toggle ───────────────────────────────────────────────────────

    def _on_toggle_original(self, sender):
        if not self._is_dirty():
            return
        self.show_original = not self.show_original
        self._update_buttons()
        self._refresh_preview()

    # ── Preview ───────────────────────────────────────────────────────────────

    def _refresh_preview(self):
        text = (self.original_texts[self.current_file]
                if self.show_original else
                (self.editor.text or ''))
        self.preview.load_html(col_preview_html(text))

    def _schedule_preview(self):
        if self._preview_timer:
            self._preview_timer.cancel()
        self._preview_timer = threading.Timer(0.5, self._refresh_preview)
        self._preview_timer.start()

    def _on_preview(self, sender):
        self.texts[self.current_file] = self.editor.text
        pv = ui.WebView()
        pv.scales_page_to_fit = True
        pv.load_html(full_page_html(self.texts))
        pv.present('fullscreen')

    # ── Validation ────────────────────────────────────────────────────────────

    def _show_validation(self):
        errs = validate_text(self.current_file, self.editor.text or '')
        if errs:
            self.val_bar.text = '  ⚠ ' + '  ·  '.join(errs)
            self.val_bar.background_color = '#fff3e0'
            self.val_bar.text_color = '#6d3a00'
            self.val_bar.hidden = False
        else:
            self.val_bar.hidden = True
        self.layout()

    # ── Save ──────────────────────────────────────────────────────────────────

    def _on_save(self, sender):
        if not self.btn_save.enabled:
            return
        self.texts[self.current_file] = self.editor.text
        self._save_all()

    # ── Revert ────────────────────────────────────────────────────────────────

    def _on_revert(self, sender):
        if not self.btn_revert.enabled:
            return
        self.texts[self.current_file] = self.original_texts[self.current_file]
        self.show_original = False
        self._load_current()
        self._update_seg_labels()
        self._update_buttons()
        self._refresh_preview()
        self._show_validation()

    # ── Commit ────────────────────────────────────────────────────────────────

    def _on_commit(self, sender):
        if not self.btn_commit.enabled:
            return
        self.texts[self.current_file] = self.editor.text
        all_errors = validate_all(self.texts)
        if all_errors:
            import console
            lines = [f'{n}.md: ' + ', '.join(e) for n, e in all_errors.items()]
            console.alert('Validation failed', '\n'.join(lines), 'OK', hide_cancel_button=True)
            return
        self._save_all()
        webbrowser.open(f'working-copy://commit?repo={REPO_ROOT.name}')

    # ── TextView delegate ─────────────────────────────────────────────────────

    def textview_did_change(self, textview):
        self.texts[self.current_file] = textview.text
        self._update_seg_labels()
        self._update_buttons()
        self._schedule_preview()
        self._show_validation()


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    v = FSHEditor()
    v.name = 'FSH Editor'
    v.present('fullscreen', hide_title_bar=False,
              orientations=['landscape', 'portrait'])


if __name__ == '__main__':
    main()
