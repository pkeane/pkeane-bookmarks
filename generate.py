#!/usr/bin/env python3
"""
Usage: python3 generate.py <chrome_bookmarks.html>

Parses a Chrome bookmarks export and writes bookmarks.jsonl + bookmarks.html
to the same directory as this script.
"""

import json
import os
import sys
from datetime import datetime
from html.parser import HTMLParser

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# ── Parse bookmarks HTML ──────────────────────────────────────────────────────

class BookmarkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.bookmarks = []
        self.in_h3 = False
        self.h3_text = ''
        self.in_a = False
        self.current_url = None
        self.current_add_date = None
        self.current_text = ''
        self.header_stack = []
        self._pending_header = None
        self.current_header = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'h3':
            self.in_h3 = True
            self.h3_text = ''
        elif tag == 'a':
            self.in_a = True
            self.current_url = attrs.get('href', '')
            self.current_add_date = attrs.get('add_date', '')
            self.current_text = ''
        elif tag == 'dl':
            if self._pending_header:
                self.header_stack.append(self._pending_header)
                self.current_header = self._pending_header
                self._pending_header = None

    def handle_endtag(self, tag):
        if tag == 'h3':
            self.in_h3 = False
            self._pending_header = self.h3_text.strip()
        elif tag == 'a':
            if self.current_url and self.current_url.startswith('http'):
                self.bookmarks.append({
                    'url': self.current_url,
                    'add_date': self.current_add_date,
                    'link_text': self.current_text.strip(),
                    'header_section': self.current_header or '',
                })
            self.in_a = False
        elif tag == 'dl':
            if self.header_stack:
                self.header_stack.pop()
                self.current_header = self.header_stack[-1] if self.header_stack else None

    def handle_data(self, data):
        if self.in_h3:
            self.h3_text += data
        elif self.in_a:
            self.current_text += data


def parse_bookmarks(path):
    parser = BookmarkParser()
    with open(path, 'r', encoding='utf-8') as f:
        parser.feed(f.read())
    return parser.bookmarks


# ── Build HTML ────────────────────────────────────────────────────────────────

def make_anchor(s):
    return s.lower().replace(' ', '-').replace('/', '-').replace("'", '').replace('&', '')


def build_html(bookmarks):
    sections = {}
    for b in bookmarks:
        sec = b['header_section'] or 'Uncategorized'
        if sec not in sections:
            sections[sec] = []
        sections[sec].append(b)

    def sort_key(s):
        if s == 'TOP':
            return '   '  # sorts first
        if s == 'Uncategorized':
            return 'zzz'
        return s.lower()

    sorted_sections = sorted(sections.keys(), key=sort_key)

    # Sidebar nav
    nav_items = []
    for sec in sorted_sections:
        anchor = make_anchor(sec)
        count = len(sections[sec])
        nav_items.append(
            '<a href="#' + anchor + '" class="nav-item">'
            '<span class="nav-label">' + sec + '</span>'
            '<span class="nav-count">' + str(count) + '</span>'
            '</a>'
        )

    # Section content
    section_parts = []
    for sec in sorted_sections:
        anchor = make_anchor(sec)
        items = sections[sec]
        links = []
        for b in items:
            url = b['url'].replace('"', '&quot;')
            text = b['link_text'].replace('<', '&lt;').replace('>', '&gt;') or url
            display = text[:120] + ('…' if len(text) > 120 else '')
            try:
                ts = int(b['add_date'])
                date_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d') if ts > 0 else ''
            except Exception:
                date_str = ''
            date_html = '<span class="bm-date">' + date_str + '</span>' if date_str else ''
            data_text = text[:200].lower().replace('"', '').replace("'", '')
            links.append(
                '<li class="bm-item" data-text="' + data_text + '">'
                '<a href="' + url + '" target="_blank" rel="noopener">' + display + '</a>'
                + date_html + '</li>'
            )
        section_parts.append(
            '<section id="' + anchor + '" class="bm-section">'
            '<h2 class="section-title">' + sec +
            ' <span class="section-count">' + str(len(items)) + '</span></h2>'
            '<ul class="bm-list">' + '\n'.join(links) + '</ul>'
            '</section>'
        )

    total = len(bookmarks)
    num_sections = len(sorted_sections)
    nav_html = '\n'.join(nav_items)
    sections_html = '\n'.join(section_parts)

    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PKEANE BOOKMARKS</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Chango&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,400&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --navy: #14213D;
      --orange: #FCA311;
      --bg: #E8E8E8;
      --white: #FFFFFF;
      --text: #14213D;
      --muted: #6b7280;
    }
    html { scroll-behavior: smooth; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'DM Sans', system-ui, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    header {
      background: var(--navy);
      color: var(--white);
      padding: 0.9rem 1.8rem;
      display: flex;
      align-items: center;
      gap: 1.5rem;
      flex-wrap: wrap;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    header h1 {
      font-family: 'Chango', sans-serif;
      font-weight: 400;
      font-size: clamp(1.5rem, 3.5vw, 2.2rem);
      letter-spacing: 0.12em;
      white-space: nowrap;
      flex-shrink: 0;
    }
    header h1 span { color: var(--orange); }
    .header-meta { color: #94a3b8; font-size: 0.82rem; white-space: nowrap; }
    .search-wrap { flex: 1; min-width: 180px; max-width: 400px; margin-left: auto; }
    #search {
      width: 100%;
      padding: 0.48rem 1rem;
      border-radius: 999px;
      border: 2px solid transparent;
      background: rgba(255,255,255,0.1);
      color: var(--white);
      font-family: inherit;
      font-size: 0.9rem;
      outline: none;
      transition: background 0.2s, border-color 0.2s;
    }
    #search::placeholder { color: #64748b; }
    #search:focus { background: rgba(255,255,255,0.18); border-color: var(--orange); }
    .layout { flex: 1; display: flex; align-items: flex-start; }
    .sidebar {
      width: 210px;
      flex-shrink: 0;
      position: sticky;
      top: 55px;
      height: calc(100vh - 55px);
      overflow-y: auto;
      background: var(--navy);
      padding: 0.8rem 0;
    }
    .sidebar::-webkit-scrollbar { width: 3px; }
    .sidebar::-webkit-scrollbar-track { background: transparent; }
    .sidebar::-webkit-scrollbar-thumb { background: #2d3f5e; border-radius: 2px; }
    .nav-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0.34rem 1rem;
      color: #94a3b8;
      text-decoration: none;
      font-size: 0.8rem;
      font-weight: 500;
      gap: 0.4rem;
      border-left: 3px solid transparent;
      transition: color 0.12s, border-color 0.12s, background 0.12s;
    }
    .nav-item:hover { color: var(--white); border-left-color: var(--orange); background: rgba(255,255,255,0.05); }
    .nav-item.active { color: var(--orange); border-left-color: var(--orange); background: rgba(252,163,17,0.08); }
    .nav-label { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .nav-count {
      background: rgba(255,255,255,0.08);
      color: #64748b;
      font-size: 0.7rem;
      padding: 0.08rem 0.38rem;
      border-radius: 999px;
      flex-shrink: 0;
    }
    main { flex: 1; min-width: 0; padding: 1.8rem 2.2rem; }
    .bm-section { margin-bottom: 2.2rem; scroll-margin-top: 80px; }
    .bm-section.hidden { display: none; }
    .section-title {
      font-family: 'Chango', sans-serif;
      font-weight: 400;
      font-size: 1.15rem;
      letter-spacing: 0.06em;
      color: var(--navy);
      border-bottom: 3px solid var(--orange);
      padding-bottom: 0.3rem;
      margin-bottom: 0.6rem;
      display: flex;
      align-items: baseline;
      gap: 0.5rem;
    }
    .section-count {
      font-family: 'DM Sans', sans-serif;
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--navy);
      background: var(--orange);
      padding: 0.08rem 0.42rem;
      border-radius: 999px;
      letter-spacing: 0;
    }
    .bm-list { list-style: none; }
    .bm-item {
      display: flex;
      align-items: baseline;
      gap: 0.7rem;
      padding: 0.38rem 0.5rem;
      border-radius: 5px;
      transition: background 0.1s;
    }
    .bm-item:hover { background: var(--white); }
    .bm-item.hidden { display: none; }
    .bm-item a {
      color: #1e3a5f;
      text-decoration: none;
      font-size: 0.88rem;
      flex: 1;
      min-width: 0;
      word-break: break-word;
      line-height: 1.4;
    }
    .bm-item a:hover { color: #1a56db; text-decoration: underline; }
    .bm-date { font-size: 0.7rem; color: var(--muted); white-space: nowrap; flex-shrink: 0; }
    #no-results { display: none; text-align: center; padding: 4rem 2rem; color: var(--muted); font-size: 1rem; }
    @media (max-width: 680px) {
      .sidebar { display: none; }
      main { padding: 1rem 0.9rem; }
      .header-meta { display: none; }
    }
  </style>
</head>
<body>

<header>
  <h1>PKEANE <span>BOOKMARKS</span></h1>
  <span class="header-meta">""" + f"{total:,}" + """ links &middot; """ + str(num_sections) + """ sections</span>
  <div class="search-wrap">
    <input type="search" id="search" placeholder="Search bookmarks&#x2026;" autocomplete="off" spellcheck="false">
  </div>
</header>

<div class="layout">
  <nav class="sidebar">
""" + nav_html + """
  </nav>
  <main>
""" + sections_html + """
    <div id="no-results">No bookmarks match your search.</div>
  </main>
</div>

<script>
(function() {
  var searchInput = document.getElementById('search');
  var noResults = document.getElementById('no-results');
  var sections = document.querySelectorAll('.bm-section');
  var navLinks = document.querySelectorAll('.nav-item');

  searchInput.addEventListener('input', function() {
    var q = this.value.trim().toLowerCase();
    var anyVisible = false;
    sections.forEach(function(sec) {
      var items = sec.querySelectorAll('.bm-item');
      var secTitleEl = sec.querySelector('.section-title');
      var secText = secTitleEl ? secTitleEl.textContent.toLowerCase() : '';
      var secVisible = 0;
      items.forEach(function(item) {
        var match = !q || (item.getAttribute('data-text') || '').includes(q) || secText.includes(q);
        item.classList.toggle('hidden', !match);
        if (match) secVisible++;
      });
      var show = !q || secVisible > 0;
      sec.classList.toggle('hidden', !show);
      if (show) anyVisible = true;
    });
    noResults.style.display = anyVisible ? 'none' : 'block';
  });

  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        var id = entry.target.id;
        navLinks.forEach(function(n) {
          n.classList.toggle('active', n.getAttribute('href') === '#' + id);
        });
      }
    });
  }, { rootMargin: '-15% 0px -75% 0px' });

  sections.forEach(function(sec) { observer.observe(sec); });
})();
</script>

</body>
</html>"""


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) != 2:
        print('Usage: python3 generate.py <chrome_bookmarks.html>')
        sys.exit(1)

    input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print(f'Error: file not found: {input_path}')
        sys.exit(1)

    print(f'Parsing {input_path} ...')
    bookmarks = parse_bookmarks(input_path)
    print(f'Found {len(bookmarks):,} bookmarks')

    jsonl_path = os.path.join(SCRIPT_DIR, 'bookmarks.jsonl')
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for b in bookmarks:
            f.write(json.dumps(b) + '\n')
    print(f'Wrote {jsonl_path}')

    html_path = os.path.join(SCRIPT_DIR, 'index.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(build_html(bookmarks))
    print(f'Wrote {html_path}')



if __name__ == '__main__':
    main()
