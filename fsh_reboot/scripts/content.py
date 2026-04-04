#!/usr/bin/env python3
"""
FSH content population.
Parses markdown files from docs/dev/content/ and returns HTML strings.
Called by generate.py; has no knowledge of output paths, templates, or GA IDs.

Supported markdown:
  #  heading        → large display heading (.col-title)
  ## heading        → small section heading (.col-heading)
  ![alt](src)       → image (.col-img)
  [![alt](src)](url)→ linked image
  [text](url)       → inline link (inside paragraphs)
  **bold**          → <strong>
  *italic*          → <em>
  - item            → unordered list (.col-list)
  blank line        → paragraph break
"""

import re
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / 'content'


# ── Markdown parser ───────────────────────────────────────────────────────────

def inline_md(text):
    """Handle inline markdown: linked images, links, bold, italic."""
    text = re.sub(
        r'\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)',
        lambda m: (f'<a href="{m.group(3)}">'
                   f'<img src="{m.group(2)}" alt="{m.group(1)}" class="col-img">'
                   f'</a>'),
        text
    )
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    return text


def md_to_html(md):
    """Convert a small markdown subset to HTML fragments."""
    lines = md.strip().splitlines()
    parts = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if not line:
            i += 1

        elif line.startswith('# '):
            parts.append(f'<h2 class="col-title">{inline_md(line[2:])}</h2>')
            i += 1

        elif line.startswith('## '):
            parts.append(f'<h2 class="col-heading">{inline_md(line[3:])}</h2>')
            i += 1

        elif line.startswith('[!['):
            m = re.match(r'\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)', line)
            if m:
                parts.append(
                    f'<a href="{m.group(3)}">'
                    f'<img src="{m.group(2)}" alt="{m.group(1)}" class="col-img">'
                    f'</a>'
                )
            i += 1

        elif line.startswith('!['):
            m = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', line)
            if m:
                parts.append(f'<img src="{m.group(2)}" alt="{m.group(1)}" class="col-img">')
            i += 1

        elif line == '---' or line == '***' or line == '___':
            parts.append('<hr>')
            i += 1

        elif line.startswith('- '):
            items = []
            while i < len(lines) and lines[i].rstrip().startswith('- '):
                items.append(f'<li>{inline_md(lines[i][2:])}</li>')
                i += 1
            parts.append('<ul class="col-list">' + ''.join(items) + '</ul>')

        elif re.match(r'^\d+\. ', line):
            items = []
            while i < len(lines) and re.match(r'^\d+\. ', lines[i].rstrip()):
                text = re.sub(r'^\d+\. ', '', lines[i])
                items.append(f'<li>{inline_md(text)}</li>')
                i += 1
            parts.append('<ol>' + ''.join(items) + '</ol>')

        else:
            para = []
            while i < len(lines):
                l = lines[i].rstrip()
                if not l or l.startswith(('#', '-', '!')):
                    break
                para.append(inline_md(l))
                i += 1
            if para:
                parts.append(f'<p>{" ".join(para)}</p>')

    return '\n'.join(parts)


def _load(filename, content_dir=None):
    """Read and parse one content file. Returns '' if absent or empty."""
    path = (content_dir or CONTENT_DIR) / filename
    if not path.exists():
        return ''
    text = path.read_text(encoding='utf-8').strip()
    return md_to_html(text) if text else ''


# ── Public API ────────────────────────────────────────────────────────────────

def get_blocks(content_dir=None):
    """Return a dict of HTML strings for all content blocks.
    Pass content_dir to read from an alternative directory (e.g. content_draft/).
    """
    hero_inner   = _load('hero.md',   content_dir)
    banner_inner = _load('banner.md', content_dir)
    return {
        'hero_block':   f'<div class="hero">{hero_inner}</div>' if hero_inner else '',
        'banner_block': f'<div class="book-banner">{banner_inner}</div>' if banner_inner else '',
        'col1':         _load('col1.md', content_dir),
        'col2':         _load('col2.md', content_dir),
        'col3':         _load('col3.md', content_dir),
    }
