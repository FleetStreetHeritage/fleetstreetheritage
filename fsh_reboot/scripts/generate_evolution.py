#!/usr/bin/env python3
"""
FSH Evolution static site generator.
Extends generate.py: uses index_evolution.html driven by markdown content files
in docs/dev/content/col{1,2,3}.md.

Usage:
  python fsh_reboot/scripts/generate_evolution.py            # staging
  python fsh_reboot/scripts/generate_evolution.py --prod     # production
"""

import json
import re
import sys
from pathlib import Path

# Shared logic from generate.py (main() is guarded so it won't run on import)
sys.path.insert(0, str(Path(__file__).parent))
import generate as gen

CONTENT_DIR = Path(__file__).parent.parent.parent / 'docs' / 'dev' / 'content'


# ── Markdown parser ──────────────────────────────────────────────────────────

def inline_md(text):
    """Handle inline markdown: linked images, links, bold, italic."""
    # Linked image [![alt](src)](url) — must come before plain link
    text = re.sub(
        r'\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)',
        lambda m: (f'<a href="{m.group(3)}">'
                   f'<img src="{m.group(2)}" alt="{m.group(1)}" class="col-img">'
                   f'</a>'),
        text
    )
    # Plain link
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # Italic
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
            # Linked image on its own line
            m = re.match(r'\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)', line)
            if m:
                parts.append(
                    f'<a href="{m.group(3)}">'
                    f'<img src="{m.group(2)}" alt="{m.group(1)}" class="col-img">'
                    f'</a>'
                )
            i += 1

        elif line.startswith('!['):
            # Standalone image
            m = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', line)
            if m:
                parts.append(f'<img src="{m.group(2)}" alt="{m.group(1)}" class="col-img">')
            i += 1

        elif line.startswith('- '):
            # Unordered list
            items = []
            while i < len(lines) and lines[i].rstrip().startswith('- '):
                items.append(f'<li>{inline_md(lines[i][2:])}</li>')
                i += 1
            parts.append('<ul class="col-list">' + ''.join(items) + '</ul>')

        else:
            # Paragraph: collect consecutive non-special lines
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


# ── Index (evolution) ────────────────────────────────────────────────────────

def generate_index_evolution(pages):
    # Volume sections (same logic as gen.generate_index)
    volumes = {}
    for page in pages:
        volumes.setdefault(page['volume'], []).append(page)

    sections_html = []
    for v in sorted(volumes):
        items = ''.join(
            f'      <li><a href="nl/{p["slug"]}.html">{p["title"]}</a></li>\n'
            for p in volumes[v] if p.get('live', True)
        )
        sections_html.append(
            f'      <section class="volume" aria-labelledby="vol-{v}-heading">\n'
            f'        <h2 class="volume-heading" id="vol-{v}-heading">{gen.VOLUME_LABELS[v]}</h2>\n'
            f'        <ul class="page-grid">\n'
            f'{items}'
            f'        </ul>\n'
            f'      </section>\n'
        )

    # Read and parse content markdown files
    def load_md(filename):
        path = CONTENT_DIR / filename
        if not path.exists() or not path.read_text(encoding='utf-8').strip():
            return ''
        return md_to_html(path.read_text(encoding='utf-8'))

    hero_inner   = load_md('hero.md')
    hero_block   = f'<div class="hero">{hero_inner}</div>' if hero_inner else ''

    banner_inner = load_md('banner.md')
    banner_block = f'<div class="book-banner">{banner_inner}</div>' if banner_inner else ''

    col_html = []
    for n in (1, 2, 3):
        col_html.append(load_md(f'col{n}.md'))

    html = (
        gen.load_template('index_evolution.html')
        .replace('<!-- GA_ID -->',           gen.GA_ID)
        .replace('<!-- HERO_BLOCK -->',      hero_block)
        .replace('<!-- BANNER_BLOCK -->',    banner_block)
        .replace('<!-- COL_1 -->',           col_html[0])
        .replace('<!-- COL_2 -->',           col_html[1])
        .replace('<!-- COL_3 -->',           col_html[2])
        .replace('<!-- VOLUME_SECTIONS -->', '\n'.join(sections_html))
    )
    (gen.OUTPUT_DIR / 'index_evolution.html').write_text(html, encoding='utf-8')


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    with open(gen.DATA_FILE, encoding='utf-8') as f:
        pages = json.load(f)['pages']

    for d in (gen.OUTPUT_DIR, gen.NL_DIR, gen.EASY_DIR, gen.QR_DIR,
              gen.ADMIN_DIR, gen.LIVE_QR_DIR):
        d.mkdir(parents=True, exist_ok=True)

    counts = {'nl': 0, 'easy': 0, 'qr': 0}
    pages_with_status = []

    for i, page in enumerate(pages):
        prev_page = pages[i - 1] if i > 0 else None
        next_page = pages[i + 1] if i < len(pages) - 1 else None

        has_pdf   = (gen.PDFS_DIR  / f"{page['num']}.pdf").exists()
        has_easy  = (gen.PDFS_DIR  / f"E_{page['num']}.pdf").exists()
        has_audio = (gen.AUDIO_DIR / f"{page['num']}.mp3").exists()

        pages_with_status.append(
            {**page, 'has_pdf': has_pdf, 'has_easy': has_easy, 'has_audio': has_audio}
        )

        gen.generate_nl(page, prev_page, next_page, has_easy, has_audio)
        counts['nl'] += 1

        if has_easy:
            gen.generate_easy(page, prev_page, next_page, has_audio)
            counts['easy'] += 1

        gen.generate_qr(page, has_easy)
        gen.generate_live_qr(page, has_easy)
        counts['qr'] += 1

    gen.generate_index(pages)
    generate_index_evolution(pages)
    gen.generate_admin(pages_with_status)

    missing_pdfs = [p for p in pages_with_status if not p['has_pdf']]
    if missing_pdfs:
        print(f"  ⚠  {len(missing_pdfs)} page(s) missing main PDF:")
        for p in missing_pdfs:
            print(f"     {p['num']} – {p['title']}")

    mode = 'PRODUCTION' if gen.PROD_MODE else 'STAGING'
    print(f"==============")
    print(f"generate_evolution.py in [{mode}] mode:")
    print(f"++++++++++++++")
    print(f"Generated products as follows:")
    print(f"  {gen.OUTPUT_DIR}/index.html  (plain listing, from index.html template)")
    print(f"  {gen.OUTPUT_DIR}/index_evolution.html  (from index_evolution.html + content/col*.md)")
    print(f"  {gen.NL_DIR}/   ×{counts['nl']} NL pages")
    if counts['easy']:
        print(f"  {gen.EASY_DIR}/   ×{counts['easy']} Easy Read pages")
    print(f"  {gen.QR_DIR}/   ×{counts['qr']} QR redirects")
    print(f"  {gen.LIVE_QR_DIR}/   ×{counts['qr']} live QR redirects → {'prod' if gen.PROD_MODE else 'staging'} paths")
    print(f"  {gen.ADMIN_DIR}/index.html  +  pages-edit.html")
    print(f"==============")


if __name__ == '__main__':
    main()
