#!/usr/bin/env python3
"""
FSH static site generator.
Reads fsh_reboot/data/pages.json, generates HTML pages into docs/dev/.

Usage:
  python fsh_reboot/scripts/generate.py            # staging (docs/dev/)
  python fsh_reboot/scripts/generate.py --prod     # production (docs/)
"""

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# ── Paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent
REPO_ROOT    = SCRIPT_DIR.parent.parent
DATA_FILE    = SCRIPT_DIR.parent / 'data' / 'pages.json'
TEMPLATE_DIR = SCRIPT_DIR.parent / 'template'
CONTENT_DIR  = SCRIPT_DIR.parent / 'content'
DRAFT_DIR    = SCRIPT_DIR.parent / 'editor' / 'content_draft'

CONTENT_FILES = ['hero.md', 'banner.md', 'col1.md', 'col2.md', 'col3.md']

PROD_MODE  = '--prod' in sys.argv
GA_ID      = 'G-E01B51HMZL' if PROD_MODE else 'G-ZP7L32M9GB'
OUTPUT_DIR = REPO_ROOT / 'docs' if PROD_MODE else REPO_ROOT / 'docs' / 'dev'
NL_DIR     = OUTPUT_DIR / 'nl'
EASY_DIR   = OUTPUT_DIR / 'easy'
QR_DIR     = OUTPUT_DIR / 'qr'
PDFS_DIR   = OUTPUT_DIR / 'pdfs'
AUDIO_DIR  = OUTPUT_DIR / 'audio'
ADMIN_DIR  = OUTPUT_DIR / 'admin'
EDITOR_DIR = OUTPUT_DIR / 'editor'

# Live QR codes always go to docs/qr/ regardless of mode.
# In staging they point into docs/dev/; in prod they point into docs/ root.
LIVE_QR_DIR   = REPO_ROOT / 'docs' / 'qr'
LIVE_NL_BASE  = '../nl/'   if PROD_MODE else '../dev/nl/'
LIVE_EASY_BASE = '../easy/' if PROD_MODE else '../dev/easy/'

# ── Template loading ────────────────────────────────────────────────────────
def load_template(name):
    return (TEMPLATE_DIR / name).read_text(encoding='utf-8')

# ── Substitution ────────────────────────────────────────────────────────────
def sub(template, replacements):
    result = template.replace('<!-- GA_ID -->', GA_ID)
    for key, value in replacements.items():
        result = result.replace(f'<!-- {key} -->', str(value))
    return result

# ── Nav URLs ─────────────────────────────────────────────────────────────────
def nl_url(page):
    """Relative URL to a page's NL wrapper, from within the nl/ directory."""
    return f"{page['slug']}.html" if page else '../index.html'

def nl_url_from_outside(page):
    """Relative URL to a page's NL wrapper, from outside the nl/ directory (e.g. easy/, qr/)."""
    return f"../nl/{page['slug']}.html" if page else '../index.html'

# ── Page generators ─────────────────────────────────────────────────────────
def generate_nl(page, prev_page, next_page, has_easy, has_audio):
    html = sub(load_template('wrapper.html'), {
        'PAGE_TITLE':       page['title'],
        'PAGE_DESCRIPTION': page['title'],
        'PAGE_ID':          page['slug'],
        'PAGE_NUM':         page['num'],
        'PDF_FILE':         f"../pdfs/{page['num']}.pdf",
        'AUDIO_FILE':       f"../audio/{page['num']}.mp3",
        'EASY_URL':         f"../easy/{page['slug']}.html",
        'NL_URL':           f"{page['slug']}.html",
        'HAS_AUDIO':        'true' if has_audio else 'false',
        'HAS_EASY':         'true' if has_easy else 'false',
        'PREV_URL':         nl_url(prev_page),
        'NEXT_URL':         nl_url(next_page),
    })
    (NL_DIR / f"{page['slug']}.html").write_text(html, encoding='utf-8')


def generate_easy(page, prev_page, next_page, has_audio):
    html = sub(load_template('wrapper-easy.html'), {
        'PAGE_TITLE':       page['title'],
        'PAGE_DESCRIPTION': page['title'],
        'PAGE_ID':          page['slug'],
        'PAGE_NUM':         page['num'],
        'EASY_PDF_FILE':    f"../pdfs/E_{page['num']}.pdf",
        'AUDIO_FILE':       f"../audio/{page['num']}.mp3",
        'NL_URL':           f"../nl/{page['slug']}.html",
        'HAS_AUDIO':        'true' if has_audio else 'false',
        # prev/next route back through NL; NL redirect logic respects easy pref
        'PREV_URL':         nl_url_from_outside(prev_page),
        'NEXT_URL':         nl_url_from_outside(next_page),
    })
    (EASY_DIR / f"{page['slug']}.html").write_text(html, encoding='utf-8')


def generate_qr(page, has_easy):
    html = sub(load_template('qr-redirect.html'), {
        'PAGE_ID':  page['slug'],
        'PAGE_NUM': page['num'],
        'NL_URL':   f"../nl/{page['slug']}.html",
        'EASY_URL': f"../easy/{page['slug']}.html" if has_easy else '',
    })
    (QR_DIR / f"{page['num']}.html").write_text(html, encoding='utf-8')


# ── Index page ──────────────────────────────────────────────────────────────
VOLUME_LABELS = {
    1: 'Volume I – People, Places, Monuments & History',
    2: 'Volume II – Biographies of Past Newspapers',
    3: 'Volume III – Biographies of Current Newspapers',
}

def build_volume_sections(pages):
    volumes = {}
    for page in pages:
        volumes.setdefault(page['volume'], []).append(page)
    sections = []
    for v in sorted(volumes):
        items = ''.join(
            f'      <li><a href="nl/{p["slug"]}.html">{p["title"]}</a></li>\n'
            for p in volumes[v] if p.get('live', True)
        )
        sections.append(
            f'      <section class="volume" aria-labelledby="vol-{v}-heading">\n'
            f'        <h2 class="volume-heading" id="vol-{v}-heading">{VOLUME_LABELS[v]}</h2>\n'
            f'        <ul class="page-grid">\n'
            f'{items}'
            f'        </ul>\n'
            f'      </section>\n'
        )
    return '\n'.join(sections)


def generate_index(pages):
    html = (load_template('index.html')
            .replace('<!-- GA_ID -->',           GA_ID)
            .replace('<!-- VOLUME_SECTIONS -->', build_volume_sections(pages)))
    (OUTPUT_DIR / 'index.html').write_text(html, encoding='utf-8')


def generate_index_evolution(pages):
    import content
    blocks = content.get_blocks()
    html = (load_template('index_evolution.html')
            .replace('<!-- GA_ID -->',           GA_ID)
            .replace('<!-- HERO_BLOCK -->',      blocks['hero_block'])
            .replace('<!-- BANNER_BLOCK -->',    blocks['banner_block'])
            .replace('<!-- COL_1 -->',           blocks['col1'])
            .replace('<!-- COL_2 -->',           blocks['col2'])
            .replace('<!-- COL_3 -->',           blocks['col3'])
            .replace('<!-- VOLUME_SECTIONS -->', build_volume_sections(pages)))
    (OUTPUT_DIR / 'index_evolution.html').write_text(html, encoding='utf-8')


def seed_draft():
    """Ensure content_draft/ exists and seed any missing files from content/."""
    DRAFT_DIR.mkdir(exist_ok=True)
    for filename in CONTENT_FILES:
        draft_file = DRAFT_DIR / filename
        if not draft_file.exists():
            src = CONTENT_DIR / filename
            if src.exists():
                shutil.copy2(src, draft_file)


def generate_index_draft(pages):
    """Generate index_draft.html from content_draft/ source files."""
    import content
    blocks = content.get_blocks(content_dir=DRAFT_DIR)
    html = (load_template('index_evolution.html')
            .replace('<!-- GA_ID -->',           GA_ID)
            .replace('<!-- HERO_BLOCK -->',      blocks['hero_block'])
            .replace('<!-- BANNER_BLOCK -->',    blocks['banner_block'])
            .replace('<!-- COL_1 -->',           blocks['col1'])
            .replace('<!-- COL_2 -->',           blocks['col2'])
            .replace('<!-- COL_3 -->',           blocks['col3'])
            .replace('<!-- VOLUME_SECTIONS -->', build_volume_sections(pages)))
    # index_draft lives one level deeper (editor/) so rewrite relative image paths
    html = html.replace('src="images/', 'src="../images/')
    (EDITOR_DIR / 'index_draft.html').write_text(html, encoding='utf-8')


def _render_editor_md(md_path):
    """Read a markdown file from the editor folder and return rendered HTML."""
    import content
    md = md_path.read_text(encoding='utf-8') if md_path.exists() else ''
    return content.md_to_html(md)


def generate_editor_hub():
    """Generate the editor hub page from WORKFLOW.md."""
    workflow_html = _render_editor_md(SCRIPT_DIR.parent / 'editor' / 'WORKFLOW.md')
    generated_at  = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    html = (load_template('editor-hub.html')
            .replace('<!-- GA_ID -->',            GA_ID)
            .replace('<!-- GENERATED_AT -->',     generated_at)
            .replace('<!-- BACK_LINK -->',        '')
            .replace('<!-- WORKFLOW_CONTENT -->', workflow_html))
    (EDITOR_DIR / 'index.html').write_text(html, encoding='utf-8')


def generate_markdown_ref():
    """Generate markdown.html reference page from MARKDOWN.md."""
    content_html = _render_editor_md(SCRIPT_DIR.parent / 'editor' / 'MARKDOWN.md')
    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    back = '<p style="margin-bottom:1.5rem"><a href="index.html" style="color:#FFFF66">← Editor home</a></p>'
    html = (load_template('editor-hub.html')
            .replace('<!-- GA_ID -->',            GA_ID)
            .replace('<!-- GENERATED_AT -->',     generated_at)
            .replace('<!-- BACK_LINK -->',        back)
            .replace('FSH Editor',                'Markdown reference')
            .replace('<!-- WORKFLOW_CONTENT -->', content_html))
    (EDITOR_DIR / 'markdown.html').write_text(html, encoding='utf-8')


# ── Live QR codes (docs/qr/) ────────────────────────────────────────────────
def generate_live_qr(page, has_easy):
    html = sub(load_template('qr-redirect.html'), {
        'PAGE_ID':  page['slug'],
        'PAGE_NUM': page['num'],
        'NL_URL':   f"{LIVE_NL_BASE}{page['slug']}.html",
        'EASY_URL': f"{LIVE_EASY_BASE}{page['slug']}.html" if has_easy else '',
    })
    (LIVE_QR_DIR / f"{page['num']}.html").write_text(html, encoding='utf-8')


# ── Admin page ──────────────────────────────────────────────────────────────
def generate_admin(pages_with_status):
    ADMIN_DIR.mkdir(parents=True, exist_ok=True)

    pages_json   = json.dumps(pages_with_status, ensure_ascii=False, indent=2)
    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    page_count   = str(len(pages_with_status))

    def render(template_name):
        return (load_template(template_name)
                .replace('<!-- PAGES_JSON -->',   pages_json)
                .replace('<!-- GENERATED_AT -->', generated_at)
                .replace('<!-- PAGE_COUNT -->',   page_count)
                .replace('<!-- GA_ID -->',        GA_ID))

    (ADMIN_DIR / 'index.html').write_text(render('admin.html'),      encoding='utf-8')
    (ADMIN_DIR / 'pages-edit.html').write_text(render('pages-edit.html'), encoding='utf-8')


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    with open(DATA_FILE, encoding='utf-8') as f:
        pages = json.load(f)['pages']

    for d in (OUTPUT_DIR, NL_DIR, EASY_DIR, QR_DIR, ADMIN_DIR, EDITOR_DIR, LIVE_QR_DIR):
        d.mkdir(parents=True, exist_ok=True)

    counts = {'nl': 0, 'easy': 0, 'qr': 0}
    pages_with_status = []

    for i, page in enumerate(pages):
        prev_page = pages[i - 1] if i > 0 else None
        next_page = pages[i + 1] if i < len(pages) - 1 else None

        has_pdf   = (PDFS_DIR  / f"{page['num']}.pdf").exists()
        has_easy  = (PDFS_DIR  / f"E_{page['num']}.pdf").exists()
        has_audio = (AUDIO_DIR / f"{page['num']}.mp3").exists()

        pages_with_status.append({**page, 'has_pdf': has_pdf, 'has_easy': has_easy, 'has_audio': has_audio})

        generate_nl(page, prev_page, next_page, has_easy, has_audio)
        counts['nl'] += 1

        if has_easy:
            generate_easy(page, prev_page, next_page, has_audio)
            counts['easy'] += 1

        generate_qr(page, has_easy)
        generate_live_qr(page, has_easy)
        counts['qr'] += 1

    seed_draft()
    generate_index(pages)
    generate_index_evolution(pages)
    generate_index_draft(pages)
    generate_editor_hub()
    generate_markdown_ref()
    generate_admin(pages_with_status)

    missing_pdfs = [p for p in pages_with_status if not p['has_pdf']]
    if missing_pdfs:
        print(f"  ⚠  {len(missing_pdfs)} page(s) missing main PDF:")
        for p in missing_pdfs:
            print(f"     {p['num']} – {p['title']}")

    mode = 'PRODUCTION' if PROD_MODE else 'STAGING'
    print(f"==============")
    print(f"generate.py in [{mode}] mode:")
    print(f"++++++++++++++")
    print(f"Generated products as follows:")
    print(f"  {OUTPUT_DIR}/index.html")
    print(f"  {OUTPUT_DIR}/index_evolution.html")
    print(f"  {EDITOR_DIR}/index.html  (editor hub)")
    print(f"  {EDITOR_DIR}/index_draft.html  (from content_draft/)")
    print(f"  {EDITOR_DIR}/markdown.html  (markdown reference)")
    print(f"  {NL_DIR}/   ×{counts['nl']} NL pages")
    if counts['easy']:
        print(f"  {EASY_DIR}/   ×{counts['easy']} Easy Read pages")
    print(f"  {QR_DIR}/   ×{counts['qr']} QR redirects (staging/prod)")
    print(f"  {LIVE_QR_DIR}/   ×{counts['qr']} live QR redirects → {'prod' if PROD_MODE else 'staging'} paths")
    print(f"  {ADMIN_DIR}/index.html  +  pages-edit.html")
    print(f"==============")


if __name__ == '__main__':
    main()
