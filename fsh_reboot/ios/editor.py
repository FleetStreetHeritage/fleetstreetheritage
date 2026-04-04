#!/usr/bin/env python3
# build 16
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
CONTENT_DIR = REPO_ROOT / 'fsh_reboot' / 'content_draft'
LIVE_DIR    = REPO_ROOT / 'fsh_reboot' / 'content'
TEMPLATE    = REPO_ROOT / 'fsh_reboot' / 'template' / 'index_evolution.html'
IMAGES_DIR  = REPO_ROOT / 'docs' / 'dev' / 'images'
SCRIPTS_DIR = REPO_ROOT / 'fsh_reboot' / 'scripts'

sys.path.insert(0, str(SCRIPTS_DIR))
import content as cnt
md_to_html = cnt.md_to_html

FILES  = ['hero',  'col1',  'col2',  'col3',  'banner']
LABELS = ['Hero',  'Col 1', 'Col 2', 'Col 3', 'Banner']

FSH_BLUE   = '#254760'
FSH_YELLOW = '#FFFF66'


# ── Validation ────────────────────────────────────────────────────────────────

def validate_text(filename, text):
    errors = []
    for m in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', text):
        src = m.group(2)
        if not src.startswith('http') and not (IMAGES_DIR / Path(src).name).exists():
            errors.append(f'Image not found: {src}')
    if text.count('[') != text.count(']'):
        errors.append('Unbalanced brackets')
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


# ── Preview container ─────────────────────────────────────────────────────────

class _PreviewContainer(ui.View):
    """Full-page preview — dark overlay frame, cycle + dismiss buttons at bottom."""
    INSET  = 14
    BTN_H  = 42

    _STATE_LABELS = {0: '🔄 Editing', 1: '🔄 Saved', 2: '🔄 Live'}
    _STATE_COLORS = {0: '#aaa',       1: '#ffcc44',  2: FSH_YELLOW}

    def __init__(self, all_texts, on_close, initial_state=0):
        """all_texts: {'editing': {name: text}, 'saved': ..., 'live': ...}"""
        self._all_texts  = all_texts
        self._on_close   = on_close
        self._state      = initial_state
        self.background_color = '#08181f'  # dark, slightly distinct from editor

        # WebView — inset on all sides to show the dark frame border
        wv = ui.WebView()
        wv.scales_page_to_fit = True
        wv.corner_radius = 6
        self._wv = wv
        self.add_subview(wv)

        # Cycle button (left)
        cyc = ui.Button()
        cyc.font = ('Helvetica Neue', 14)
        cyc.background_color = FSH_BLUE
        cyc.corner_radius = 6
        cyc.action = self._on_cycle
        self._cyc = cyc
        self.add_subview(cyc)

        # Dismiss button (right) — same styling as Preview page button
        dis = ui.Button()
        dis.title = 'Dismiss preview'
        dis.tint_color = FSH_YELLOW
        dis.font = ('Helvetica Neue', 14)
        dis.background_color = FSH_BLUE
        dis.corner_radius = 6
        dis.action = self._close
        self._dis = dis
        self.add_subview(dis)

        self._update_cycle()
        self._load_html()

    def layout(self):
        w, h  = self.width, self.height
        i     = self.INSET
        bh    = self.BTN_H
        self._wv.frame  = (i, i, w - i*2, h - i*3 - bh)
        btn_y = h - i - bh
        half  = (w - i*3) / 2
        self._cyc.frame = (i,        btn_y, half, bh)
        self._dis.frame = (i*2+half, btn_y, half, bh)

    def _on_cycle(self, sender):
        self._state = (self._state + 1) % 3
        self._update_cycle()
        self._load_html()

    def _update_cycle(self):
        self._cyc.title      = self._STATE_LABELS[self._state]
        self._cyc.tint_color = self._STATE_COLORS[self._state]

    def _load_html(self):
        key   = {0: 'editing', 1: 'saved', 2: 'live'}[self._state]
        texts = self._all_texts[key]
        self._wv.load_html(full_page_html(texts))

    def _close(self, sender):
        self.close()

    def will_close(self):
        ui.delay(self._on_close, 0.1)


# ── Editor ────────────────────────────────────────────────────────────────────

class FSHEditor(ui.View):

    def __init__(self):
        self.current_idx    = 0
        self.original_texts = {}  # texts as last saved to content_draft/
        self.live_texts     = {}  # texts from content/ (published live)
        self.texts          = {}  # current in-editor texts
        self.pending_commit = set()  # saved but not yet committed
        self.show_state     = 0   # 0=current  1=saved-draft  2=live
        self._preview_timer = None
        self._touch_start   = None
        self._kb_height     = 0

        self._load_all_files()
        self._build_ui()

    # ── File I/O ──────────────────────────────────────────────────────────────

    def _load_all_files(self):
        for name in FILES:
            path = CONTENT_DIR / f'{name}.md'
            t = path.read_text(encoding='utf-8') if path.exists() else ''
            self.original_texts[name] = t
            self.texts[name] = t
            live_path = LIVE_DIR / f'{name}.md'
            self.live_texts[name] = (live_path.read_text(encoding='utf-8')
                                     if live_path.exists() else '')

    @property
    def current_file(self):
        return FILES[self.current_idx]

    def _is_dirty(self, name=None):
        name = name or self.current_file
        return self.texts[name] != self.original_texts[name]

    def _sync_editor(self):
        """Sync editor content into texts dict."""
        self.texts[self.current_file] = self.editor.text or ''

    def _save_all(self):
        for name in FILES:
            if self._is_dirty(name):
                (CONTENT_DIR / f'{name}.md').write_text(self.texts[name], encoding='utf-8')
                self.original_texts[name] = self.texts[name]
                self.pending_commit.add(name)
        self._update_seg_labels()
        self._update_buttons()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        self.background_color = '#1a3450'

        # Segmented control — lighter background so labels are readable
        self.seg = ui.SegmentedControl()
        self.seg.segments = LABELS[:]
        self.seg.selected_index = 0
        self.seg.tint_color = FSH_YELLOW
        self.seg.background_color = '#3a6a8a'
        self.seg.action = self._on_segment
        self.add_subview(self.seg)

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

        # Toolbar buttons — cycle | Revert | Save | Preview | Commit | Publish
        btn_specs = [
            ('🔄 Current',   self._on_cycle_state,     '#2a4a60', '#ccc'),
            ('Revert',       self._on_revert,           '#5a2020', '#fff'),
            ('Save',         self._on_save,             FSH_BLUE,  '#fff'),
            ('Preview page', self._on_preview,          FSH_BLUE,  FSH_YELLOW),
            ('Commit',       self._on_commit,           '#1a6e32', '#fff'),
            ('Publish',      self._on_publish,          '#7a4a00', FSH_YELLOW),
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

        self.btn_toggle  = self.buttons[0]
        self.btn_revert  = self.buttons[1]
        self.btn_save    = self.buttons[2]
        self.btn_commit  = self.buttons[4]
        self.btn_publish = self.buttons[5]

        self._load_current()
        self._update_buttons()
        self._refresh_preview()

    def layout(self):
        w, h = self.width, self.height
        if not w or not h:
            return

        pad   = 8
        seg_h = 36
        btn_h = 40
        val_h = 0

        # Seg always anchored at top — minimum below it before toolbar
        seg_bottom  = pad + seg_h + pad
        min_content = 80  # never let content area collapse to nothing
        max_kb      = h - seg_bottom - min_content - btn_h - pad
        kb = max(0, min(self._kb_height, max_kb))

        self.seg.frame = (pad, pad, w - pad*2, seg_h)

        # Validation bar sits just above toolbar
        if self.val_bar.text and not self.val_bar.hidden:
            val_h = 44
        toolbar_y = h - kb - btn_h - pad
        # Hard floor: toolbar can never overlap seg
        toolbar_y = max(seg_bottom + min_content, toolbar_y)
        self.val_bar.frame = (0, toolbar_y - val_h, w, val_h)

        # Toolbar
        n     = len(self.buttons)
        btn_w = (w - pad * (n + 1)) / n
        for i, b in enumerate(self.buttons):
            b.frame = (pad + i * (btn_w + pad), toolbar_y, btn_w, btn_h)

        # Content area (between seg and toolbar)
        content_y = pad + seg_h + pad
        content_h = max(40, toolbar_y - val_h - pad - content_y)

        landscape = (w > h) and (self.current_file != 'hero')

        if landscape:
            half = (w - pad * 3) / 2
            self.preview.frame = (pad,          content_y, half, content_h)
            self.editor.frame  = (pad*2 + half, content_y, half, content_h)
        else:
            half = (content_h - pad) / 2
            self.preview.frame = (pad, content_y,              w - pad*2, half)
            self.editor.frame  = (pad, content_y + half + pad, w - pad*2, half)

    # ── Keyboard avoidance ────────────────────────────────────────────────────

    def keyboard_frame_did_change(self, frame):
        screen_h = ui.get_screen_size()[1]
        kb_top   = frame[1]
        # If the keyboard top is at or beyond the screen bottom it's fully hidden
        self._kb_height = max(0, screen_h - kb_top) if kb_top < screen_h else 0
        self.layout()

    # ── Segment labels ────────────────────────────────────────────────────────

    def _update_seg_labels(self):
        labels = []
        for i, name in enumerate(FILES):
            label = LABELS[i]
            if self._is_dirty(name):
                label += ' ●'          # unsaved change
            elif name in self.pending_commit:
                label += ' ○'          # saved, awaiting commit
            labels.append(label)
        self.seg.segments = labels
        # restore selected index (reassigning segments resets it)
        self.seg.selected_index = self.current_idx

    # ── Button states ─────────────────────────────────────────────────────────

    def _update_buttons(self):
        dirty = self._is_dirty()
        has_pending = bool(self.pending_commit)

        # Cycle button: always enabled; label and colour reflect current view state
        _state_labels = {0: '🔄 Editing', 1: '🔄 Saved', 2: '🔄 Live'}
        _state_colors = {0: '#aaa', 1: '#ffcc44', 2: FSH_YELLOW}
        self.btn_toggle.title      = _state_labels[self.show_state]
        self.btn_toggle.tint_color = _state_colors[self.show_state]
        self.btn_toggle.enabled    = True
        self.btn_toggle.alpha      = 1.0

        # Revert: only when dirty
        self.btn_revert.enabled = dirty
        self.btn_revert.alpha   = 1.0 if dirty else 0.35

        # Save: only when any file dirty
        any_dirty = any(self._is_dirty(n) for n in FILES)
        self.btn_save.enabled = any_dirty
        self.btn_save.alpha   = 1.0 if any_dirty else 0.35

        # Commit: only when there is something saved to commit
        self.btn_commit.enabled = has_pending
        self.btn_commit.alpha   = 1.0 if has_pending else 0.35

        # Publish: same gate as commit — needs saved content to push
        self.btn_publish.enabled = has_pending
        self.btn_publish.alpha   = 1.0 if has_pending else 0.35

    # ── Content switching ─────────────────────────────────────────────────────

    def _load_current(self):
        self.show_state = 0
        self.editor.text = self.texts[self.current_file]

    def _on_segment(self, sender):
        self._sync_editor()
        self.current_idx = sender.selected_index
        self._kb_height = 0
        self._load_current()
        self.layout()
        self._refresh_preview()
        self._show_validation()
        self._update_buttons()

    def _navigate(self, delta):
        self._sync_editor()
        self.current_idx = (self.current_idx + delta) % len(FILES)
        self.seg.selected_index = self.current_idx
        self._kb_height = 0
        self._load_current()
        self.layout()
        self._refresh_preview()
        self._show_validation()
        self._update_buttons()

    # ── Swipe ─────────────────────────────────────────────────────────────────

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

    def _on_cycle_state(self, sender):
        self._sync_editor()
        self.show_state = (self.show_state + 1) % 3
        self._update_buttons()
        self._refresh_preview()

    # ── Preview ───────────────────────────────────────────────────────────────

    def _refresh_preview(self):
        if self.show_state == 2:
            text = self.live_texts.get(self.current_file, '')
        elif self.show_state == 1:
            text = self.original_texts[self.current_file]
        else:
            text = self.editor.text or ''
        self.preview.load_html(col_preview_html(text))

    def _schedule_preview(self):
        if self._preview_timer:
            self._preview_timer.cancel()
        # Timer fires on a background thread — dispatch UI update back to main thread
        self._preview_timer = threading.Timer(
            0.5, lambda: ui.delay(self._refresh_preview, 0)
        )
        self._preview_timer.start()

    def _on_preview(self, sender):
        self._sync_editor()
        all_texts = {
            'editing': dict(self.texts),
            'saved':   dict(self.original_texts),
            'live':    dict(self.live_texts),
        }
        pv = _PreviewContainer(all_texts, self._after_preview,
                               initial_state=self.show_state)
        pv.present('fullscreen', hide_title_bar=True)

    def _after_preview(self):
        self._kb_height = 0
        self.layout()

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
        self._sync_editor()
        self._save_all()

    # ── Revert ────────────────────────────────────────────────────────────────

    def _on_revert(self, sender):
        if not self.btn_revert.enabled:
            return
        self.texts[self.current_file] = self.original_texts[self.current_file]
        self._load_current()  # resets show_state to 0
        self._update_seg_labels()
        self._update_buttons()
        self._refresh_preview()
        self._show_validation()

    # ── Commit ────────────────────────────────────────────────────────────────

    def _on_commit(self, sender):
        if not self.btn_commit.enabled:
            return
        self._sync_editor()
        all_errors = validate_all(self.texts)
        if all_errors:
            import console
            lines = [f'{n}.md: ' + ', '.join(e) for n, e in all_errors.items()]
            console.alert('Validation failed', '\n'.join(lines), 'OK', hide_cancel_button=True)
            return
        self._save_all()
        self.pending_commit.clear()
        self._update_seg_labels()
        self._update_buttons()
        webbrowser.open(f'working-copy://commit?repo={REPO_ROOT.name}')

    # ── Publish ───────────────────────────────────────────────────────────────

    def _on_publish(self, sender):
        if not self.btn_publish.enabled:
            return
        self._sync_editor()
        all_errors = validate_all(self.texts)
        if all_errors:
            import console
            lines = [f'{n}.md: ' + ', '.join(e) for n, e in all_errors.items()]
            console.alert('Validation failed', '\n'.join(lines), 'OK', hide_cancel_button=True)
            return
        self._save_all()
        # Write the PUBLISH flag — GitHub Action will promote draft → content on next push
        (CONTENT_DIR / 'PUBLISH').write_text('', encoding='utf-8')
        self.pending_commit.clear()
        self._update_seg_labels()
        self._update_buttons()
        webbrowser.open(f'working-copy://commit?repo={REPO_ROOT.name}')

    # ── TextView delegate ─────────────────────────────────────────────────────

    def textview_did_change(self, textview):
        self.texts[self.current_file] = textview.text or ''
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
