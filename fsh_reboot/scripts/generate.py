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
DEV_PDFS_DIR = REPO_ROOT / 'docs' / 'dev' / 'pdfs'  # source for sync_prod_pdfs()
STORIES_DIR  = SCRIPT_DIR.parent / 'content' / 'stories'  # markdown source for story-type pages
ADMIN_DIR  = OUTPUT_DIR / 'admin'
EDITOR_DIR = OUTPUT_DIR / 'editor'

# In prod mode, replaced index pages are archived here (outside docs/, so never published).
ARCHIVE_DIR = REPO_ROOT / 'archived_index_pages'

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
    result = result.replace('<!-- SRC_MAP_JS -->', src_map_js())
    for key, value in replacements.items():
        result = result.replace(f'<!-- {key} -->', str(value))
    return result

# ── PDF filenames ────────────────────────────────────────────────────────────
def pdf_filename(page):
    """Supplied PDF filename for a page, falling back to the old <num>.pdf scheme."""
    return page.get('pdf', f"{page['num']}.pdf")

def js_escape(text):
    """Escape a string for safe substitution inside a single-quoted JS literal."""
    return text.replace('\\', '\\\\').replace("'", "\\'")

# ── QR source codes ──────────────────────────────────────────────────────────
# Two-letter codes for the 's' query param on QR and page URLs — kept short to
# fit the fixed QR size budget — expanded to readable labels before they reach
# any GA4 event, so reports show "Wall"/"Leaflet" rather than raw codes.
SRC_LABELS = {
    'wl': 'Wall',       # physical Heritage Wall, Bouverie Street
    'lf': 'Leaflet',
    'po': 'Poster',
    'wb': 'Web',        # external link to the site
    'in': 'Internal',   # link from within the site itself
    'bk': 'Book',
}

def src_map_js():
    """JS snippet: SRC_LABELS lookup + expandSrc() helper. Any unrecognised
    code passes through as-is, so a typo stays visible in GA instead of
    vanishing silently."""
    labels = json.dumps(SRC_LABELS, separators=(',', ':'))
    return (f"const SRC_LABELS = {labels};\n"
            f"    function expandSrc(code) {{ return code ? (SRC_LABELS[code] || code) : ''; }}")

def easy_pdf_filename(page):
    """Easy Read PDF filename: E_ + the main PDF filename (override with an
    explicit 'easy_pdf' field in pages.json if a page ever needs one)."""
    return page.get('easy_pdf', f"E_{pdf_filename(page)}")

# ── Nav URLs ─────────────────────────────────────────────────────────────────
# Where wrapper pages point "Home", relative to the nl/ and easy/ directories.
# When the new homepage goes live at the site root this is the one place to change.
WRAPPER_HOME_URL = '../index.html'

def nl_url(page):
    """Relative URL to a page's NL wrapper, from within the nl/ directory."""
    return f"{page['slug']}.html" if page else WRAPPER_HOME_URL

def nl_url_from_outside(page):
    """Relative URL to a page's NL wrapper, from outside the nl/ directory (e.g. easy/, qr/)."""
    return f"../nl/{page['slug']}.html" if page else WRAPPER_HOME_URL

# ── Page generators ─────────────────────────────────────────────────────────
def generate_nl(page, prev_page, next_page, has_easy, has_audio):
    html = sub(load_template('wrapper.html'), {
        'PAGE_TITLE':       page['title'],
        'PAGE_TITLE_JS':    js_escape(page['title']),
        'PAGE_DESCRIPTION': page['title'],
        'PAGE_ID':          page['slug'],
        'PAGE_NUM':         page['num'],
        'PDF_FILE':         f"../pdfs/{pdf_filename(page)}",
        'AUDIO_FILE':       f"../audio/{page['num']}.mp3",
        'EASY_URL':         f"../easy/{page['slug']}.html",
        'NL_URL':           f"{page['slug']}.html",
        'HAS_AUDIO':        'true' if has_audio else 'false',
        'HAS_EASY':         'true' if has_easy else 'false',
        'PREV_URL':         nl_url(prev_page),
        'NEXT_URL':         nl_url(next_page),
        'HOME_URL':         WRAPPER_HOME_URL,
    })
    (NL_DIR / f"{page['slug']}.html").write_text(html, encoding='utf-8')


def generate_story_nl(page, prev_page, next_page, has_audio):
    """Story-type pages (prose content, no PDF) — content_html is rendered at
    build time from fsh_reboot/content/stories/<num>.md via the shared
    markdown parser, same subset used for the homepage content blocks."""
    import content
    md = (STORIES_DIR / f"{page['num']}.md").read_text(encoding='utf-8')
    story_html = content.md_to_html(md)
    html = sub(load_template('wrapper-story.html'), {
        'PAGE_TITLE':       page['title'],
        'PAGE_DESCRIPTION': page['title'],
        'PAGE_ID':          page['slug'],
        'PAGE_NUM':         page['num'],
        'AUDIO_FILE':       f"../audio/{page['num']}.mp3",
        'HAS_AUDIO':        'true' if has_audio else 'false',
        'PREV_URL':         nl_url(prev_page),
        'NEXT_URL':         nl_url(next_page),
        'HOME_URL':         WRAPPER_HOME_URL,
        'STORY_HTML':       story_html,
    })
    (NL_DIR / f"{page['slug']}.html").write_text(html, encoding='utf-8')


def generate_easy(page, prev_page, next_page, has_audio):
    html = sub(load_template('wrapper-easy.html'), {
        'PAGE_TITLE':       page['title'],
        'PAGE_TITLE_JS':    js_escape(page['title']),
        'PAGE_DESCRIPTION': page['title'],
        'PAGE_ID':          page['slug'],
        'PAGE_NUM':         page['num'],
        'EASY_PDF_FILE':    f"../pdfs/{easy_pdf_filename(page)}",
        'AUDIO_FILE':       f"../audio/{page['num']}.mp3",
        'NL_URL':           f"../nl/{page['slug']}.html",
        'HAS_AUDIO':        'true' if has_audio else 'false',
        # prev/next route back through NL; NL redirect logic respects easy pref
        'PREV_URL':         nl_url_from_outside(prev_page),
        'NEXT_URL':         nl_url_from_outside(next_page),
        'HOME_URL':         WRAPPER_HOME_URL,
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
PART_LABELS = {
    1: 'Part 1 – People, Places, Monuments & History',
    2: 'Part 2 – Biographies of Past Newspapers',
    3: 'Part 3 – Biographies of Current Newspapers',
    4: 'Part 4 – Personal Stories',
}

# Parts whose page titles run long (e.g. "Name – Role") get a wider, 2-column
# grid instead of the default 3, so titles don't wrap awkwardly.
WIDE_PARTS = {4}

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
        grid_class = 'page-grid page-grid-wide' if v in WIDE_PARTS else 'page-grid'
        sections.append(
            f'      <section class="volume" aria-labelledby="vol-{v}-heading">\n'
            f'        <h2 class="volume-heading" id="vol-{v}-heading">{PART_LABELS[v]}</h2>\n'
            f'        <ul class="{grid_class}">\n'
            f'{items}'
            f'        </ul>\n'
            f'      </section>\n'
        )
    return '\n'.join(sections)


def archive_existing_index():
    """In prod mode, keep a dated copy of the homepage we are about to replace.
    Skips the copy if the current page is identical to the newest archive."""
    target = OUTPUT_DIR / 'index.html'
    if not PROD_MODE or not target.exists():
        return
    ARCHIVE_DIR.mkdir(exist_ok=True)
    existing = sorted(ARCHIVE_DIR.glob('index_*.html'))
    if existing and existing[-1].read_bytes() == target.read_bytes():
        return
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    dest = ARCHIVE_DIR / f'index_{stamp}.html'
    shutil.copy2(target, dest)
    print(f"  archived replaced index → {dest.relative_to(REPO_ROOT)}")


def sync_prod_pdfs():
    """In prod mode, mirror docs/dev/pdfs/ into the prod PDFS_DIR so PDFs for
    new or reworked pages are never missed at deploy time. Re-copies every
    file unconditionally (cheap, and simpler than tracking what changed) —
    git only picks up files whose content actually differs, since it diffs
    by hash, not by mtime."""
    if not PROD_MODE:
        return
    PDFS_DIR.mkdir(parents=True, exist_ok=True)
    src_names = {f.name for f in DEV_PDFS_DIR.glob('*.pdf')}
    for name in src_names:
        shutil.copy2(DEV_PDFS_DIR / name, PDFS_DIR / name)
    removed = 0
    for f in PDFS_DIR.glob('*.pdf'):
        if f.name not in src_names:
            f.unlink()
            removed += 1
    try:
        pdfs_label = PDFS_DIR.relative_to(REPO_ROOT)
    except ValueError:
        pdfs_label = PDFS_DIR
    msg = f"  synced {pdfs_label}/ from docs/dev/pdfs/ ({len(src_names)} files"
    print(msg + (f", removed {removed} stale)" if removed else ")"))


def generate_index(pages):
    """Generate the homepage from published content/ blocks."""
    archive_existing_index()
    import content
    blocks = content.get_blocks()
    html = (load_template('index.html')
            .replace('<!-- HOME_URL -->',        'index.html')
            .replace('<!-- GA_ID -->',           GA_ID)
            .replace('<!-- SRC_MAP_JS -->',      src_map_js())
            .replace('<!-- HERO_BLOCK -->',      blocks['hero_block'])
            .replace('<!-- BANNER_BLOCK -->',    blocks['banner_block'])
            .replace('<!-- COL_1 -->',           blocks['col1'])
            .replace('<!-- COL_2 -->',           blocks['col2'])
            .replace('<!-- COL_3 -->',           blocks['col3'])
            .replace('<!-- VOLUME_SECTIONS -->', build_volume_sections(pages)))
    (OUTPUT_DIR / 'index.html').write_text(html, encoding='utf-8')


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
    html = (load_template('index.html')
            .replace('<!-- HOME_URL -->',        'index_draft.html')
            .replace('<!-- GA_ID -->',           GA_ID)
            .replace('<!-- SRC_MAP_JS -->',      src_map_js())
            .replace('<!-- HERO_BLOCK -->',      blocks['hero_block'])
            .replace('<!-- BANNER_BLOCK -->',    blocks['banner_block'])
            .replace('<!-- COL_1 -->',           blocks['col1'])
            .replace('<!-- COL_2 -->',           blocks['col2'])
            .replace('<!-- COL_3 -->',           blocks['col3'])
            .replace('<!-- VOLUME_SECTIONS -->', build_volume_sections(pages)))
    # index_draft lives one level deeper (editor/) so rewrite relative paths
    html = html.replace('src="images/', 'src="../images/')
    html = html.replace('href="nl/', 'href="../nl/')
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


# ── Non-page QR redirects ───────────────────────────────────────────────────
# Stable QR URLs for destinations that aren't wrapper pages. Print materials
# can commit to these URLs now; where they land is a regeneration decision.
def generate_special_qrs():
    specials = [
        # (filename stem, page_id for analytics, staging target, live target)
        # live home QR points at the public homepage (docs/index.html) in both
        # modes — unlike page QRs, its destination already exists in production.
        ('home', 'home', '../index.html', '../index.html'),
    ]
    for stem, page_id, staging_target, live_target in specials:
        for out_dir, target in ((QR_DIR, staging_target), (LIVE_QR_DIR, live_target)):
            html = sub(load_template('qr-redirect.html'), {
                'PAGE_ID':  page_id,
                'PAGE_NUM': page_id,
                'NL_URL':   target,
                'EASY_URL': '',
            })
            (out_dir / f'{stem}.html').write_text(html, encoding='utf-8')


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

    pages_html = render('pages.html')
    (ADMIN_DIR / 'pages.html').write_text(pages_html, encoding='utf-8')

    # Editor copy: fix meta links for editor/ context
    editor_pages_html = (pages_html
        .replace('<a href="index.html">← Admin home</a>', '<a href="index.html">← Editor home</a>')
        .replace('&nbsp;·&nbsp; <a href="pages-edit.html">Edit pages →</a>', '')
        .replace('&nbsp;·&nbsp; <a href="../editor/">Editor hub →</a>', ''))
    (EDITOR_DIR / 'pages.html').write_text(editor_pages_html, encoding='utf-8')
    (ADMIN_DIR / 'pages-edit.html').write_text(render('pages-edit.html'), encoding='utf-8')


def generate_admin_hub():
    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    html = (load_template('admin-hub.html')
            .replace('<!-- GA_ID -->',        GA_ID)
            .replace('<!-- GENERATED_AT -->', generated_at))
    (ADMIN_DIR / 'index.html').write_text(html, encoding='utf-8')


# ── Data validation ─────────────────────────────────────────────────────────
import re as _re

def validate_pages(pages):
    """Return {index: [problems]} for pages whose data would break a
    substitution context. Titles may contain apostrophes (escaped where
    needed); anything else needs a manual rename in pages.json. Invalid
    pages are skipped by generation and flagged red in the admin sanity
    panel until fixed — the rest of the site still generates and deploys."""
    issues = {}
    seen = {'num': set(), 'slug': set(), 'pdf': set()}
    def add(i, msg):
        issues.setdefault(i, []).append(msg)
    for i, p in enumerate(pages):
        if not _re.fullmatch(r'\d+', str(p.get('num', ''))):
            add(i, "num must be digits only")
        if not _re.fullmatch(r'[a-z0-9-]+', p.get('slug', '')):
            add(i, "slug must be lowercase letters, digits and hyphens only")
        for field in ('pdf', 'easy_pdf'):
            if field in p and not _re.fullmatch(r'[A-Za-z0-9_&.-]+\.pdf', p[field]):
                add(i, f"{field} filename has unsafe characters ({p[field]})")
        title = p.get('title', '')
        for ch, why in [('"', 'breaks HTML attributes'), ('<', 'breaks HTML'),
                        ('>', 'breaks HTML'), ('\\', 'breaks JS strings')]:
            if ch in title:
                add(i, f"title contains {ch!r} ({why}) — please rephrase")
        for field in ('num', 'slug', 'pdf'):
            v = p.get(field)
            if v is None:
                continue  # absent (e.g. pdf on a story-type page) is not a duplicate
            if v in seen[field]:
                add(i, f"duplicate {field} '{v}'")
            seen[field].add(v)
    return issues


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    with open(DATA_FILE, encoding='utf-8') as f:
        pages = json.load(f)['pages']
    data_issues = validate_pages(pages)
    valid_pages = [p for i, p in enumerate(pages) if i not in data_issues]

    for d in (OUTPUT_DIR, NL_DIR, EASY_DIR, QR_DIR, ADMIN_DIR, EDITOR_DIR, LIVE_QR_DIR):
        d.mkdir(parents=True, exist_ok=True)

    sync_prod_pdfs()

    counts = {'nl': 0, 'easy': 0, 'qr': 0}

    # status for every page (invalid ones flagged for the admin sanity panel)
    pages_with_status = []
    for i, page in enumerate(pages):
        status = {
            **page,
            'has_pdf':   (PDFS_DIR  / pdf_filename(page)).exists(),
            'has_easy':  (PDFS_DIR  / easy_pdf_filename(page)).exists(),
            'has_audio': (AUDIO_DIR / f"{page['num']}.mp3").exists(),
        }
        if i in data_issues:
            status['data_issues'] = data_issues[i]
        pages_with_status.append(status)

    # generation runs over valid pages only; prev/next skip invalid ones
    for i, page in enumerate(valid_pages):
        prev_page = valid_pages[i - 1] if i > 0 else None
        next_page = valid_pages[i + 1] if i < len(valid_pages) - 1 else None

        has_easy  = False if page.get('story') else (PDFS_DIR / easy_pdf_filename(page)).exists()
        has_audio = (AUDIO_DIR / f"{page['num']}.mp3").exists()

        if page.get('story'):
            generate_story_nl(page, prev_page, next_page, has_audio)
        else:
            generate_nl(page, prev_page, next_page, has_easy, has_audio)
        counts['nl'] += 1

        if has_easy:
            generate_easy(page, prev_page, next_page, has_audio)
            counts['easy'] += 1

        generate_qr(page, has_easy)
        generate_live_qr(page, has_easy)
        counts['qr'] += 1

    generate_special_qrs()
    seed_draft()
    generate_index(valid_pages)
    generate_index_draft(valid_pages)
    generate_editor_hub()
    generate_markdown_ref()
    generate_admin(pages_with_status)
    generate_admin_hub()

    if data_issues:
        print(f"  ⚠  {len(data_issues)} page(s) SKIPPED — invalid data, rename needed in pages.json:")
        for i, msgs in sorted(data_issues.items()):
            print(f"     {pages[i].get('num', '?')} – {pages[i].get('title', '?')}: {'; '.join(msgs)}")

    missing_pdfs = [p for p in pages_with_status if not p['has_pdf'] and not p.get('story')]
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
    print(f"  {EDITOR_DIR}/index.html  (editor hub)")
    print(f"  {EDITOR_DIR}/index_draft.html  (from content_draft/)")
    print(f"  {EDITOR_DIR}/markdown.html  (markdown reference)")
    print(f"  {NL_DIR}/   ×{counts['nl']} NL pages")
    if counts['easy']:
        print(f"  {EASY_DIR}/   ×{counts['easy']} Easy Read pages")
    print(f"  {QR_DIR}/   ×{counts['qr']} QR redirects (staging/prod)")
    print(f"  {LIVE_QR_DIR}/   ×{counts['qr']} live QR redirects → {'prod' if PROD_MODE else 'staging'} paths")
    print(f"  {ADMIN_DIR}/index.html  (admin hub)")
    print(f"  {ADMIN_DIR}/pages.html  +  pages-edit.html")
    print(f"  {EDITOR_DIR}/pages.html  (copy)")
    print(f"==============")


if __name__ == '__main__':
    main()
