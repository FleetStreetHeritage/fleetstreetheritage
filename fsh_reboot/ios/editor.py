#!/usr/bin/env python3
# build 4
"""
FSH Content Editor — Pythonista iOS app
Edit and preview content markdown files for the Fleet Street Heritage website.

Stored in fsh_reboot/ios/editor.py in the repo.
Open and run from Working Copy via Pythonista.
"""

import ui
import re
import os
import sys
import threading
import webbrowser
from pathlib import Path

# ── Paths (derived from script location) ─────────────────────────────────────
# fsh_reboot/ios/editor.py → parent.parent = fsh_reboot/ → parent = repo root
REPO_ROOT    = Path(__file__).resolve().parent.parent.parent
CONTENT_DIR  = REPO_ROOT / 'fsh_reboot' / 'content'
TEMPLATE     = REPO_ROOT / 'fsh_reboot' / 'template' / 'index_evolution.html'
IMAGES_DIR   = REPO_ROOT / 'docs' / 'dev' / 'images'

SCRIPTS_DIR  = REPO_ROOT / 'fsh_reboot' / 'scripts'
sys.path.insert(0, str(SCRIPTS_DIR))
import content as cnt

md_to_html = cnt.md_to_html

# ── Content files ─────────────────────────────────────────────────────────────
FILES  = ['hero',  'banner', 'col1',  'col2',  'col3']
LABELS = ['Hero',  'Banner', 'Col 1', 'Col 2', 'Col 3']

# ── Colours ───────────────────────────────────────────────────────────────────
FSH_BLUE   = '#254760'
FSH_YELLOW = '#FFFF66'


# ── Validation ────────────────────────────────────────────────────────────────

def validate_text(filename, text):
    """Return list of error strings; empty list means clean."""
    errors = []
    for m in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', text):
        src = m.group(2)
        if src.startswith('http'):
            continue
        # Resolve relative to images dir
        img = IMAGES_DIR / Path(src).name
        if not img.exists():
            errors.append(f'Image not found: {src}')
    opens  = text.count('[')
    closes = text.count(']')
    if opens != closes:
        errors.append(f'Unbalanced brackets: {opens} [ vs {closes} ]')
    lparen = len(re.findall(r'\]\(', text))
    rparen = len(re.findall(r'\]\([^)]*\)', text))
    if lparen != rparen:
        errors.append('Unclosed link parenthesis')
    return errors


def validate_all(texts):
    """Validate all files. Returns dict of filename → [errors]."""
    results = {}
    for name, text in texts.items():
        errs = validate_text(name, text)
        if errs:
            results[name] = errs
    return results


# ── HTML rendering ────────────────────────────────────────────────────────────

COL_CSS = """
  body {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.9rem;
    line-height: 1.6;
    background: #254760;
    color: #ffffff;
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
  p { margin-bottom: 0.6rem; }
  a { color: #FFFF66; text-decoration: underline; }
  ul { list-style: none; margin-top: 0.5rem; font-size: 0.85rem; }
  img { display: block; width: 100%; max-width: 220px; height: auto; margin-bottom: 0.75rem; }
"""


def abs_images(html, images_dir):
    """Rewrite relative img src attributes to absolute file:// URLs."""
    def replace(m):
        src = m.group(1)
        if src.startswith('http') or src.startswith('file'):
            return m.group(0)
        abs_path = images_dir / Path(src).name
        return f'src="{abs_path.as_uri()}"'
    return re.sub(r'src="([^"]+)"', replace, html)


def col_preview_html(text):
    body = md_to_html(text) if text.strip() else '<p style="color:#aaa">(empty)</p>'
    return f'<html><head><meta name="viewport" content="width=device-width"><style>{COL_CSS}</style></head><body>{body}</body></html>'


def full_page_html(texts):
    """Render the complete index_evolution page with current content."""
    if not TEMPLATE.exists():
        return '<html><body><p>Template not found.</p></body></html>'

    def block(name, wrapper_open, wrapper_close):
        inner = md_to_html(texts.get(name, ''))
        return f'{wrapper_open}{inner}{wrapper_close}' if inner.strip() else ''

    hero_block   = block('hero',   '<div class="hero">',        '</div>')
    banner_block = block('banner', '<div class="book-banner">', '</div>')
    col1 = md_to_html(texts.get('col1', ''))
    col2 = md_to_html(texts.get('col2', ''))
    col3 = md_to_html(texts.get('col3', ''))

    html = (TEMPLATE.read_text(encoding='utf-8')
            .replace('<!-- GA_ID -->',        'GA-PREVIEW')
            .replace('<!-- HERO_BLOCK -->',   hero_block)
            .replace('<!-- BANNER_BLOCK -->', banner_block)
            .replace('<!-- COL_1 -->',        col1)
            .replace('<!-- COL_2 -->',        col2)
            .replace('<!-- COL_3 -->',        col3)
            .replace('<!-- VOLUME_SECTIONS -->', '<p style="color:rgba(255,255,255,0.4);font-size:0.8rem;text-align:center">(page listing not shown in preview)</p>'))
    return html


# ── Main editor view ──────────────────────────────────────────────────────────

class FSHEditor(ui.View):
    def __init__(self):
        self.current_file = FILES[0]
        self.texts = {}          # filename → current text in editor
        self.dirty = set()       # filenames with unsaved changes
        self._preview_timer = None

        self._load_all_files()
        self._build_ui()

    # ── File I/O ──────────────────────────────────────────────────────────────

    def _load_all_files(self):
        for name in FILES:
            path = CONTENT_DIR / f'{name}.md'
            self.texts[name] = path.read_text(encoding='utf-8') if path.exists() else ''

    def _save_file(self, name):
        path = CONTENT_DIR / f'{name}.md'
        path.write_text(self.texts[name], encoding='utf-8')
        self.dirty.discard(name)
        self._update_title()

    def _save_current(self):
        self._save_file(self.current_file)

    def _save_all(self):
        for name in FILES:
            if name in self.dirty:
                self._save_file(name)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        self.background_color = '#1a3450'

        # Segmented control
        self.seg = ui.SegmentedControl()
        self.seg.segments = LABELS
        self.seg.selected_index = 0
        self.seg.tint_color = FSH_YELLOW
        self.seg.action = self._on_segment
        self.add_subview(self.seg)

        # Editor (left / top)
        self.editor = ui.TextView()
        self.editor.font = ('Menlo', 13)
        self.editor.background_color = '#0f2030'
        self.editor.text_color = '#e8e8e8'
        self.editor.autocorrection_type = False
        self.editor.autocapitalization_type = ui.AUTOCAPITALIZE_NONE
        self.editor.delegate = self
        self.add_subview(self.editor)

        # Preview (right / bottom)
        self.preview = ui.WebView()
        self.preview.scales_page_to_fit = True
        self.add_subview(self.preview)

        # Validation bar
        self.val_bar = ui.Label()
        self.val_bar.font = ('Helvetica Neue', 11)
        self.val_bar.number_of_lines = 0
        self.val_bar.background_color = '#e8f5e9'
        self.val_bar.text_color = '#1e5c2a'
        self.val_bar.hidden = True
        self.add_subview(self.val_bar)

        # Toolbar buttons
        btn_specs = [
            ('Save',         self._on_save,    '#254760', '#ffffff'),
            ('Preview page', self._on_preview, '#254760', FSH_YELLOW),
            ('Commit',       self._on_commit,  '#1a6e32', '#ffffff'),
        ]
        self.buttons = []
        for label, action, bg, fg in btn_specs:
            b = ui.Button()
            b.title = label
            b.background_color = bg
            b.tint_color = fg
            b.corner_radius = 6
            b.action = action
            self.add_subview(b)
            self.buttons.append(b)

        self._load_current()
        self._refresh_preview()

    def layout(self):
        w, h = self.width, self.height
        pad = 8
        seg_h = 36
        btn_h = 40
        val_h = 0

        # Segmented control
        self.seg.frame = (pad, pad, w - pad*2, seg_h)

        # Validation bar (above toolbar, hidden until needed)
        val_text = self.val_bar.text or ''
        if val_text and not self.val_bar.hidden:
            val_h = 44
        self.val_bar.frame = (0, h - btn_h - val_h, w, val_h)

        # Toolbar
        n = len(self.buttons)
        btn_w = (w - pad * (n + 1)) / n
        for i, b in enumerate(self.buttons):
            b.frame = (pad + i * (btn_w + pad), h - btn_h - pad, btn_w, btn_h)

        # Editor and preview
        content_y = pad + seg_h + pad
        content_h = h - content_y - btn_h - val_h - pad*2

        landscape = w > h
        if landscape:
            half = (w - pad * 3) / 2
            self.editor.frame  = (pad,          content_y, half, content_h)
            self.preview.frame = (pad*2 + half,  content_y, half, content_h)
        else:
            half = (content_h - pad) / 2
            self.editor.frame  = (pad, content_y,          w - pad*2, half)
            self.preview.frame = (pad, content_y + half + pad, w - pad*2, half)

    # ── Content switching ─────────────────────────────────────────────────────

    def _load_current(self):
        self.editor.text = self.texts[self.current_file]

    def _on_segment(self, sender):
        # Save current text before switching
        self.texts[self.current_file] = self.editor.text
        self.current_file = FILES[sender.selected_index]
        self._load_current()
        self._refresh_preview()
        self._show_validation()

    # ── Preview ───────────────────────────────────────────────────────────────

    def _refresh_preview(self):
        text = self.editor.text if self.editor.text is not None else ''
        html = col_preview_html(text)
        html = abs_images(html, REPO_ROOT / 'docs' / 'dev' / 'images')
        self.preview.load_html(html)

    def _schedule_preview(self):
        if self._preview_timer:
            self._preview_timer.cancel()
        self._preview_timer = threading.Timer(0.5, self._refresh_preview)
        self._preview_timer.start()

    def _on_preview(self, sender):
        self.texts[self.current_file] = self.editor.text
        html = full_page_html(self.texts)
        pv = ui.WebView()
        pv.scales_page_to_fit = True
        html = abs_images(html, REPO_ROOT / 'docs' / 'dev' / 'images')
        pv.load_html(html)
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
        self.texts[self.current_file] = self.editor.text
        self._save_all()
        self._update_title()

    def _update_title(self):
        unsaved = len(self.dirty)
        self.name = f'FSH Editor{"  •" * unsaved}'

    # ── Commit ────────────────────────────────────────────────────────────────

    def _on_commit(self, sender):
        self.texts[self.current_file] = self.editor.text

        # Validate all files first
        all_errors = validate_all(self.texts)
        if all_errors:
            lines = []
            for fname, errs in all_errors.items():
                lines.append(f'{fname}.md: ' + ', '.join(errs))
            import console
            console.alert('Validation failed', '\n'.join(lines), 'OK', hide_cancel_button=True)
            return

        # Save all files
        self._save_all()

        # Open Working Copy to commit
        # URL scheme: working-copy://commit?repo=fleetstreetheritage
        repo = REPO_ROOT.name
        url  = f'working-copy://commit?repo={repo}'
        webbrowser.open(url)

    # ── TextView delegate ─────────────────────────────────────────────────────

    def textview_did_change(self, textview):
        self.texts[self.current_file] = textview.text
        self.dirty.add(self.current_file)
        self._update_title()
        self._schedule_preview()
        self._show_validation()


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    v = FSHEditor()
    v.name = 'FSH Editor'
    v.present('fullscreen', hide_title_bar=False, orientations=['landscape', 'portrait'])


if __name__ == '__main__':
    main()
