#!/usr/bin/env python3
"""Auto-generate sitemap.xml from actual guide files + static pages.
Uses git log to get real lastmod dates for each file."""
import os
import glob
import subprocess
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDES_DIR = os.path.join(BASE_DIR, "guides")
SITEMAP_PATH = os.path.join(BASE_DIR, "sitemap.xml")
SITE_URL = "https://iogameguide.com"

def get_git_lastmod(filepath):
    """Get the last git commit date for a file."""
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%ci', '--', filepath],
            capture_output=True, text=True, cwd=BASE_DIR
        )
        if result.returncode == 0 and result.stdout.strip():
            dt = datetime.strptime(result.stdout.strip()[:10], '%Y-%m-%d')
            return dt.strftime('%Y-%m-%d')
    except Exception:
        pass
    return datetime.now().strftime('%Y-%m-%d')

def get_git_lastmod_static(filepath):
    """Get the last git commit date for static pages."""
    return get_git_lastmod(os.path.join(BASE_DIR, filepath) if filepath else '')

# Static pages: (path, changefreq, priority)
STATIC_PAGES = [
    ("", "daily", "1.0"),           # homepage
    ("games.html", "daily", "0.9"),
    ("about.html", "monthly", "0.5"),
    ("privacy-policy.html", "yearly", "0.3"),
    ("terms-of-service.html", "yearly", "0.3"),
    ("cookie-policy.html", "yearly", "0.3"),
]

lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

# Static pages
for path, freq, pri in STATIC_PAGES:
    loc = f"{SITE_URL}/{path}" if path else SITE_URL
    lastmod = get_git_lastmod_static(path) if path else get_git_lastmod('index.html')
    lines.append(f'''  <url>
    <loc>{loc}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{pri}</priority>
  </url>''')

# Guide pages - auto-scan
guide_files = sorted(glob.glob(os.path.join(GUIDES_DIR, "*.html")))
for gf in guide_files:
    name = os.path.basename(gf)
    lastmod = get_git_lastmod(gf)
    lines.append(f'''  <url>
    <loc>{SITE_URL}/guides/{name}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>''')

lines.append('</urlset>')

sitemap = '\n'.join(lines) + '\n'
with open(SITEMAP_PATH, 'w') as f:
    f.write(sitemap)

guide_count = len(guide_files)
total = guide_count + len(STATIC_PAGES)
print(f"✅ Sitemap generated: {total} URLs ({guide_count} guides + {len(STATIC_PAGES)} static)")
