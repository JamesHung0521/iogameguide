#!/usr/bin/env python3
"""Auto-generate sitemap.xml from actual guide files + static pages."""
import os
import glob
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDES_DIR = os.path.join(BASE_DIR, "guides")
SITEMAP_PATH = os.path.join(BASE_DIR, "sitemap.xml")
SITE_URL = "https://iogameguide.com"
TODAY = datetime.now().strftime("%Y-%m-%d")

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
    lines.append(f'''  <url>
    <loc>{loc}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{pri}</priority>
  </url>''')

# Guide pages - auto-scan
guide_files = sorted(glob.glob(os.path.join(GUIDES_DIR, "*.html")))
for gf in guide_files:
    name = os.path.basename(gf)
    lines.append(f'''  <url>
    <loc>{SITE_URL}/guides/{name}</loc>
    <lastmod>{TODAY}</lastmod>
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
