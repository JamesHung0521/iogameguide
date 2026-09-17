#!/usr/bin/env python3
"""
Daily .io Game Guide Generator (Hybrid Mode)
- Fetches existing games from GitHub main.js
- Searches for new popular .io games
- Generates complete guide HTML + screenshots
- Uploads to GitHub via REST API (Contents API) — no git clone/push
- Returns result for main agent to generate Pinterest images
- Reports MISSING_IMAGES if not enough real screenshots found
"""

import asyncio
import sys
import re
import json
import os
import socket
import subprocess
import shutil
import time
import base64
import hashlib
import requests
from io import BytesIO
from urllib.parse import urlparse
from datetime import datetime
from codeact_sdk import CodeActSDK
from pydantic import BaseModel
from typing import List

# === Tool schema versions (from get_codeact_tool_schemas) ===
SEARCH_VER = "v1_5ac1b0eba8c26f2a"
FETCH_VER = "v1_2c8d0580b3f93a58"

# === Constants ===
GITHUB_RAW_MAINJS = "https://raw.githubusercontent.com/JamesHung0521/iogameguide/main/js/main.js"
GITHUB_REPO = "https://github.com/JamesHung0521/iogameguide.git"
SITE_BASE = "https://iogameguide.com"
REPO_DIR = "/tmp/iogameguide_daily"
IMAGE_STRATEGY = "hybrid"  # "website" = 从官网HTML提取截图; "search" = 多关键词网络搜索; "hybrid" = 先website后search自动回退
DEAD_GAMES_FILE = "./codeact/output/dead_games.json"  # 死站记录文件


# ============================================================
# Retry wrappers for requests — handle cold-start network timeouts
# ============================================================
def retry_get(url, **kwargs):
    """requests.get with automatic retry (max 3 attempts, 5s interval)."""
    max_retries = 3
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, **kwargs)
            return resp
        except Exception as e:
            last_exc = e
            if attempt < max_retries:
                print(f"[重试] 第{attempt}/{max_retries}次失败，5秒后重试...")
                time.sleep(5)
            else:
                print(f"[重试] 第{attempt}/{max_retries}次失败，已达最大重试次数")
    raise last_exc


def retry_post(url, **kwargs):
    """requests.post with automatic retry (max 3 attempts, 5s interval)."""
    max_retries = 3
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(url, **kwargs)
            return resp
        except Exception as e:
            last_exc = e
            if attempt < max_retries:
                print(f"[重试] 第{attempt}/{max_retries}次失败，5秒后重试...")
                time.sleep(5)
            else:
                print(f"[重试] 第{attempt}/{max_retries}次失败，已达最大重试次数")
    raise last_exc


# ============================================================
# GitHub Contents API helpers (replace git clone/push)
# ============================================================
GITHUB_API_BASE = "https://api.github.com/repos/JamesHung0521/iogameguide/contents"


def retry_put(url, **kwargs):
    """requests.put with automatic retry (max 3 attempts, 5s interval)."""
    max_retries = 3
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.put(url, **kwargs)
            return resp
        except Exception as e:
            last_exc = e
            if attempt < max_retries:
                print(f"[PUT重试] 第{attempt}/{max_retries}次失败，5秒后重试...")
                time.sleep(5)
            else:
                print(f"[PUT重试] 第{attempt}/{max_retries}次失败，已达最大重试次数")
    raise last_exc


def github_file_get(path, token, ref="main"):
    """
    Get file content from GitHub via Contents API.
    Returns (content_str: str, sha: str) on success; (None, None) if 404.
    For text files only. For binary files use github_file_get_bytes.
    """
    url = f"{GITHUB_API_BASE}/{path}?ref={ref}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    resp = retry_get(url, headers=headers, timeout=30)
    if resp.status_code == 404:
        return None, None
    if resp.status_code != 200:
        raise Exception(f"GitHub GET {path} failed: HTTP {resp.status_code} {resp.text[:200]}")
    data = resp.json()
    sha = data.get("sha", "")
    encoding = data.get("encoding", "")
    if encoding == "base64":
        file_content = base64.b64decode(data["content"])
        try:
            text = file_content.decode("utf-8")
            return text, sha
        except UnicodeDecodeError:
            return file_content, sha
    else:
        return data.get("content", ""), sha


def github_file_get_bytes(path, token, ref="main"):
    """
    Get binary file content from GitHub via Contents API.
    Returns (content_bytes: bytes, sha: str) on success, (None, None) if 404.
    """
    url = f"{GITHUB_API_BASE}/{path}?ref={ref}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    resp = retry_get(url, headers=headers, timeout=30)
    if resp.status_code == 404:
        return None, None
    if resp.status_code != 200:
        raise Exception(f"GitHub GET bytes {path} failed: HTTP {resp.status_code} {resp.text[:200]}")
    data = resp.json()
    sha = data.get("sha", "")
    content_bytes = base64.b64decode(data["content"])
    return content_bytes, sha


def github_file_put(path, token, content, sha=None, message="Update file via API"):
    """
    Put (create or update) a file via GitHub Contents API.
    content can be str (text files) or bytes (binary files).
    sha is required for updates (existing files), None for new files.
    Returns full response dict on success.
    """
    url = f"{GITHUB_API_BASE}/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    if isinstance(content, str):
        content_bytes = content.encode("utf-8")
    else:
        content_bytes = content
    encoded = base64.b64encode(content_bytes).decode("ascii")
    body = {
        "message": message,
        "content": encoded,
        "branch": "main"
    }
    if sha:
        body["sha"] = sha
    resp = retry_put(url, headers=headers, json=body, timeout=60)
    if resp.status_code not in (200, 201):
        raise Exception(f"GitHub PUT {path} failed: HTTP {resp.status_code} {resp.text[:300]}")
    return resp.json()


# ============================================================
# Pydantic Models for LLM structured output
# ============================================================
class GameCandidate(BaseModel):
    name: str
    slug: str
    icon: str
    icon_color: str
    difficulty: int
    tags: List[str]
    description: str
    game_url: str


class GameSelection(BaseModel):
    candidates: List[GameCandidate]


class GuideContent(BaseModel):
    introduction: str
    getting_started: str
    basic_tips: str
    advanced_strategies: str
    pro_tips: str
    conclusion: str


# ============================================================
# HTML Template — uses __PLACEHOLDER__ format to avoid { } conflicts
# ============================================================
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>__GAME_NAME__ Complete Guide 2026 | iogameguide</title>
    <meta name="description" content="__GAME_NAME__ complete guide: tips, tricks, strategies and advanced techniques.">
    <meta name="keywords" content="__GAME_SLUG__ guide, __GAME_SLUG__ tips, __GAME_SLUG__ strategy, __GAME_SLUG__ browser game">
    <meta name="author" content="iogameguide Editorial Team - Alex Rivera">
    <meta name="robots" content="index, follow">
    <meta property="og:type" content="article">
    <meta property="og:title" content="__GAME_NAME__ Complete Guide: Tips, Tricks & Strategies">
    <meta property="og:description" content="Master __GAME_NAME__ with our complete guide covering gameplay mechanics, advanced strategies, and pro tips.">
    <meta property="og:url" content="https://iogameguide.com/guides/__GAME_SLUG__-guide">
    <meta property="article:published_time" content="__DATE__">
    <meta property="article:modified_time" content="__DATE__">
    <link rel="canonical" href="https://iogameguide.com/guides/__GAME_SLUG__-guide">
    <link rel="stylesheet" href="../css/style.css">
    <meta name="monetag" content="6edeea88afeae1aabde93ea959fedbfd">
    <script src="/js/ad-config.js"></script>
    <script>
    if (window.AD_CONFIG && window.AD_CONFIG.monetag) {
        (function(s){s.src='https://5gvci.com/act/files/tag.min.js?z=11429977';s.async=true;s.setAttribute('data-cfasync','false')})([document.documentElement, document.body].filter(Boolean).pop().appendChild(document.createElement('script')));
        (function(s){s.dataset.zone='11430095',s.src='https://n6wxm.com/vignette.min.js'})([document.documentElement, document.body].filter(Boolean).pop().appendChild(document.createElement('script')));
        (function(s){s.dataset.zone='11430119',s.src='https://nap5k.com/tag.min.js'})([document.documentElement, document.body].filter(Boolean).pop().appendChild(document.createElement('script')));
    }
    if (window.AD_CONFIG && window.AD_CONFIG.adsense) {
        (function(s){s.async=true;s.src='https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1074835585646908';s.crossOrigin='anonymous'})(document.head.appendChild(document.createElement('script')));
    }
    </script>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@context": "https://schema.org",
                "@type": "VideoGame",
                "name": "__GAME_NAME__",
                "description": "Master __GAME_NAME__ with our complete guide.",
                "url": "https://iogameguide.com/guides/__GAME_SLUG__-guide",
                "author": {"@type": "Organization", "name": "iogameguide Editorial Team - Alex Rivera"},
                "publisher": {"@type": "Organization", "name": "iogameguide.com"},
                "datePublished": "__DATE__",
                "gamePlatform": ["Web Browser"],
                "genre": "__GAME_GENRE__",
                "applicationCategory": "Game"
            },
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": "__GAME_NAME__ Complete Guide",
                "author": {"@type": "Organization", "name": "iogameguide Editorial Team - Alex Rivera"},
                "datePublished": "__DATE__",
                "image": "https://iogameguide.com/images/games/__GAME_SLUG__/hero.jpg"
            }
        ]
    }
    </script>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-3SFHCK9FDP"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-3SFHCK9FDP');
</script>
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="../index" class="logo">
                <svg class="logo-icon" viewBox="0 0 36 36" fill="none">
                    <defs><linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#00ff88"/><stop offset="100%" style="stop-color:#00d4ff"/></linearGradient></defs>
                    <circle cx="18" cy="18" r="16" stroke="url(#grad1)" stroke-width="2" fill="none"/>
                    <path d="M12 18 L18 12 L24 18 L18 24 Z" fill="url(#grad1)"/>
                </svg>
                <span>iogameguide</span>
            </a>
            <div class="hamburger">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <ul class="nav-links">
                <li><a href="../index">Home</a></li>
                <li><a href="../games">All Games</a></li>
                <li><a href="../about">About</a></li>
            </ul>
        </div>
    </nav>

    <main class="guide-page">
        <div class="container">
            <header class="guide-header">
                <span class="game-badge">__GAME_ICON__ __GAME_NAME__</span>
                <h1>__GAME_NAME__ Complete Guide</h1>
                <p class="guide-meta"><span>By iogameguide Editorial Team - Alex Rivera</span><span>&#8226;</span><span>Updated: __DATE__</span><span>•</span><span>__READING_TIME__ min read</span></p>
                <a href="__GAME_URL__" target="_blank" rel="noopener noreferrer" class="play-now-btn" style="display:inline-block; padding:12px 28px; background:linear-gradient(135deg, #6366f1, #8b5cf6); color:#fff; text-decoration:none; border-radius:50px; font-size:1.1rem; font-weight:700; margin:16px 0 24px 0; transition:all 0.3s ease; box-shadow:0 4px 15px rgba(99,102,241,0.3);">🎮 Play __GAME_NAME__ Now</a>
            </header>
            <div class="game-hero">
                <img src="../images/games/__GAME_SLUG__/hero.jpg" alt="__GAME_NAME__ gameplay" loading="lazy">
            </div>
            <article class="article-content">
                <h2 id="introduction">Introduction</h2>
                <p>__INTRODUCTION__</p>
                <h2 id="getting-started">Getting Started</h2>
                <figure class="game-screenshot">
                    <img src="../images/games/__GAME_SLUG__/screenshot-1.jpg" alt="__GAME_NAME__" loading="lazy">
                    <figcaption>Game interface</figcaption>
                </figure>
                <p>__GETTING_STARTED__</p>
                <h2 id="basic-tips">Basic Tips</h2>
                <p>__BASIC_TIPS__</p>
                <h2 id="advanced-strategies">Advanced Strategies</h2>
                <figure class="game-screenshot">
                    <img src="../images/games/__GAME_SLUG__/screenshot-2.jpg" alt="__GAME_NAME__" loading="lazy">
                    <figcaption>Advanced tactics</figcaption>
                </figure>
                <p>__ADVANCED_STRATEGIES__</p>
                <h2 id="pro-tips">Pro Tips</h2>
                <figure class="game-screenshot">
                    <img src="../images/games/__GAME_SLUG__/screenshot-3.jpg" alt="__GAME_NAME__" loading="lazy">
                    <figcaption>Pro techniques</figcaption>
                </figure>
                <p>__PRO_TIPS__</p>
                <h2 id="conclusion">Conclusion</h2>
                <p>__CONCLUSION__</p>
            </article>
__RELATED_GUIDES__
        </div>
    </main>

    <footer class="footer">
        <div class="footer-content">
            <div class="footer-section"><h4>iogameguide</h4><p>Your ultimate .io game guide</p></div>
            <div class="footer-section"><h4>Links</h4><ul><li><a href="../index">Home</a></li><li><a href="../games">All Games</a></li><li><a href="../about">About</a></li></ul></div>
            <div class="footer-section"><h4>Legal</h4><ul><li><a href="../privacy-policy">Privacy</a></li><li><a href="../terms-of-service">Terms</a></li></ul></div>
        </div>
        <div class="footer-bottom"><p>&copy; 2026 iogameguide</p></div>
    </footer>
    <script src="../js/main.js?v=__TIMESTAMP__"></script>
</body>
</html>"""


# ============================================================
# Helper functions
# ============================================================
def fill_template(template: str, **kwargs) -> str:
    """Replace __KEY__ placeholders with values. Any unreplaced __*__ placeholders are stripped to prevent literal text."""
    result = template
    for key, value in kwargs.items():
        result = result.replace(f"__{key}__", str(value))
    # Safety: strip any remaining unreplaced __*__ placeholders (e.g. __RELATED_GUIDES__)
    result = re.sub(r'__[A-Z_]+__', '', result)
    return result


def generate_related_guides_html(game_slug, game_tags, main_js_content):
    """
    Generate Related Guides HTML section by finding similar games from gamesData.
    Uses tag matching to find related games, falls back to popular games.
    """
    # Parse gamesData from main.js
    games_match = re.search(r'const gamesData\s*=\s*\[([\s\S]*?)\n\];', main_js_content)
    if not games_match:
        return ""

    games_block = games_match.group(1)

    # Parse each game entry
    all_games = []
    entries = re.split(r'\n\s*\},\s*\{', games_block)
    for i, entry in enumerate(entries):
        if i == 0:
            entry = entry.lstrip('[').strip()
            if not entry.startswith('{'):
                entry = '{' + entry
        else:
            entry = '{' + entry
        if not entry.rstrip().endswith('}'):
            entry = entry + '}'

        gid_match = re.search(r"id:\s*['\"]([^'\"]+)['\"]", entry)
        if not gid_match:
            continue
        gid = gid_match.group(1)

        name_match = re.search(r"name:\s*['\"]([^'\"]+)['\"]", entry)
        icon_match = re.search(r"icon:\s*['\"]([^'\"]*)['\"]", entry)
        color_match = re.search(r"iconColor:\s*['\"]([^'\"]*)['\"]", entry)
        tags_match = re.search(r"tags:\s*\[([^\]]*)\]", entry)

        name = name_match.group(1) if name_match else gid
        icon = icon_match.group(1) if icon_match else "\U0001f3ae"
        color = color_match.group(1) if color_match else "#6366f1"
        tags_str = tags_match.group(1) if tags_match else ""
        tags = [t.strip().strip("'\"") for t in tags_str.split(",") if t.strip().strip("'\"")]

        all_games.append({
            "id": gid,
            "name": name,
            "icon": icon,
            "iconColor": color,
            "tags": tags,
        })

    # Parse guidesData for guide info (title, readTime, excerpt)
    # First try standalone guidesData array; if not found, fall back to guide entries inside gamesData
    guides_match = re.search(r'const guidesData\s*=\s*\[([\s\S]*?)\n\];', main_js_content)
    guide_info = {}
    guides_block = None
    if guides_match:
        guides_block = guides_match.group(1)
    else:
        # Fallback: single gamesData array containing both games and guides
        games_match2 = re.search(r'const gamesData\s*=\s*\[([\s\S]*?)\n\];', main_js_content)
        if games_match2:
            guides_block = games_match2.group(1)

    if guides_block:
        guide_entries = re.split(r'\n\s*\},\s*\{', guides_block)
        for i, entry in enumerate(guide_entries):
            if i == 0:
                entry = entry.lstrip('[').strip()
                if not entry.startswith('{'):
                    entry = '{' + entry
            else:
                entry = '{' + entry
            if not entry.rstrip().endswith('}'):
                entry = entry + '}'

            # Skip entries that are games (have 'name' field but no 'gameId' field and no -guide id)
            id_match = re.search(r"id:\s*['\"]([^'\"]+)['\"]", entry)
            if not id_match:
                continue
            entry_id = id_match.group(1)
            has_gameId = re.search(r"gameId:\s*['\"]([^'\"]+)['\"]", entry) is not None
            has_title = re.search(r"title:\s*['\"]([^'\"]*)['\"]", entry) is not None
            # Only process guide entries (has gameId or has title or id ends with -guide)
            if not has_gameId and not has_title and not entry_id.endswith('-guide'):
                continue

            game_id_match = re.search(r"gameId:\s*['\"]([^'\"]+)['\"]", entry)
            if not game_id_match:
                if entry_id.endswith('-guide'):
                    game_id = entry_id.replace('-guide', '')
                else:
                    continue
            else:
                game_id = game_id_match.group(1)

            title_match = re.search(r"title:\s*['\"]([^'\"]*)['\"]", entry)
            readtime_match = re.search(r"readTime:\s*['\"]([^'\"]*)['\"]", entry)
            excerpt_match = re.search(r"excerpt:\s*['\"]([^'\"]*)['\"]", entry)

            guide_info[game_id] = {
                "title": title_match.group(1) if title_match else f"{game_id} Guide",
                "readTime": readtime_match.group(1) if readtime_match else "8 min",
                "excerpt": excerpt_match.group(1) if excerpt_match else "",
            }

    # Find related games: same tags first
    game_tags_set = set(t.lower() for t in (game_tags or []))

    scored = []
    for g in all_games:
        if g["id"] == game_slug:
            continue
        if g["id"] not in guide_info:
            continue
        shared = len(game_tags_set & set(t.lower() for t in g["tags"]))
        scored.append((shared, g))

    scored.sort(key=lambda x: -x[0])

    related = [g for _, g in scored if _ > 0][:4]

    # If not enough, fill with popular games
    POPULAR_FALLBACK = [
        "slither-io", "krunker-io", "shell-shockers", "agar-io",
        "diep-io", "paper-io", "hole-io", "moomoo-io",
    ]
    if len(related) < 4:
        existing_ids = {g["id"] for g in related}
        for slug in POPULAR_FALLBACK:
            if len(related) >= 4:
                break
            if slug == game_slug or slug in existing_ids:
                continue
            for g in all_games:
                if g["id"] == slug and slug in guide_info:
                    related.append(g)
                    existing_ids.add(slug)
                    break

    # If still not enough, add any game with a guide
    if len(related) < 4:
        existing_ids = {g["id"] for g in related}
        for g in all_games:
            if len(related) >= 4:
                break
            if g["id"] == game_slug or g["id"] in existing_ids:
                continue
            if g["id"] in guide_info:
                related.append(g)
                existing_ids.add(g["id"])

    if not related:
        return ""

    # Build HTML
    cards = []
    for g in related[:4]:
        info = guide_info.get(g["id"], {})
        title = info.get("title", f"{g['name']} Guide")
        read_time = info.get("readTime", "8 min")
        excerpt = info.get("excerpt", f"Complete guide for {g['name']}.")
        color = g.get("iconColor", "#6366f1")
        bg_color = color + "15" if len(color) == 7 else color

        card = f"""            <a href="https://iogameguide.com/guides/{g['id']}-guide" class="guide-card">
                <div class="guide-thumb" style="background: {bg_color}; border-radius: 8px;">
                    <span style="font-size: 2rem;">{g['icon']}</span>
                </div>
                <div class="guide-content">
                    <h3>{title}</h3>
                    <div class="guide-meta">
                        <span>{g['icon']} {g['name']}</span>
                        <span>\u23f1\ufe0f {read_time}</span>
                    </div>
                    <p class="guide-excerpt">{excerpt}</p>
                </div>
            </a>"""
        cards.append(card)

    cards_html = "\n".join(cards)
    html = f"""        <section class="related-guides">
            <div class="section-header">
                <h2 class="section-title">\U0001f4da Related Guides</h2>
            </div>
            <div class="guide-list">
{cards_html}
            </div>
        </section>"""

    return html


def escape_js_string(s: str) -> str:
    """Escape a string for use in a JavaScript single-quoted string literal."""
    return s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ")


def validate_guide_images(img_dir, game_name):
    """
    校验攻略图片质量，防止重复/低质图片被推送。
    使用 MD5 哈希进行精确内容去重（比文件大小比对更可靠）。
    返回 (passed: bool, errors: list[str], missing: list[str])
    missing: 缺失的图片文件名列表 (e.g. ["hero.jpg", "screenshot-1.jpg"])
    """
    required_files = ["hero.jpg", "screenshot-1.jpg", "screenshot-2.jpg", "screenshot-3.jpg"]
    min_size_hero_kb = 10        # hero 下载门槛3KB，校验门槛10KB
    min_size_screenshot_kb = 30  # screenshot 下载门槛30KB，校验门槛30KB
    errors = []
    missing = []
    file_info = []  # (fname, size_bytes, md5)

    for fname in required_files:
        fpath = os.path.join(img_dir, fname)
        # 检查文件是否存在
        if not os.path.exists(fpath):
            errors.append(f"缺失: {fname}")
            missing.append(fname)
            continue
        # 检查文件大小（hero 和 screenshot 使用不同门槛）
        min_size_kb = min_size_hero_kb if fname == "hero.jpg" else min_size_screenshot_kb
        size_kb = os.path.getsize(fpath) / 1024
        size_bytes = os.path.getsize(fpath)
        # 计算 MD5 用于精确内容去重
        try:
            with open(fpath, "rb") as f:
                md5 = compute_md5(f.read())
        except Exception:
            md5 = ""
        file_info.append((fname, size_bytes, md5))
        if size_kb < min_size_kb:
            errors.append(f"{fname} 过小 ({size_kb:.1f}KB < {min_size_kb}KB)")
            missing.append(fname)

    # 检查是否有重复：MD5 相同 → 内容完全相同；文件大小相同 → 可能重复
    for i in range(len(file_info)):
        for j in range(i + 1, len(file_info)):
            if file_info[i][2] and file_info[i][2] == file_info[j][2]:
                errors.append(f"重复(MD5): {file_info[i][0]} 和 {file_info[j][0]} 内容完全相同")
            elif file_info[i][1] == file_info[j][1]:
                errors.append(f"重复(大小): {file_info[i][0]} 和 {file_info[j][0]} 大小相同 ({file_info[i][1]}b)")

    passed = len(errors) == 0
    return passed, errors, missing


def extract_image_urls_from_text(text: str) -> list:
    """从搜索结果的文本中提取图片 URL。"""
    urls = []
    # 匹配 http/https 开头、以常见图片扩展名结尾的 URL
    for match in re.finditer(
        r'https?://[^\s"\'<>]+\.(?:jpg|jpeg|png|webp|avif|gif)(?:\?[^\s"\'<>]*)?',
        text, re.IGNORECASE
    ):
        url = match.group(0).rstrip('.,;:)')  # 去掉尾部标点
        if url not in urls:
            urls.append(url)
    return urls


def _is_svg_content(resp):
    """
    检查响应内容是否为 SVG 格式。
    SVG 图片保存为 .jpg 会导致无法显示，应跳过。
    返回 True 如果是 SVG。
    """
    # 方法1: 检查 Content-Type header
    content_type = resp.headers.get("content-type", "").lower()
    if "svg" in content_type:
        return True
    # 方法2: 检查响应体开头是否包含 SVG 标记
    try:
        head = resp.content[:500].lower()
        if b"<svg" in head or b"<?xml" in head and b"svg" in head:
            return True
    except Exception:
        pass
    return False


# ============================================================
# Image deduplication & validation helpers
# ============================================================




def _detect_real_format(data: bytes):
    """检测图片数据的真实格式（通过文件头魔数）。返回 PIL 格式名或 None。"""
    if len(data) < 12:
        return None
    head = data[:12]
    if head[:3] == b"\xff\xd8\xff":
        return "JPEG"
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        return "PNG"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "WEBP"
    if head[:6] in (b"GIF87a", b"GIF89a"):
        return "GIF"
    if head[:2] == b"BM":
        return "BMP"
    if len(data) >= 16 and head[4:8] == b"ftyp":
        brand = head[8:12]
        if brand in (b"avif", b"heic", b"heif", b"mif1"):
            return "AVIF"
    lower_head = data[:200].lower()
    if b"<svg" in lower_head or (b"<?xml" in lower_head and b"svg" in lower_head):
        return "SVG"
    try:
        from PIL import Image
        from io import BytesIO
        img = Image.open(BytesIO(data))
        return img.format
    except Exception:
        return None


def ensure_jpeg_bytes(data: bytes, quality: int = 85):
    """
    确保图片数据是真实的 JPEG 格式。
    如果是 WebP/PNG/GIF/BMP/AVIF 等非 JPEG 格式，用 PIL 转换编码为 JPEG。
    SVG 直接返回 None（不应保存为 JPG）。
    返回 (converted_data: bytes, original_format: str, is_converted: bool)。
    """
    real_fmt = _detect_real_format(data)
    if real_fmt == "JPEG":
        return (data, "JPEG", False)
    if real_fmt == "SVG":
        return (None, "SVG", False)
    try:
        from PIL import Image
        from io import BytesIO
        img = Image.open(BytesIO(data))
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        out = BytesIO()
        img.save(out, "JPEG", quality=quality, optimize=True)
        return (out.getvalue(), real_fmt or "unknown", True)
    except Exception as e:
        print(f"  [ensure_jpeg] 转换失败 ({real_fmt}): {e}")
        return (None, real_fmt or "unknown", False)

def compute_md5(data: bytes) -> str:
    """计算 bytes 数据的 MD5 哈希值，用于图片去重。"""
    return hashlib.md5(data).hexdigest()


def get_image_dimensions(data: bytes):
    """
    获取图片的宽高信息。
    返回 (width, height)，无法解析时返回 (0, 0)。
    """
    try:
        from PIL import Image
        img = Image.open(BytesIO(data))
        return img.size  # (width, height)
    except Exception:
        return (0, 0)


def is_valid_game_image(data: bytes, is_hero: bool, existing_md5s: set,
                        source_url: str = "", used_source_domains: list = None):
    """
    综合验证下载的图片是否适合作为游戏攻略图片。

    检查项：
    1. MD5 去重 — 与已下载的任何图片内容完全相同则拒绝
    2. 最小尺寸 — hero ≥ 1280x720, screenshot ≥ 400x400
    3. 宽高比验证 — 排除接近正方形的小图（icon/logo 特征）
    4. 来源多样性 — 软提示，同一域名已用过多时降低优先级但不硬拒

    返回 (is_valid: bool, reason: str, md5: str)
    """
    if used_source_domains is None:
        used_source_domains = []

    # 1. MD5 去重 — 硬性检查
    md5 = compute_md5(data)
    if md5 in existing_md5s:
        return (False, f"MD5重复({md5[:8]})", md5)

    # 2. 尺寸检查（PIL 可用时）
    w, h = get_image_dimensions(data)
    if w == 0 or h == 0:
        # PIL 无法解析尺寸（可能是 WebP/AVIF 等格式），只靠 MD5 + 文件大小判断
        return (True, f"OK(尺寸未知,{len(data)}b)", md5)

    if is_hero:
        min_w, min_h = 1280, 720
    else:
        min_w, min_h = 400, 400

    if w < min_w or h < min_h:
        return (False, f"尺寸不足({w}x{h}<{min_w}x{min_h})", md5)

    # 3. 宽高比验证 — 排除 icon/logo（接近正方形且尺寸不大的图）
    if not is_hero:
        ratio = w / h if h > 0 else 0
        # icon/logo 通常是正方形（0.85~1.15）且尺寸不大（≤600px）
        if 0.85 <= ratio <= 1.15 and max(w, h) <= 600:
            return (False, f"疑似icon/logo(正方形{w}x{h},比例{ratio:.2f})", md5)

    # 4. 来源多样性 — 软提示（不硬拒，但记录）
    src_domain = ""
    try:
        src_domain = urlparse(source_url).hostname or ""
    except Exception:
        pass
    diversity_note = ""
    if src_domain and src_domain in used_source_domains:
        domain_count = sum(1 for d in used_source_domains if d == src_domain)
        diversity_note = f" [来源重复:{src_domain}x{domain_count}]"

    return (True, f"OK({w}x{h}{diversity_note})", md5)


def record_image_source(source_url: str, used_source_domains: list):
    """记录图片来源域名，用于多样性追踪。使用 list 以统计同一域名的使用次数。"""
    try:
        domain = urlparse(source_url).hostname or ""
        if domain:
            used_source_domains.append(domain)



    except Exception:
        pass

# ============================================================
# Blog image filtering & LLM relevance verification
# ============================================================

# Non-game blog keywords — if found in image URL path/filename, likely NOT game-related
BLOG_KEYWORDS = [
    'skincare', 'fashion', 'wife', 'movie', 'business', 'luxury', 'watch',
    'bag', 'beauty', 'cosmetic', 'dress', 'shoe', 'jewelry', 'ring',
    'necklace', 'perfume', 'makeup', 'haircut', 'nail-art', 'spa', 'salon',
    'recipe', 'food-blog', 'cook', 'kitchen', 'restaurant', 'dining',
    'travel', 'vacation', 'hotel', 'flight', 'tourist', 'beach-photo',
    'wedding', 'baby-photo', 'kids-photo', 'family-photo',
    'home-decor', 'garden', 'furniture', 'interior-design',
    'real-estate', 'property', 'apartment', 'housing',
    'car-review', 'auto-show', 'motorcycle',
    'fitness', 'yoga-pose', 'gym-workout', 'diet-plan', 'weight-loss',
    'finance', 'stock-chart', 'investment', 'crypto', 'bitcoin',
    'health-tip', 'medical', 'doctor', 'pharmacy',
    'pet-care', 'dog-photo', 'cat-photo',
    'book-review', 'novel', 'music-album',
    'christmas', 'halloween', 'easter',
    'wallpaper-4k', 'desktop-background',
    'fan-cooler', 'cpu-cooler', 'pc-build',
    'mountain', 'landscape', 'sunset', 'sunrise',
    'selfie', 'portrait', 'model',
]

# Known game list/aggregator sites — reliable sources for game screenshots
GAME_LIST_DOMAINS = [
    'iogamelist.com', 'iogames.space', 'iogames.fun', 'bestiogames.com',
    'slopeonline.online', 'iogames.world', 'iogamez.com', 'iogames.gg',
    'crazygames.com', 'poki.com', 'y8.com', 'kizi.com',
    'iogames.site', 'iogamehub.com', 'io-games.com',
    'steamcdn-a.akamaihd.net', 'steamcdn.com', 'steamstatic.com',
    'miniclip.com', 'addictinggames.com', 'armorgames.com',
    'coolmathgames.com', 'silvergames.com',
]


def is_likely_blog_image(url: str) -> bool:
    """
    Heuristic check: does this image URL likely point to a non-game blog image?
    Returns True if the URL contains blog/non-game keywords.
    """
    url_lower = url.lower()
    # Extract the filename portion
    filename = url_lower.split('/')[-1].split('?')[0].replace('-', ' ').replace('_', ' ')

    # Check for blog keywords anywhere in the URL
    for kw in BLOG_KEYWORDS:
        if kw in url_lower:
            return True

    # WordPress uploads: check if filename has any game-related term
    if '/wp-content/uploads/' in url_lower:
        game_terms = [
            'game', 'play', 'screenshot', 'gameplay', 'screen', 'thumb',
            'cover', 'banner', 'hero', 'icon', 'logo', 'preview',
            'splash', 'feature', 'og-', 'og_', 'social',
        ]
        has_game_term = any(term in filename for term in game_terms)
        if not has_game_term:
            return True

    return False


def is_game_list_site(url: str) -> bool:
    """Check if URL is from a known game list/aggregator site."""
    try:
        domain = urlparse(url).hostname or ''
        for gd in GAME_LIST_DOMAINS:
            if gd in domain:
                return True
    except Exception:
        pass
    return False


def filter_and_prioritize_image_urls(urls: list, game_name: str = "") -> list:
    """
    Filter out likely blog images and prioritize game list site URLs.
    Returns a reordered list with game-list-site URLs first.
    """
    game_slug = game_name.lower().replace('.io', '').replace(' ', '-').strip() if game_name else ""

    filtered = []
    blog_skipped = 0
    for url in urls:
        if is_likely_blog_image(url):
            blog_skipped += 1
            continue
        filtered.append(url)

    if blog_skipped:
        print(f"  [URL过滤] 过滤掉 {blog_skipped} 个疑似博客图片URL")

    # Prioritize: game-list-site URLs first, then URLs containing game name
    game_site_urls = []
    game_name_urls = []
    other_urls = []
    for url in filtered:
        if is_game_list_site(url):
            game_site_urls.append(url)
        elif game_slug and game_slug in url.lower():
            game_name_urls.append(url)
        else:
            other_urls.append(url)

    result = game_site_urls + game_name_urls + other_urls
    return result


class ImageRelevanceCheck(BaseModel):
    """LLM structured output for image relevance verification."""
    is_game_related: bool
    reason: str


async def verify_image_relevance_llm(sdk, game_name: str, img_url: str) -> tuple:
    """
    Use LLM to verify if an image URL is likely game-related based on URL analysis.
    Returns (is_relevant: bool, reason: str).
    Fails open (returns True) if LLM is unavailable.
    """
    try:
        prompt = f"""You are verifying if an image URL points to a game screenshot or game-related image.

Game name: "{game_name}"
Image URL: {img_url}

Analyze the URL path, filename, and domain. Does this image appear to be game-related?

Indicators that it is NOT game-related (answer is_game_related=false):
- Blog post images (skincare, fashion, food, travel, real estate, hardware, nature photos)
- WordPress blog uploads with non-game filenames (e.g., /wp-content/uploads/2024/01/skincare-tips.jpg)
- URLs containing lifestyle, beauty, health, finance, or non-gaming keywords

Indicators that it IS game-related (answer is_game_related=true):
- Game list sites (iogamelist.com, crazygames.com, poki.com, etc.)
- URLs containing the game name or game-related terms (gameplay, screenshot, play)
- Game CDN/asset domains (steamcdn, etc.)

Be conservative: if uncertain, lean towards is_game_related=true."""

        result = await sdk.call_llm(
            messages=[{"role": "user", "content": prompt}],
            response_format=ImageRelevanceCheck,
        )
        if isinstance(result, ImageRelevanceCheck):
            return (result.is_game_related, result.reason)
        # Fallback: parse text response
        if isinstance(result, str):
            text = result.strip().upper()
            is_related = text.startswith("YES") or "TRUE" in text[:20]
            return (is_related, result[:100])
        return (True, "LLM返回格式异常,默认通过")
    except Exception as e:
        return (True, f"LLM验证异常,默认通过: {e}")


# ============================================================
# Dead game URL detection — 避免为已死亡的游戏网站生成攻略
# ============================================================
def _check_dns(url):
    """检查URL对应域名的DNS解析是否正常。返回 (success: bool, ip: str or None)。"""
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        return (False, None)
    try:
        ip = socket.gethostbyname(hostname)
        return (True, ip)
    except socket.gaierror:
        return (False, None)


def _check_cloudflare_error(resp):
    """
    检查响应是否为 Cloudflare 源服务器错误页面。
    返回 (is_dead: bool, reason: str or None)。
    Cloudflare 520-524 状态码表示源服务器有问题。
    """
    # Cloudflare 5xx: 520=Web server returns unknown error, 521=Web server is down,
    # 522=Connection timed out, 523=Origin is unreachable, 524=Timeout occurred
    if 520 <= resp.status_code <= 524:
        return (True, f"Cloudflare HTTP {resp.status_code} (origin server down)")
    # 也检查响应体中的 Cloudflare 错误标记（有些情况下状态码是200但页面是错误页）
    try:
        body = resp.text[:5000].lower()
        if "cloudflare" in body and (
            "error 522" in body or "error 521" in body
            or "origin web server timed out" in body
            or "web server is down" in body
        ):
            return (True, "Cloudflare error page detected (origin server down)")
    except Exception:
        pass
    return (False, None)


def _check_domain_sale(resp):
    """
    检查响应内容是否为域名售卖/停放页面。
    返回 (is_dead: bool, reason: str or None)。

    检测策略：
    1. 域名售卖平台特征（如 atom.com, dan.com, sedo.com, GoDaddy 售卖页等）
    2. 域名停放特征（domain parking, buy this domain, is for sale 等）
    3. 游戏特征缺失检测（如果页面没有任何游戏相关特征，可能是停放页）

    注意：只有明确检测到售卖/停放特征时才判定为死站，
    避免误杀正常游戏网站（有些游戏网站可能很简陋）。
    """
    try:
        body = resp.text[:10000].lower()
    except Exception:
        return (False, None)

    # --- 域名售卖平台特征（强信号，直接判定死站） ---
    sale_platform_indicators = [
        "atom.com",               # atom.com 域名交易平台
        "dan.com",                # dan.com 域名交易平台
        "sedo.com",               # sedo 域名交易平台
        "afternic.com",           # AfterNic 域名交易平台
        "flippa.com",             # Flippa 域名交易平台
        "bodis.com",              # Bodis 域名停放
        "sedoparking.com",        # Sedo 停放
        "godaddy.com/forsale",    # GoDaddy 售卖
        "buydomains.com",         # BuyDomains 平台
        "hugedomains.com",        # HugeDomains 平台
        "parkingcrew.net",        # ParkingCrew 停放
    ]
    for indicator in sale_platform_indicators:
        if indicator in body:
            return (True, f"Domain sale/parking page detected (contains '{indicator}')")

    # --- 域名售卖关键词特征（中等信号，需要组合判断） ---
    sale_keywords = [
        "is for sale",
        "buy this domain",
        "domain for sale",
        "purchase this domain",
        "this domain is for sale",
        "domain parking",
        "parked domain",
        "this domain has been parked",
        "make an offer",
        "domain marketplace",
        "premium domain",
        "domain name is for sale",
        "acquire this domain",
    ]
    sale_hits = [kw for kw in sale_keywords if kw in body]
    if len(sale_hits) >= 2:
        # 多个售卖关键词同时出现 → 判定死站
        return (True, f"Domain sale page detected (keywords: {', '.join(sale_hits[:3])})")

    # --- 域名停放页面特征（标题或页面结构） ---
    parking_structures = [
        'title>domain parked',
        'title>domain for sale',
        'title>this domain',
        'class="parked"',
        'id="parked"',
        'data-parking',
    ]
    for ps in parking_structures:
        if ps in body:
            return (True, f"Domain parking structure detected ('{ps}')")

    # --- 游戏特征检测（如果没有任何游戏特征但有售卖特征，判定死站） ---
    game_indicators = [
        "<canvas",              # HTML5 Canvas (游戏渲染)
        "unity",                # Unity WebGL
        "play",                 # Play button
        "game",                 # game 相关
        "join",                 # join game
        "start",                # start game
        "multiplayer",          # 多人游戏
        "phaser",               # Phaser 游戏引擎
        "pixi",                 # Pixi.js 游戏引擎
        "babylon",              # Babylon.js 引擎
        "three.js",             # Three.js 3D引擎
        "socket.io",            # 实时通信（多人游戏常用）
        "webgl",                # WebGL
        "gamecanvas",
        "playbutton",
        "play-game",
        "iframe",               # 嵌入游戏 iframe
    ]
    has_game_indicator = any(ind in body for ind in game_indicators)

    # 如果检测到售卖关键词但完全没有游戏特征 → 判定死站
    if len(sale_hits) >= 1 and not has_game_indicator:
        return (True, f"Domain sale page (keyword: '{sale_hits[0]}') with no game indicators")

    # --- 停放子域名检测（重定向到 ww数字. 子域名的停放页） ---
    # 特征组合判断（三条件全部满足才判定死站，避免误杀正常游戏网站）：
    #   1. 最终URL重定向到 ww<数字>. 前缀的子域名（如 ww547.bladers.io）
    #   2. 页面无游戏渲染元素（canvas/iframe/webgl 等严格子集，排除 play/game 等泛词）
    #   3. 页面有 noindex/nofollow meta 标签 或 链接目录结构（class="dir-link" 等）
    try:
        final_host = urlparse(resp.url.lower()).hostname or ""
        if re.match(r'^ww\d+\.', final_host):
            # 条件2：检查游戏渲染元素（严格子集，排除泛词）
            game_render_indicators = [
                "<canvas", "unity", "phaser", "pixi", "babylon",
                "three.js", "webgl", "gamecanvas", "iframe",
                "socket.io", "playbutton", "play-game",
            ]
            has_game_render = any(ind in body for ind in game_render_indicators)
            # 条件3：noindex/nofollow 或 链接目录结构
            has_noindex = 'noindex' in body and 'nofollow' in body
            dir_indicators = ['dir-link', 'list_1', 'list_2', 'related-links']
            has_dir_structure = any(ind in body for ind in dir_indicators)
            # 三条件组合判断
            if not has_game_render and (has_noindex or has_dir_structure):
                signals = []
                if has_noindex:
                    signals.append("noindex/nofollow")
                if has_dir_structure:
                    signals.append("link-directory structure")
                return (True, f"Parking subdomain detected (redirected to {final_host}, no game elements, {', '.join(signals)})")
    except Exception:
        pass

    return (False, None)


def _check_cross_domain_redirect(original_url, resp):
    """
    检查响应是否发生了跨域名跳转（重定向到不同域名）。
    返回 (is_dead: bool, reason: str or None)。

    跨域名跳转通常意味着原游戏网站已失效，被重定向到垃圾站/调查站/停放页等。
    同域名内的跳转（如 http→https、www→非www、子域名变化）属于正常行为，不判定死站。

    比较策略（逐级放宽，任一级匹配即视为同域名）：
    1. hostname 完全一致 → 同域名（含无跳转的情况）
    2. 去掉 www. 前缀后一致 → 同域名
    3. 根域名（最后两段，如 brawls.io）一致 → 同域名（子域名变化）
    4. 以上都不匹配 → 跨域名跳转 → 判定死站
    """
    try:
        original_host = (urlparse(original_url).hostname or "").lower()
        final_host = (urlparse(resp.url).hostname or "").lower()

        if not original_host or not final_host:
            return (False, None)

        # 1. hostname 完全一致（含无跳转的情况）
        if original_host == final_host:
            return (False, None)

        # 2. 去掉 www. 前缀后比较
        def _strip_www(h):
            return h[4:] if h.startswith("www.") else h

        orig_norm = _strip_www(original_host)
        final_norm = _strip_www(final_host)
        if orig_norm == final_norm:
            return (False, None)

        # 3. 根域名（最后两段）一致 → 同站子域名跳转
        #    例: play.brawls.io → brawls.io 视为同域名
        orig_root = ".".join(orig_norm.split(".")[-2:])
        final_root = ".".join(final_norm.split(".")[-2:])
        if orig_root == final_root:
            return (False, None)

        # 4. 根域名不同 → 跨域名跳转 → 死站
        return (True, f"Redirected to different domain: {final_host}")
    except Exception:
        return (False, None)


def check_game_url(url):
    """
    检查游戏网站URL是否存活。
    返回 (is_dead: bool, reason: str)

    多层检测策略（宁可误杀，不放过死站）：
    1. 第一轮请求 (5s超时, HTTPS)
       - 跨域名跳转 → 确认死亡（重定向到不同域名，通常是垃圾站/调查站）
       - HTTP 200 → 内容验证（检查域名售卖/停放页）→ 通过则活着，否则死站
       - Cloudflare 5xx → 确认死亡
       - HTTP 5xx → 确认死亡
       - HTTP 4xx → 不算死亡（可能反爬）
    2. 超时 → 第二轮请求 (15s超时，先HTTPS再HTTP降级)
       - 得到响应 → 按状态码 + 内容验证判断
       - 再次超时 → 进入DNS检测
    3. DNS最终裁决
       - DNS解析失败 → 确认死亡
       - DNS解析成功但两次请求都超时 → 确认死亡（服务器无响应）
    4. ConnectionError → 检查DNS
       - DNS失败 → 确认死亡
       - DNS成功但连接被拒 → 确认死亡（保守策略）
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    # --- Round 1: HTTPS, 5s timeout ---
    try:
        resp = requests.get(url, timeout=5, allow_redirects=True, headers=headers)
        # 跨域名跳转检测：如果最终URL域名和原始域名不同，判定死站
        xd_dead, xd_reason = _check_cross_domain_redirect(url, resp)
        if xd_dead:
            return (True, xd_reason)
        if resp.status_code == 200:
            # 内容验证：检查是否为域名售卖/停放页面
            sale_dead, sale_reason = _check_domain_sale(resp)
            if sale_dead:
                return (True, sale_reason)
            return (False, "ok")
        cf_dead, cf_reason = _check_cloudflare_error(resp)
        if cf_dead:
            return (True, cf_reason)
        if 500 <= resp.status_code < 600:
            return (True, f"HTTP {resp.status_code}")
        return (False, f"HTTP {resp.status_code} (non-fatal)")
    except requests.exceptions.Timeout:
        pass  # 进入 Round 2
    except requests.exceptions.ConnectionError as e:
        err_str = str(e).lower()
        if "name or service not known" in err_str or "gaierror" in err_str:
            return (True, "DNS resolution failed (ConnectionError)")
        dns_ok, _ = _check_dns(url)
        if not dns_ok:
            return (True, "DNS resolution failed (ConnectionError)")
        return (True, "Connection failed but DNS resolves (server likely down)")
    except Exception as e:
        return (True, f"Unknown error: {type(e).__name__}")

    # --- Round 2: Retry with longer timeout (15s), try HTTP fallback ---
    parsed = urlparse(url)
    http_url = url.replace("https://", "http://", 1) if parsed.scheme == "https" else url

    for attempt_url, attempt_label in [(url, "HTTPS"), (http_url, "HTTP-fallback")]:
        try:
            resp = requests.get(attempt_url, timeout=15, allow_redirects=True, headers=headers)
            # 跨域名跳转检测
            xd_dead, xd_reason = _check_cross_domain_redirect(attempt_url, resp)
            if xd_dead:
                return (True, xd_reason)
            if resp.status_code == 200:
                # 内容验证：检查是否为域名售卖/停放页面
                sale_dead, sale_reason = _check_domain_sale(resp)
                if sale_dead:
                    return (True, sale_reason)
                return (False, f"ok (retry via {attempt_label})")
            cf_dead, cf_reason = _check_cloudflare_error(resp)
            if cf_dead:
                return (True, cf_reason)
            if 500 <= resp.status_code < 600:
                return (True, f"HTTP {resp.status_code} (retry via {attempt_label})")
            return (False, f"HTTP {resp.status_code} (non-fatal, retry via {attempt_label})")
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            continue
        except Exception:
            continue

    # --- Round 3: Both rounds timed out — DNS check as final arbiter ---
    dns_ok, dns_ip = _check_dns(url)
    if not dns_ok:
        return (True, "DNS resolution failed (after timeout)")
    # DNS解析成功但服务器两次请求都无响应 → 死站（保守策略）
    return (True, f"Server unresponsive (DNS resolves to {dns_ip}, timed out twice)")


def load_dead_games():
    """加载死站名单，返回 slug 字符串集合。文件不存在返回空set。"""
    try:
        with open(DEAD_GAMES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(item["slug"] for item in data if "slug" in item)
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def add_dead_game(slug, name, reason):
    """向 dead_games.json 追加一条死站记录（避免重复添加同一slug）。"""
    try:
        with open(DEAD_GAMES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    # 避免重复添加同一slug
    for item in data:
        if item.get("slug") == slug:
            return

    data.append({
        "slug": slug,
        "name": name,
        "reason": reason,
        "date": datetime.now().strftime("%Y-%m-%d")
    })

    # 确保目录存在
    os.makedirs(os.path.dirname(DEAD_GAMES_FILE), exist_ok=True)

    with open(DEAD_GAMES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================
# Main
# ============================================================
async def main():
    result_mode = sys.argv[1] if len(sys.argv) > 1 else "notify"
    github_token = sys.argv[2] if len(sys.argv) > 2 else ""

    print(f"[参数] result_mode={result_mode}, token={'***' if github_token else '无'}")

    sdk = CodeActSDK()

    try:
        # ============================================================
        # Step 1: Get existing games from GitHub
        # ============================================================
        print("[步骤1] 获取已有游戏列表...")
        resp = retry_get(GITHUB_RAW_MAINJS, timeout=30)
        resp.raise_for_status()
        main_js_text = resp.text

        # Parse gamesData — extract all id values
        games_match = re.search(r'const gamesData\s*=\s*\[([\s\S]*?)\n\];', main_js_text)
        if not games_match:
            raise Exception("无法解析 gamesData，正则未匹配")

        existing_ids = set(re.findall(r"id:\s*['\"]([^'\"]+)['\"]", games_match.group(1)))
        print(f"[步骤1] 已有 {len(existing_ids)} 个游戏（gamesData）")

        # 也解析 guidesData — 提取所有 gameId，确保已有攻略的游戏不会被重复选择
        guides_match = re.search(r'const guidesData\s*=\s*\[([\s\S]*?)\n\];', main_js_text)
        all_guide_ids = set()
        if guides_match:
            guide_game_ids = set(re.findall(r"gameId:\s*['\"]([^'\"]+)['\"]", guides_match.group(1)))
            # 也提取 guidesData 中的 id（去掉 -guide 后缀得到 gameId）
            guide_ids = set(re.findall(r"id:\s*['\"]([^'\"]+)['\"]", guides_match.group(1)))
            guide_game_ids_from_ids = {gid.replace('-guide', '') for gid in guide_ids if gid.endswith('-guide')}
            all_guide_ids = guide_game_ids | guide_game_ids_from_ids
        else:
            # Fallback: single gamesData array — extract guide entries (id ends with -guide or has gameId)
            # 从 gamesData 中提取所有攻略相关的 gameId
            games_block = games_match.group(1)
            # 从 id 字段提取：以 -guide 结尾的 id 去掉后缀得到 gameId
            guide_ids_from_games = set(re.findall(r"id:\s*['\"]([^'\"]+-guide)['\"]", games_block))
            all_guide_ids = {gid.replace('-guide', '') for gid in guide_ids_from_games}
            # 也从 gameId 字段提取（有些条目可能直接有 gameId）
            gameId_fields = set(re.findall(r"gameId:\s*['\"]([^'\"]+)['\"]", games_block))
            all_guide_ids = all_guide_ids | gameId_fields

        if all_guide_ids:
            new_from_guides = all_guide_ids - existing_ids
            if new_from_guides:
                print(f"[步骤1] 从 guidesData 额外发现 {len(new_from_guides)} 个已有攻略的游戏: {new_from_guides}")
            existing_ids = existing_ids.union(all_guide_ids)
        print(f"[步骤1] 合并后共 {len(existing_ids)} 个已覆盖游戏")

        # 黑名单：这些游戏域名无效或已关闭，不应选择
        BLACKLIST = {'aggie-io', 'agario-io'}  # aggie.io redirects to magma.com; agario.io is duplicate of agar.io
        existing_ids = existing_ids.union(BLACKLIST)  # 加入黑名单，视为已存在
        print(f"[步骤1] 黑名单游戏: {BLACKLIST}")

        # 加载死站名单，将死站slug加入existing_ids（和黑名单一样处理，视为已存在跳过）
        dead_game_slugs = load_dead_games()
        if dead_game_slugs:
            existing_ids = existing_ids.union(dead_game_slugs)
            print(f"[步骤1] 死站游戏 ({len(dead_game_slugs)}个): {dead_game_slugs}")

        # ============================================================
        # Step 2: Search for popular .io games (broad + niche + directories)
        # ============================================================
        print("[步骤2] 搜索热门 .io 游戏...")
        search_queries = [
            "best .io games 2026",
            "popular multiplayer browser games .io",
            "top new .io games to play online free",
            "underrated .io games worth playing",
            "new .io games 2025 2026 multiplayer",
            "list of .io browser games playable online"
        ]

        all_search_results = []
        for query in search_queries:
            try:
                result = await sdk.call_tool(
                    "codeact_search_web",
                    {"query": query, "response_length": "medium"},
                    schema_version=SEARCH_VER
                )
                if result.get("is_success") and result.get("results"):
                    all_search_results.extend(result["results"])
            except Exception as e:
                print(f"  搜索失败 '{query}': {e}")

        # Also fetch comprehensive game directories
        print("  从游戏目录获取更多游戏...")
        directory_urls = [
            "https://iogames.space/popular",
            "https://iogames.space/category/crazy-games",
        ]
        for durl in directory_urls:
            try:
                dir_page = await sdk.call_tool(
                    "codeact_fetch_web",
                    {"url": durl},
                    schema_version=FETCH_VER
                )
                if dir_page.get("is_success"):
                    # Add as a pseudo-search-result with the directory content
                    all_search_results.append({
                        "title": f"Directory: {durl}",
                        "url": durl,
                        "snippet": dir_page.get("content", "")[:2000]
                    })
            except Exception as e:
                print(f"  目录获取失败 '{durl}': {e}")

        if not all_search_results:
            raise Exception("搜索无结果，无法继续")

        print(f"[步骤2] 搜索到 {len(all_search_results)} 条结果")

        # ============================================================
        # Step 3: Find new games — parse directory content + LLM enrich
        # ============================================================
        print("[步骤3] 提取候选游戏并过滤...")

        # 3a: Extract game names/slugs from all search results and directory content
        # Look for patterns like "GameName.io", "game-name.io" in all text
        all_text = " ".join([
            f"{r.get('title', '')} {r.get('snippet', '')}"
            for r in all_search_results
        ])

        # Extract .io game names from text (e.g., "BuildRoyale.io", "lolbeans.io")
        io_game_names = set()
        # Pattern 1: CamelCase or single-word names ending in .io (e.g., BuildRoyale.io, Krunker.io)
        for match in re.finditer(r'([A-Z][A-Za-z0-9]*\.io)', all_text):
            name = match.group(1).strip()
            if 4 < len(name) < 30:
                io_game_names.add(name)

        # Pattern 2: Multi-word .io names (e.g., "Shell Shockers", "Smash Karts" from directory)
        # Look for lines like "GameName 4.3" or "GameName.io 3.7" from directory pages
        for match in re.finditer(r'([A-Z][A-Za-z0-9]+(?:\s[A-Za-z0-9]+){0,2}(?:\.io)?)\s+\d+\.\d+', all_text):
            name = match.group(1).strip()
            if 2 < len(name) < 30:
                if not name.endswith('.io'):
                    name = name + '.io'
                io_game_names.add(name)

        # Convert names to slugs and filter out existing games
        candidates = []
        seen_slugs = set()
        # 目录页面常见伪游戏名（从目录页面文本误提取的名称前缀）
        DIRECTORY_ARTIFACTS = {
            'all-io-games', 'all-io', 'allio', 'allgames',
            'top-io-games', 'best-io-games', 'new-io-games',
            'popular-io-games', 'crazy-games', 'iogames',
        }
        for name in sorted(io_game_names):
            # Generate slug: lowercase, replace dots/spaces with hyphens
            slug = name.lower().replace('.io', '').replace('.io', '').strip()
            slug = re.sub(r'[\s.]+', '-', slug).strip('-')
            if not slug:
                continue
            # Add -io suffix if not already there
            slug = slug + '-io' if not slug.endswith('-io') else slug
            # Clean up
            slug = slug.replace('--', '-').strip('-')

            # Skip if slug is too long (likely a bad extraction) or already seen
            if len(slug) > 30 or slug in seen_slugs:
                continue

            # 验证 slug 不是目录页面伪游戏名
            # 检查 slug 是否以目录伪名开头（如 "all-io-gamesev-io" 以 "all-io-games" 开头）
            is_artifact = False
            for artifact in DIRECTORY_ARTIFACTS:
                if slug.startswith(artifact) and len(slug) > len(artifact) + 3:
                    print(f"  [跳过] slug '{slug}' 疑似目录伪游戏名（前缀 '{artifact}'），跳过")
                    is_artifact = True
                    break
            if is_artifact:
                continue

            seen_slugs.add(slug)

            if slug not in existing_ids:
                candidates.append((name, slug))

        print(f"  从搜索结果提取 {len(io_game_names)} 个 .io 游戏，{len(candidates)} 个未覆盖")

        # 3b: If not enough from text extraction, use LLM to suggest from its knowledge
        if len(candidates) < 3:
            print("  文本提取不足，使用 LLM 补充...")
            llm_result = await sdk.call_llm(
                messages=[{
                    "role": "user",
                    "content": f"""List 20 .io browser games that are NOT in this list:
{json.dumps(sorted(existing_ids))}

Format: one game per line, just the full game name (e.g., "BuildRoyale.io").
Include lesser-known and newer games, not just the most famous ones.
Each game must end in .io and be a real, playable browser game."""
                }]
            )

            if isinstance(llm_result, str):
                for line in llm_result.strip().split('\n'):
                    line = line.strip().lstrip('0123456789.-) ')
                    if '.io' in line.lower() and len(line) < 40:
                        io_game_names.add(line)
                        slug = line.lower().replace('.io', '').replace('.IO', '').strip()
                        slug = re.sub(r'[\s.]+', '-', slug).strip('-') + '-io'
                        slug = slug.replace('--', '-').strip('-')
                        if slug not in existing_ids:
                            candidates.append((line, slug))

            print(f"  LLM 补充后，共 {len(candidates)} 个未覆盖候选")

        if not candidates:
            raise Exception("所有候选游戏都已存在于 gamesData 中")

        # 3c: Use LLM to rank candidates by popularity, then enrich + URL存活检查
        # Take up to 15 candidates for LLM to rank
        top_candidates = candidates[:15]
        candidate_names = [name for name, slug in top_candidates]

        print(f"  候选游戏 (前15): {candidate_names}")

        # Ask LLM to return top 5 most popular games in ranked order
        ranking_result = await sdk.call_llm(
            messages=[{
                "role": "user",
                "content": f"""Rank these .io browser games by how well-known and popular they are.
Games: {json.dumps(candidate_names)}

Return the TOP 10 most popular games, one per line, in order from most popular to least.
Consider: active player base, cultural recognition, Google search volume, YouTube content.
Just return game names, one per line, nothing else."""
            }]
        )

        # Parse the LLM's ranked list into (name, slug) pairs
        ranked_candidates = []
        if isinstance(ranking_result, str):
            for line in ranking_result.strip().split('\n'):
                rname = line.strip().lstrip('0123456789.-) ')
                if not rname:
                    continue
                # Find matching candidate
                for name, slug in top_candidates:
                    if name.lower() == rname.lower() or rname.lower() in name.lower():
                        ranked_candidates.append((name, slug))
                        break
                else:
                    # Try partial match
                    for name, slug in top_candidates:
                        base = name.replace('.io', '').lower()
                        if base in rname.lower() or rname.lower().replace('.io', '') in base:
                            ranked_candidates.append((name, slug))
                            break

        # Fallback: if LLM didn't return valid matches, use original candidate order
        if not ranked_candidates:
            ranked_candidates = top_candidates[:10]

        # Ensure we try at most 10 candidates
        max_attempts = min(10, len(ranked_candidates))
        if max_attempts == 0:
            raise Exception("无可用候选游戏")

        print(f"  排名候选 (前{max_attempts}): {[name for name, _ in ranked_candidates[:max_attempts]]}")

        # 3d: Try each ranked candidate — enrich + URL存活检查（最多10次）
        game = None
        skipped_games = []  # 收集被跳过的死站游戏信息 [{name, url, reason}, ...]
        for attempt in range(max_attempts):
            selected_name, selected_slug = ranked_candidates[attempt]
            print(f"  [尝试 {attempt+1}/{max_attempts}] 候选: {selected_name} ({selected_slug})")

            # Search for real game info before LLM enrichment (anti-hallucination)
            game_search_context = ""
            try:
                search_resp = await sdk.call_tool(
                    "codeact_search_web",
                    {"query": f"{selected_name} .io game gameplay description how to play"},
                    schema_version=SEARCH_VER
                )
                if search_resp.get("is_success") and search_resp.get("results"):
                    snippets = []
                    for r in search_resp["results"][:3]:
                        title = r.get("title", "")
                        snippet = r.get("content", "") or r.get("snippet", "")
                        if snippet:
                            snippets.append(f"{title}: {snippet[:500]}")
                    game_search_context = "\n".join(snippets)[:2000]
            except Exception as e:
                print(f"  游戏搜索失败: {e}")

            # Enrich the selected game with details using LLM
            game_info_result = await sdk.call_llm(
                messages=[{
                    "role": "user",
                    "content": f"""Provide details for the .io browser game "{selected_name}":

Search results about this game:
{game_search_context}

Based on the search results above (and your knowledge if the search results are insufficient), provide:
- icon: A single emoji that best represents this game
- icon_color: A hex color code that matches the game's theme (e.g., "#FF6B6B")
- difficulty: Integer 1-5 (1=very easy, 5=very hard)
- tags: Array of 2-3 English category tags
- description: One short sentence describing the game's ACTUAL core gameplay. Base this on the search results, NOT on guessing from the game name.
- game_url: The game's official website URL

IMPORTANT: The description must describe the game's REAL mechanics. Do NOT guess. If the search results don't clearly describe the game, say so honestly in the description rather than guessing."""
                }],
                response_format=GameCandidate
            )

            if isinstance(game_info_result, str):
                try:
                    parsed = json.loads(game_info_result)
                    game = GameCandidate(
                        name=selected_name,
                        slug=selected_slug,
                        icon=parsed.get('icon', '🎮'),
                        icon_color=parsed.get('icon_color', '#6366F1'),
                        difficulty=parsed.get('difficulty', 3),
                        tags=parsed.get('tags', ['Multiplayer', 'Browser']),
                        description=parsed.get('description', f'Play {selected_name} online for free.'),
                        game_url=parsed.get('game_url', f'https://{selected_name.lower().replace(" ", "")}')
                    )
                except Exception:
                    game = GameCandidate(
                        name=selected_name, slug=selected_slug, icon='🎮',
                        icon_color='#6366F1', difficulty=3, tags=['Multiplayer', 'Browser'],
                        description=f'Play {selected_name} online for free.',
                        game_url=f'https://{selected_name.lower().replace(" ", "")}'
                    )
            elif hasattr(game_info_result, 'name'):
                game = game_info_result
                # slug is set below in the common validation block
            else:
                game = GameCandidate(
                    name=selected_name, slug=selected_slug, icon='🎮',
                    icon_color='#6366F1', difficulty=3, tags=['Multiplayer', 'Browser'],
                    description=f'Play {selected_name} online for free.',
                    game_url=f'https://{selected_name.lower().replace(" ", "")}'
                )

            # 确保 slug 始终使用我们生成的值（防止 LLM 返回不同的 slug）
            game.slug = selected_slug

            # 验证并修正 game_url — 确保是有效的 .io 游戏网站 URL
            # 如果 LLM 返回的 URL 不以 http 开头，或包含异常前缀，则从 slug 重新生成
            game_url = game.game_url.strip() if game.game_url else ""
            base_name = selected_name.replace('.io', '').replace('.IO', '').strip().lower().replace(' ', '')
            expected_url = f"https://{base_name}.io"
            if not game_url or not game_url.startswith('http') or 'all-io-games' in game_url.lower():
                game.game_url = expected_url
                print(f"  [URL修正] game_url 不合法，从游戏名重新生成: {game.game_url}")

            # URL存活检查
            is_dead, reason = check_game_url(game.game_url)
            if is_dead:
                print(f"[URL检查] {game.name} ({game.game_url}) 已死亡: {reason}，跳过")
                add_dead_game(game.slug, game.name, reason)
                skipped_games.append({"name": game.name, "url": game.game_url, "reason": reason})
                game = None  # 重置，继续尝试下一个候选
                continue
            else:
                print(f"[URL检查] {game.name} ({game.game_url}) 存活检查通过: {reason}")
                break  # 找到存活游戏，退出循环

        if game is None:
            # 所有候选游戏URL都不可用 — 收集信息通知主人，不崩溃
            skipped_lines = "\n".join(
                f"  • {g['name']} ({g['url']}): {g['reason']}"
                for g in skipped_games
            )
            notify_msg = (
                f"[主人](at://owner) ⚠️ 今日尝试了 {len(skipped_games)} 个候选游戏，URL全部不可用\n\n"
                f"尝试的游戏及失败原因：\n{skipped_lines}\n\n"
                f"请确认是否跳过今日攻略，或手动指定游戏。"
            )
            await sdk.submit_result(
                result_mode="notify",
                status="warning",
                message=notify_msg
            )
            return

        print(f"[步骤3] ✅ 选择游戏: {game.name} (slug: {game.slug}, difficulty: {game.difficulty})")

        # ============================================================
        # Step 4: Fetch key files from GitHub via REST API (no git clone)
        # ============================================================
        print("[步骤4] 通过 GitHub REST API 获取关键文件...")
        subprocess.run(["rm", "-rf", REPO_DIR], check=False, capture_output=True)
        os.makedirs(REPO_DIR, exist_ok=True)
        os.makedirs(f"{REPO_DIR}/guides", exist_ok=True)
        os.makedirs(f"{REPO_DIR}/css", exist_ok=True)
        os.makedirs(f"{REPO_DIR}/js", exist_ok=True)
        os.makedirs(f"{REPO_DIR}/images/games/{game.slug}", exist_ok=True)

        # Use provided token or fallback
        GITHUB_TOKEN = github_token or os.environ.get("GITHUB_TOKEN", "os.environ.get("GITHUB_TOKEN", "")")
        if not GITHUB_TOKEN:
            raise Exception("GitHub token 未配置，无法使用 REST API")

        # Fetch main.js
        print("  拉取 js/main.js ...")
        main_js_content_local, _ = github_file_get("js/main.js", GITHUB_TOKEN)
        if main_js_content_local is None:
            raise Exception("无法获取 main.js")
        with open(f"{REPO_DIR}/js/main.js", "w", encoding="utf-8") as f:
            f.write(main_js_content_local)
        print(f"  ✅ main.js ({len(main_js_content_local)} bytes)")

        # Fetch sitemap.xml
        print("  拉取 sitemap.xml ...")
        sitemap_content_local, _ = github_file_get("sitemap.xml", GITHUB_TOKEN)
        if sitemap_content_local:
            with open(f"{REPO_DIR}/sitemap.xml", "w", encoding="utf-8") as f:
                f.write(sitemap_content_local)
            print(f"  ✅ sitemap.xml ({len(sitemap_content_local)} bytes)")
        else:
            print("  ⚠️ sitemap.xml 未找到，将生成新文件")

        # Fetch index.html and games.html (for step 9.7)
        print("  拉取 index.html ...")
        index_html_local, _ = github_file_get("index.html", GITHUB_TOKEN)
        if index_html_local:
            with open(f"{REPO_DIR}/index.html", "w", encoding="utf-8") as f:
                f.write(index_html_local)
            print(f"  ✅ index.html ({len(index_html_local)} bytes)")

        print("  拉取 games.html ...")
        games_html_local, _ = github_file_get("games.html", GITHUB_TOKEN)
        if games_html_local:
            with open(f"{REPO_DIR}/games.html", "w", encoding="utf-8") as f:
                f.write(games_html_local)
            print(f"  ✅ games.html ({len(games_html_local)} bytes)")

        # Try to fetch existing guide HTML (for Related Guides preservation)
        existing_guide_path = f"guides/{game.slug}-guide.html"
        print(f"  检查现有攻略 {existing_guide_path} ...")
        old_guide_html, _ = github_file_get(existing_guide_path, GITHUB_TOKEN)
        if old_guide_html:
            with open(f"{REPO_DIR}/guides/{game.slug}-guide.html", "w", encoding="utf-8") as f:
                f.write(old_guide_html)
            print(f"  ✅ 现有攻略已保存到本地 ({len(old_guide_html)} bytes)")
        else:
            print("  ℹ️ 该游戏暂无现有攻略（全新创建）")

        print("[步骤4] ✅ 关键文件拉取完成（REST API 模式）")

        # ============================================================
        # Step 5: Download game screenshots (three-layer strategy)
        #   Layer 1: Extract og:image from official game website
        #   Layer 2: Search-based image download (existing logic)
        #   Layer 3: AI generation fallback (report to main agent)
        # ============================================================
        print("[步骤5] 搜索并下载游戏截图...")
        img_dir = f"{REPO_DIR}/images/games/{game.slug}"
        os.makedirs(img_dir, exist_ok=True)

        # 区分 hero 和 screenshot 的质量要求：
        # - hero.jpg: >3KB 即可（Logo/宣传图/美化图都接受）
        # - screenshot-1/2/3: >30KB（必须是游戏实际画面截图，排除小图标和Logo）
        MIN_SIZE_HERO = 3000  # 3KB for hero
        MIN_SIZE_SCREENSHOT = 30000  # 30KB for screenshots (real gameplay)

        # --- 图片去重和来源追踪（跨 Layer 1/2 共享） ---
        downloaded_md5s = set()          # 已下载图片的 MD5 集合（内容去重）
        used_source_domains = []         # 已使用图片来源域名列表（多样性追踪，list 可统计重复次数）

        # --- Layer 1: 优先从官网提取 og:image 作为 hero ---
        hero_from_og = None
        website_html = None  # 保存官网HTML供Layer 2 website策略复用
        try:
            print(f"  [Layer 1] 尝试提取官网 og:image: {game.game_url}")
            resp = retry_get(game.game_url, timeout=10, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, allow_redirects=True)
            if resp.status_code == 200:
                html = resp.text
                og_match = re.search(r'<meta\s+(?:property|name)=["\']og:image(?::url)?["\']\s+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
                if not og_match:
                    og_match = re.search(r'<meta\s+content=["\']([^"\']+)["\']\s+(?:property|name)=["\']og:image(?::url)?["\']', html, re.IGNORECASE)
                if og_match:
                    og_url = og_match.group(1)
                    # 下载 og:image
                    img_resp = retry_get(og_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
                    if img_resp.status_code == 200 and len(img_resp.content) > MIN_SIZE_HERO and b"<html" not in img_resp.content[:500].lower() and not _is_svg_content(img_resp):
                        # MD5 去重 + 尺寸验证
                        _hero_valid, _hero_reason, _hero_md5 = is_valid_game_image(
                            img_resp.content, is_hero=True, existing_md5s=downloaded_md5s,
                            source_url=og_url, used_source_domains=used_source_domains
                        )
                        if _hero_valid:
                            _jpeg_data, _orig_fmt, _converted = ensure_jpeg_bytes(img_resp.content)
                            if _jpeg_data is None:
                                print(f"  og:image 转换失败 (格式: {_orig_fmt})，跳过")
                            else:
                                with open(f"{img_dir}/hero.jpg", "wb") as f:
                                    f.write(_jpeg_data)
                                hero_from_og = og_url
                                _hero_md5 = compute_md5(_jpeg_data)
                                downloaded_md5s.add(_hero_md5)
                                record_image_source(og_url, used_source_domains)
                                _conv_note = " [WebP→JPEG]" if _converted else ""
                                print(f"  ✅ og:image 下载成功: {len(_jpeg_data)} bytes ({_hero_reason}){_conv_note}")
                        else:
                            print(f"  og:image 验证失败: {_hero_reason} (size={len(img_resp.content)} bytes)")
                    else:
                        svg_note = " [SVG detected, skipped]" if _is_svg_content(img_resp) else ""
                        print(f"  og:image 下载失败 (size={len(img_resp.content)}){svg_note}")
                else:
                    print(f"  官网无 og:image 标签")
            else:
                print(f"  官网访问失败 (status={resp.status_code})")
        except Exception as e:
            print(f"  og:image 提取失败: {e}")

        # 捕获Layer 1获取的官网HTML，供Layer 2 website策略复用（不修改Layer 1逻辑）
        try:
            website_html = html  # html变量在Layer 1中赋值（resp.status_code == 200时）
        except NameError:
            website_html = None

        # --- Layer 2: 图片获取 (website策略: 从官网HTML提取 / search策略: 多关键词搜索) ---
        if hero_from_og:
            image_names = ["screenshot-1.jpg", "screenshot-2.jpg", "screenshot-3.jpg"]
            downloaded = 0  # hero 已从 og:image 获取，只需下载 3 张截图
            print(f"  [Layer 2] hero 已从 og:image 获取，只需截图")
        else:
            image_names = ["hero.jpg", "screenshot-1.jpg", "screenshot-2.jpg", "screenshot-3.jpg"]
            downloaded = 0
            print(f"  [Layer 2] hero 未获取，需要全部图片")
        total_needed = len(image_names)  # 3 (hero from og) or 4 (all from search)

        # --- Layer 2: 图片获取策略 (website/search/hybrid) ---
        use_website = IMAGE_STRATEGY in ("website", "hybrid")
        use_search = IMAGE_STRATEGY in ("search", "hybrid")

        if use_website:
            # --- Layer 2 (website): 从官网HTML提取<img>标签图片作为截图 ---
            print(f"  [Layer 2-website] 从官网HTML提取图片 (策略: {IMAGE_STRATEGY})")
            from urllib.parse import urljoin, urlparse
            candidate_img_urls = []

            if website_html:
                # 解析所有 <img> 标签的 src 属性
                img_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
                for match in img_pattern.finditer(website_html):
                    src = match.group(1).strip()
                    # 过滤: data URI 内联图
                    if src.startswith('data:'):
                        continue
                    # 补全为绝对URL（处理相对路径）
                    abs_url = urljoin(game.game_url, src)
                    # 过滤: og:image 本身（已用作 hero）
                    if hero_from_og and (abs_url == hero_from_og or src == hero_from_og):
                        continue
                    if abs_url not in candidate_img_urls:
                        candidate_img_urls.append(abs_url)
                print(f"  [Layer 2-website] 从官网HTML提取到 {len(candidate_img_urls)} 个图片URL")
            else:
                print(f"  [Layer 2-website] ⚠️ 官网HTML不可用，无候选图片")

            # URL过滤: 移除疑似博客图片，优先游戏列表站
            candidate_img_urls = filter_and_prioritize_image_urls(candidate_img_urls, game.name)
            print(f"  [Layer 2-website] URL过滤后剩余 {len(candidate_img_urls)} 个候选")

            for img_url in candidate_img_urls:
                if downloaded >= total_needed:
                    break
                try:
                    img_resp = retry_get(
                        img_url, timeout=15, allow_redirects=True,
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                    )
                    content_type = img_resp.headers.get("content-type", "")
                    img_size = len(img_resp.content)
                    is_not_html = b"<html" not in img_resp.content[:500].lower()
                    is_not_svg = not _is_svg_content(img_resp)
                    # 判断当前要下载的是 hero 还是 screenshot
                    current_fname = image_names[downloaded]
                    is_hero = (current_fname == "hero.jpg")
                    min_size = MIN_SIZE_HERO if is_hero else MIN_SIZE_SCREENSHOT
                    if img_resp.status_code == 200 and img_size > min_size and is_not_html and is_not_svg:
                        # MD5 去重 + 尺寸检查 + 类型验证
                        _valid, _reason, _md5 = is_valid_game_image(
                            img_resp.content, is_hero, downloaded_md5s,
                            source_url=img_url, used_source_domains=used_source_domains
                        )
                        if _valid:
                            # LLM验证: 分析URL是否与游戏相关
                            _llm_ok, _llm_reason = await verify_image_relevance_llm(sdk, game.name, img_url)
                            if not _llm_ok:
                                print(f"  跳过(website): LLM判定非游戏图片 - {_llm_reason} ({img_size}b)")
                                continue
                            _jpeg_data, _orig_fmt, _converted = ensure_jpeg_bytes(img_resp.content)
                            if _jpeg_data is None:
                                print(f"  跳过(website) {current_fname}: 非可转换图片格式 ({_orig_fmt})")
                                continue
                            with open(f"{img_dir}/{current_fname}", "wb") as f:
                                f.write(_jpeg_data)
                            _final_md5 = compute_md5(_jpeg_data)
                            if _final_md5 in downloaded_md5s and _final_md5 != _md5:
                                print(f"  跳过(website) {current_fname}: 转码后 MD5 重复 ({_final_md5[:8]})")
                                os.remove(f"{img_dir}/{current_fname}")
                                continue
                            downloaded_md5s.add(_final_md5)
                            record_image_source(img_url, used_source_domains)
                            img_type = "hero" if is_hero else "screenshot"
                            _conv_note = " [WebP→JPEG]" if _converted else ""
                            print(f"  ✅ 下载(website): {current_fname} ({len(_jpeg_data)}b, {img_type}, {_reason}, LLM✓){_conv_note}")
                            downloaded += 1
                        else:
                            print(f"  跳过(website): {_reason} ({img_size}b)")
                    else:
                        reasons = []
                        if not is_not_html:
                            reasons.append("HTML非图片")
                        if not is_not_svg:
                            reasons.append("SVG格式跳过")
                        if img_size <= min_size:
                            reasons.append(f"太小({img_size}b<{min_size}b)")
                        if not reasons:
                            reasons.append(f"HTTP {img_resp.status_code}")
                        print(f"  跳过(website): {', '.join(reasons)} ({content_type}, {img_size}b)")
                except Exception as e:
                    print(f"  跳过(website): {e}")

            print(f"  [Layer 2-website] 已下载 {downloaded}/{total_needed} 张，不足部分走 Layer 3 AI生成")

        # hybrid模式: website策略截图不足3张时，回退到search策略补充
        _screenshot_count = sum(1 for i in range(1, 4) if os.path.exists(f"{img_dir}/screenshot-{i}.jpg"))
        if use_search and (not use_website or _screenshot_count < 3):
            if use_website:
                print(f"  [Layer 2-hybrid] website策略仅获取 {_screenshot_count}/3 张截图，回退到search策略补充")
            # --- Layer 2 (search): 多关键词网络搜索图片 ---
            print(f"  [Layer 2-search] 多关键词搜索图片 (策略: {IMAGE_STRATEGY})")
            candidate_img_urls = []

            # 5a: 多关键词搜索 — 始终执行全部3个关键词，合并去重，候选量翻倍
            search_keywords = [
                f"{game.name} gameplay screenshot",
                f"{game.name} tips guide",
                f"{game.name} review",
            ]
            for idx, kw in enumerate(search_keywords, 1):
                print(f"  图片搜索{idx}: '{kw}'")
                try:
                    search_result = await sdk.call_tool(
                        "codeact_search_web",
                        {"query": kw, "engine": "image"},
                        schema_version=SEARCH_VER
                    )
                    if search_result.get("is_success") and search_result.get("results"):
                        for r in search_result["results"]:
                            url = r.get("url", "")
                            snippet = r.get("snippet", "")
                            if url and any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif']):
                                if url not in candidate_img_urls:
                                    candidate_img_urls.append(url)
                            snippet_urls = extract_image_urls_from_text(snippet)
                            for u in snippet_urls:
                                if u not in candidate_img_urls:
                                    candidate_img_urls.append(u)
                        print(f"    图片搜索{idx}: 累计 {len(candidate_img_urls)} 个候选URL")
                except Exception as e:
                    print(f"  图片搜索{idx}失败: {e}")

            # 5b: 视觉搜索作为补充来源（不依赖候选数，始终执行）
            print(f"  视觉搜索: '{game.name} gameplay'")
            try:
                img_search_v = await sdk.call_tool(
                    "codeact_search_web",
                    {"query": f"{game.name} gameplay", "engine": "visual"},
                    schema_version=SEARCH_VER
                )
                if img_search_v.get("is_success") and img_search_v.get("results"):
                    for r in img_search_v["results"]:
                        url = r.get("url", "")
                        snippet = r.get("snippet", "")
                        if url and any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif']):
                            if url not in candidate_img_urls:
                                candidate_img_urls.append(url)
                        snippet_urls = extract_image_urls_from_text(snippet)
                        for u in snippet_urls:
                            if u not in candidate_img_urls:
                                candidate_img_urls.append(u)
                    print(f"    视觉搜索: 累计 {len(candidate_img_urls)} 个候选URL")
            except Exception as e:
                print(f"  视觉搜索失败: {e}")

            print(f"  总候选截图 URL: {len(candidate_img_urls)} 个")

            # URL过滤: 移除疑似博客图片，优先游戏列表站
            candidate_img_urls = filter_and_prioritize_image_urls(candidate_img_urls, game.name)
            print(f"  [Layer 2-search] URL过滤后剩余 {len(candidate_img_urls)} 个候选")

            # 5e: Download images from candidate URLs
            screenshot_downloaded = 0

            for img_url in candidate_img_urls:
                if downloaded >= total_needed:
                    break
                try:
                    img_resp = retry_get(
                        img_url, timeout=15, allow_redirects=True,
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                    )
                    content_type = img_resp.headers.get("content-type", "")
                    img_size = len(img_resp.content)
                    is_not_html = b"<html" not in img_resp.content[:500].lower()
                    is_not_svg = not _is_svg_content(img_resp)

                    # 判断当前要下载的是 hero 还是 screenshot
                    current_fname = image_names[downloaded]
                    is_hero = (current_fname == "hero.jpg")
                    min_size = MIN_SIZE_HERO if is_hero else MIN_SIZE_SCREENSHOT

                    if img_resp.status_code == 200 and img_size > min_size and is_not_html and is_not_svg:
                        # MD5 去重 + 尺寸检查 + 类型验证
                        _valid, _reason, _md5 = is_valid_game_image(
                            img_resp.content, is_hero, downloaded_md5s,
                            source_url=img_url, used_source_domains=used_source_domains
                        )
                        if _valid:
                            # LLM验证: 分析URL是否与游戏相关
                            _llm_ok, _llm_reason = await verify_image_relevance_llm(sdk, game.name, img_url)
                            if not _llm_ok:
                                print(f"  跳过: LLM判定非游戏图片 - {_llm_reason} ({img_size}b)")
                                continue
                            _jpeg_data, _orig_fmt, _converted = ensure_jpeg_bytes(img_resp.content)
                            if _jpeg_data is None:
                                print(f"  跳过 {current_fname}: 非可转换图片格式 ({_orig_fmt})")
                                continue
                            with open(f"{img_dir}/{current_fname}", "wb") as f:
                                f.write(_jpeg_data)
                            _final_md5 = compute_md5(_jpeg_data)
                            if _final_md5 in downloaded_md5s and _final_md5 != _md5:
                                print(f"  跳过 {current_fname}: 转码后 MD5 重复 ({_final_md5[:8]})")
                                os.remove(f"{img_dir}/{current_fname}")
                                continue
                            downloaded_md5s.add(_final_md5)
                            record_image_source(img_url, used_source_domains)
                            img_type = "hero" if is_hero else "screenshot"
                            _conv_note = " [WebP→JPEG]" if _converted else ""
                            print(f"  ✅ 下载: {current_fname} ({len(_jpeg_data)}b, {img_type}, {_reason}, LLM✓){_conv_note}")
                            downloaded += 1
                            if not is_hero:
                                screenshot_downloaded += 1
                        else:
                            print(f"  跳过: {_reason} ({img_size}b)")
                    else:
                        reasons = []
                        if not is_not_html:
                            reasons.append("HTML非图片")
                        if not is_not_svg:
                            reasons.append("SVG格式跳过")
                        if img_size <= min_size:
                            reasons.append(f"太小({img_size}b<{min_size}b)")
                        if not reasons:
                            reasons.append(f"HTTP {img_resp.status_code}")
                        print(f"  跳过: {', '.join(reasons)} ({content_type}, {img_size}b)")
                except Exception as e:
                    print(f"  跳过: {e}")

        # Record which images are missing (no placeholder creation)
        missing_images = []
        for i in range(downloaded, total_needed):
            missing_images.append(image_names[i].replace('.jpg', ''))  # e.g. "screenshot-2", "screenshot-3"

        # --- Layer 3: 检查 hero.jpg 是否缺失或尺寸不对，尝试裁剪修复，不行再AI兜底 ---
        hero_needs_ai = False
        if not os.path.exists(f"{img_dir}/hero.jpg"):
            print(f"  [Layer 3] ⚠️ hero.jpg 缺失（og:image 和搜索均未获取），需要主 Agent AI 生成兜底")
            hero_needs_ai = True
        else:
            try:
                from PIL import Image as PILImage
                hero_img = PILImage.open(f"{img_dir}/hero.jpg")
                w, h = hero_img.size
                ratio = w / h if h > 0 else 0
                if ratio >= 1.5:
                    print(f"  [Layer 3] ✅ hero.jpg 尺寸合格: {w}x{h} (比例{ratio:.2f})")
                elif w >= 800:
                    # 图足够大，居中裁剪成16:9横版
                    target_ratio = 16 / 9
                    new_h = int(w / target_ratio)
                    if new_h <= h:
                        top = (h - new_h) // 2
                        cropped = hero_img.crop((0, top, w, top + new_h))
                        cropped.save(f"{img_dir}/hero.jpg", quality=90)
                        print(f"  [Layer 3] ✂️ hero.jpg 裁剪: {w}x{h} → {w}x{new_h} (比例{w/new_h:.2f})")
                    else:
                        # 宽不够撑16:9，以高度为基准裁宽度
                        new_w = int(h * target_ratio)
                        if new_w <= w:
                            left = (w - new_w) // 2
                            cropped = hero_img.crop((left, 0, left + new_w, h))
                            cropped.save(f"{img_dir}/hero.jpg", quality=90)
                            print(f"  [Layer 3] ✂️ hero.jpg 裁剪: {w}x{h} → {new_w}x{h} (比例{new_w/h:.2f})")
                        else:
                            print(f"  [Layer 3] ⚠️ hero.jpg {w}x{h} 无法裁剪成横版，需要 AI 生成兜底")
                            os.remove(f"{img_dir}/hero.jpg")
                            hero_needs_ai = True
                else:
                    # 图较小，先2x放大再裁剪成16:9横版
                    upscale = 2
                    new_w_total = w * upscale
                    new_h_total = h * upscale
                    hero_img_upscaled = hero_img.resize((new_w_total, new_h_total), PILImage.LANCZOS)
                    print(f"  [Layer 3] 🔍 hero.jpg 2x放大: {w}x{h} → {new_w_total}x{new_h_total}")
                    target_ratio = 16 / 9
                    crop_h = int(new_w_total / target_ratio)
                    if crop_h <= new_h_total:
                        top = (new_h_total - crop_h) // 2
                        cropped = hero_img_upscaled.crop((0, top, new_w_total, top + crop_h))
                        cropped.save(f"{img_dir}/hero.jpg", quality=90)
                        print(f"  [Layer 3] ✂️ hero.jpg 放大+裁剪: {w}x{h} → {new_w_total}x{crop_h} (比例{new_w_total/crop_h:.2f})")
                    else:
                        # 放大后仍无法裁成16:9
                        crop_w = int(new_h_total * target_ratio)
                        if crop_w <= new_w_total:
                            left = (new_w_total - crop_w) // 2
                            cropped = hero_img_upscaled.crop((left, 0, left + crop_w, new_h_total))
                            cropped.save(f"{img_dir}/hero.jpg", quality=90)
                            print(f"  [Layer 3] ✂️ hero.jpg 放大+裁剪: {w}x{h} → {crop_w}x{new_h_total} (比例{crop_w/new_h_total:.2f})")
                        else:
                            print(f"  [Layer 3] ⚠️ hero.jpg {w}x{h} 放大后仍无法裁成横版，需要 AI 生成兜底")
                            os.remove(f"{img_dir}/hero.jpg")
                            hero_needs_ai = True
            except ImportError:
                print(f"  [Layer 3] ⚠️ PIL未安装，跳过hero尺寸校验")
            except Exception as e:
                print(f"  [Layer 3] ⚠️ hero尺寸校验异常: {e}")
        if hero_needs_ai and "hero" not in missing_images:
            missing_images.append("hero")

        # 5f: 兜底复制机制 — 截图不足时从已下载图片中复制补位（轮换源图减少重复）
        all_image_files = ["hero.jpg", "screenshot-1.jpg", "screenshot-2.jpg", "screenshot-3.jpg"]
        missing_files = [f for f in all_image_files if not os.path.exists(f"{img_dir}/{f}")]

        if missing_files:
            existing_files = [(f, os.path.getsize(f"{img_dir}/{f}")) for f in all_image_files if os.path.exists(f"{img_dir}/{f}")]
            if existing_files:
                # 去重：如果现有图片中有 MD5 相同的，只保留一份作为复制源
                from collections import OrderedDict
                unique_sources = OrderedDict()
                for fname, fsize in existing_files:
                    try:
                        with open(f"{img_dir}/{fname}", "rb") as _ff:
                            _fmd5 = compute_md5(_ff.read())
                        if _fmd5 not in unique_sources:
                            unique_sources[_fmd5] = (fname, fsize)
                    except Exception:
                        unique_sources[f"fallback_{fname}"] = (fname, fsize)
                source_list = list(unique_sources.values())
                source_list.sort(key=lambda x: x[1], reverse=True)
                if len(source_list) > 1:
                    print(f"  [兜底复制] 缺失 {missing_files}，从 {len(source_list)} 张唯一图片补位（MD5去重后）")
                else:
                    print(f"  [兜底复制] 缺失 {missing_files}，仅 1 张可用源，复制后可能存在重复（源不足）")
                copy_sources_used = []
                for idx, missing_fname in enumerate(missing_files):
                    source_idx = idx % len(source_list)
                    src_fname, src_size = source_list[source_idx]
                    src_path = f"{img_dir}/{src_fname}"
                    missing_path = f"{img_dir}/{missing_fname}"
                    shutil.copy2(src_path, missing_path)
                    copy_sources_used.append(src_fname)
                    print(f"  ✅ 补位: {missing_fname} <- {src_fname} ({src_size}b)")
                    m_name = missing_fname.replace('.jpg', '')
                    if m_name in missing_images:
                        missing_images.remove(m_name)

                # 如果所有补位都用了同一个源，提示重复风险
                if len(set(copy_sources_used)) == 1 and len(missing_files) > 1:
                    print(f"  ⚠️ 所有补位图片均来自 {copy_sources_used[0]}，存在重复风险（仅1张可用源图）")
            else:
                print(f"  [兜底复制] 无可用图片文件，无法补位")

        # 最终状态报告（基于实际文件存在情况）
        total_downloaded = downloaded + (1 if hero_from_og else 0)
        actual_existing = sum(1 for f in all_image_files if os.path.exists(f"{img_dir}/{f}"))
        if missing_images:
            print(f"  ⚠️ 已下载 {total_downloaded}/4 张，缺失: {missing_images}（需要主 Agent 补生成）")
        else:
            copied_count = actual_existing - total_downloaded
            copy_info = f"，兜底复制 {copied_count} 张" if copied_count > 0 else ""
            print(f"  ✅ 全部 {actual_existing}/4 张图片就绪（下载 {total_downloaded}{copy_info}）")

        print(f"[步骤5] ✅ 图片完成 ({actual_existing}/4 张就绪, og:image={'✅' if hero_from_og else '❌'})")

        # ============================================================
        # Step 6: Generate guide content via LLM
        # ============================================================
        print("[步骤6] 生成攻略内容...")

        # Fetch reference info about the game (enhanced: try multiple URLs + official site)
        game_info = ""
        try:
            info_search = await sdk.call_tool(
                "codeact_search_web",
                {"query": f"{game.name} wiki guide tips strategies gameplay mechanics"},
                schema_version=SEARCH_VER
            )
            if info_search.get("is_success") and info_search.get("results"):
                # Try top 3 URLs until we get valid content
                for r in info_search["results"][:3]:
                    url = r.get("url", "")
                    if not url:
                        continue
                    try:
                        page = await sdk.call_tool(
                            "codeact_fetch_web",
                            {"url": url},
                            schema_version=FETCH_VER
                        )
                        if page.get("is_success"):
                            content = page.get("content", "")
                            if content and len(content) > 200:
                                game_info = content[:4000]
                                break
                    except:
                        continue
        except Exception as e:
            print(f"  信息获取失败: {e}")

        # Also try fetching the official game site for description
        if not game_info:
            try:
                site_page = await sdk.call_tool(
                    "codeact_fetch_web",
                    {"url": game.game_url},
                    schema_version=FETCH_VER
                )
                if site_page.get("is_success"):
                    game_info = site_page.get("content", "")[:3000]
            except:
                pass

        if game_info:
            print(f"  📖 获取到游戏参考资料 ({len(game_info)} 字符)")
        else:
            print(f"  ⚠️ 未获取到游戏参考资料，LLM将仅基于游戏描述生成（可能影响准确性）")

        guide = await sdk.call_llm(
            messages=[{
                "role": "user",
                "content": f"""Write a complete game guide for {game.name}.

Game description: {game.description}
Official URL: {game.game_url}
Reference material: {game_info[:3000]}

Write these 6 sections in English. Be SPECIFIC to {game.name} — no generic filler.

1. introduction (100-150 words): What is {game.name}, what makes it unique, why players love it.
2. getting_started (150-200 words): How to start, controls, first steps, basic mechanics.
3. basic_tips (150-200 words): 4-5 essential tips for beginners, with specific examples.
4. advanced_strategies (150-200 words): 3-4 strategies for experienced players.
5. pro_tips (100-150 words): 3-4 expert-level tips that separate good from great players.
6. conclusion (50-100 words): Summary and encouragement to try the game.

CRITICAL ANTI-HALLUCINATION RULES:
- Only describe game mechanics that are confirmed by the Reference material or Description above.
- If the Reference material is empty or insufficient, focus on general .io game mechanics that apply broadly, and explicitly note which aspects are general advice vs. game-specific.
- DO NOT invent specific game mechanics (e.g., thirst meters, evolution systems, biomes, dash abilities) unless they appear in the reference material or description.
- If you are uncertain about a specific mechanic, describe it generically or omit it rather than guessing."""
            }],
            response_format=GuideContent
        )

        print("[步骤6] ✅ 攻略内容生成完成")

        # ============================================================
        # Step 7: Create HTML file
        # ============================================================
        print("[步骤7] 生成 HTML 文件...")
        today = datetime.now().strftime("%Y-%m-%d")
        timestamp = today.replace("-", "")

        # Generate Related Guides section
        main_js_for_rg = ""
        main_js_path_rg = f"{REPO_DIR}/js/main.js"
        if os.path.exists(main_js_path_rg):
            with open(main_js_path_rg, "r", encoding="utf-8") as f:
                main_js_for_rg = f.read()
        related_guides_html = generate_related_guides_html(game.slug, game.tags, main_js_for_rg)

        html = fill_template(
            HTML_TEMPLATE,
            GAME_NAME=game.name,
            GAME_SLUG=game.slug,
            GAME_ICON=game.icon,
            GAME_URL=game.game_url,
            DATE=today,
            READING_TIME="8",
            INTRODUCTION=guide.introduction,
            GETTING_STARTED=guide.getting_started,
            BASIC_TIPS=guide.basic_tips,
            ADVANCED_STRATEGIES=guide.advanced_strategies,
            PRO_TIPS=guide.pro_tips,
            CONCLUSION=guide.conclusion,
            TIMESTAMP=timestamp,
            GAME_GENRE=", ".join(game.tags),
            RELATED_GUIDES=related_guides_html
        )

        guide_html_path = f"{REPO_DIR}/guides/{game.slug}-guide.html"
        with open(guide_html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[步骤7] ✅ HTML 写入: {guide_html_path}")

        # ============================================================
        # Step 8: Update main.js — gamesData & guidesData
        # ============================================================
        print("[步骤8] 更新 main.js...")
        main_js_path = f"{REPO_DIR}/js/main.js"
        with open(main_js_path, "r", encoding="utf-8") as f:
            main_js_content = f.read()

        # --- 8a: Add new game to gamesData (at the END, before ];) ---
        games_start = main_js_content.find("const gamesData")
        if games_start == -1:
            raise Exception("找不到 gamesData")

        # Find the ]; that closes gamesData — it's the first one after gamesData starts
        games_closing = main_js_content.find("\n];", games_start)
        if games_closing == -1:
            raise Exception("找不到 gamesData 的 ];")

        new_game_js = f"""    {{
    id: '{escape_js_string(game.slug)}',
    name: '{escape_js_string(game.name)}',
    icon: '{game.icon}',
    iconColor: '{game.icon_color}',
    guideCount: 1,
    difficulty: {game.difficulty},
    tags: {json.dumps(game.tags)},
    description: '{escape_js_string(game.description)}'
    }}"""

        # Insert with smart comma handling: ensure exactly one comma separator
        # Find the last } before the closing ];
        pre_closing = main_js_content[:games_closing].rstrip()
        if pre_closing.endswith(","):
            # Last entry already has trailing comma — just append new entry
            main_js_content = (
                main_js_content[:games_closing] + "\n" +
                new_game_js +
                main_js_content[games_closing:]
            )
        elif pre_closing.endswith("}"):
            # Last entry has no trailing comma — add one
            main_js_content = (
                main_js_content[:games_closing] + ",\n" +
                new_game_js +
                main_js_content[games_closing:]
            )
        else:
            # Fallback: just add comma + entry
            main_js_content = (
                main_js_content[:games_closing] + ",\n" +
                new_game_js +
                main_js_content[games_closing:]
            )
        print("  ✅ gamesData 已更新（末尾追加）")

        # --- 8b: Add new guide to guidesData (at the END, before ];) ---
        # Build excerpt from introduction (max 120 chars)
        excerpt = guide.introduction[:120].replace("\n", " ").replace("'", "\\'")
        if len(guide.introduction) > 120:
            excerpt += "..."

        new_guide_js = f"""    {{
        id: '{escape_js_string(game.slug)}-guide',
        title: '{escape_js_string(game.name)} Guide: Tips, Strategies & Advanced Techniques',
        game: '{escape_js_string(game.name)}',
        gameId: '{escape_js_string(game.slug)}',
        date: '{today}',
        url: '{escape_js_string(game.slug)}-guide',
        image: '{escape_js_string(game.slug)}',
        difficulty: {game.difficulty},
        readTime: '8 min',
        excerpt: '{excerpt}'
    }}"""

        guides_start = main_js_content.find("const guidesData")
        if guides_start != -1:
            # Separate guidesData array exists — append there
            guides_closing = main_js_content.find("\n];", guides_start)
            if guides_closing == -1:
                raise Exception("找不到 guidesData 的 ];")

            # Smart comma handling for guidesData
            pre_closing = main_js_content[:guides_closing].rstrip()
            if pre_closing.endswith(","):
                main_js_content = (
                    main_js_content[:guides_closing] + "\n" +
                    new_guide_js +
                    main_js_content[guides_closing:]
                )
            elif pre_closing.endswith("}"):
                main_js_content = (
                    main_js_content[:guides_closing] + ",\n" +
                    new_guide_js +
                    main_js_content[guides_closing:]
                )
            else:
                main_js_content = (
                    main_js_content[:guides_closing] + ",\n" +
                    new_guide_js +
                    main_js_content[guides_closing:]
                )
            print("  ✅ guidesData 已更新（末尾追加）")
        else:
            # Fallback: single gamesData array (no separate guidesData)
            # Append guide entry at the end of gamesData
            print("  ⚠️ 未找到独立的 guidesData 数组，将攻略条目追加到 gamesData 末尾")
            games_start_pos = main_js_content.find("const gamesData")
            if games_start_pos == -1:
                raise Exception("找不到 gamesData")
            # Find the closing of gamesData (the first \n]; after const gamesData)
            games_closing_pos = main_js_content.find("\n];", games_start_pos)
            if games_closing_pos == -1:
                raise Exception("找不到 gamesData 的 ];")

            pre_closing = main_js_content[:games_closing_pos].rstrip()
            if pre_closing.endswith(","):
                main_js_content = (
                    main_js_content[:games_closing_pos] + "\n" +
                    new_guide_js +
                    main_js_content[games_closing_pos:]
                )
            elif pre_closing.endswith("}"):
                main_js_content = (
                    main_js_content[:games_closing_pos] + ",\n" +
                    new_guide_js +
                    main_js_content[games_closing_pos:]
                )
            else:
                main_js_content = (
                    main_js_content[:games_closing_pos] + ",\n" +
                    new_guide_js +
                    main_js_content[games_closing_pos:]
                )
            print("  ✅ 攻略条目已追加到 gamesData 末尾")

        with open(main_js_path, "w", encoding="utf-8") as f:
            f.write(main_js_content)
        print("[步骤8] ✅ main.js 已保存")

        # ============================================================
        # Step 9: Update sitemap.xml
        # ============================================================
        print("[步骤9] 更新 sitemap.xml...")
        sitemap_path = f"{REPO_DIR}/sitemap.xml"
        with open(sitemap_path, "r", encoding="utf-8") as f:
            sitemap = f.read()

        guide_url = f"{SITE_BASE}/guides/{game.slug}-guide"
        if guide_url in sitemap:
            print(f"[步骤9] ⏭️ {game.slug}-guide 已在 sitemap 中，跳过")
        else:
            new_url_entry = f"""  <url>
    <loc>{guide_url}</loc>
    <lastmod>{today}</lastmod>
    <priority>0.8</priority>
  </url>
"""
            sitemap = sitemap.replace("</urlset>", new_url_entry + "</urlset>")
            with open(sitemap_path, "w", encoding="utf-8") as f:
                f.write(sitemap)
            print("[步骤9] ✅ sitemap.xml 已更新")

        # ============================================================
        # Step 9.5: Validate image quality (防重复/低质图)
        # 不再中止流程，改为记录缺失信息到 missing_images
        # ============================================================
        print("[步骤9.5] 校验图片质量...")
        img_dir = f"{REPO_DIR}/images/games/{game.slug}"
        img_passed, img_errors, img_missing = validate_guide_images(img_dir, game.name)
        if not img_passed:
            error_detail = "\n  ".join(img_errors)
            print(f"  ⚠️ 图片质量校验未通过:\n  {error_detail}")
            # Merge with already-tracked missing images (from download phase)
            for m in img_missing:
                m_name = m.replace('.jpg', '')
                if m_name not in missing_images:
                    missing_images.append(m_name)
            # 专门检查 hero.jpg 缺失，输出 AI 生成提示
            if "hero" in [m.replace('.jpg', '') for m in img_missing] or not os.path.exists(f"{img_dir}/hero.jpg"):
                print(f"  ⚠️ hero.jpg 缺失，请主 Agent 使用 image_generate 工具生成：")
                print(f"     游戏名：{game.name}，风格：游戏宣传海报，竖版")
            # 删除不合格的 hero.jpg，防止被 git add 推到 GitHub
            if "hero" in missing_images:
                hero_jpg = f"{img_dir}/hero.jpg"
                if os.path.exists(hero_jpg):
                    hero_size = os.path.getsize(hero_jpg)
                    os.remove(hero_jpg)
                    print(f"  🗑️ 已删除不合格的 hero.jpg ({hero_size / 1024:.1f}KB)，防止推送空/小图到 GitHub")
        else:
            print("[步骤9.5] ✅ 图片质量校验通过（4张图均>50KB且各不相同）")


        # ============================================================
        # Step 9.7: Update static links in index.html and games.html
        # ============================================================
        print("[步骤9.7] 更新首页和游戏页静态链接...")
        try:
            # 获取所有攻略列表（从本地 sitemap.xml，已在步骤4拉取）
            sitemap_local_path = os.path.join(REPO_DIR, "sitemap.xml")
            if os.path.exists(sitemap_local_path):
                with open(sitemap_local_path, "r", encoding="utf-8") as f:
                    sitemap_content = f.read()
            else:
                # Fallback: fetch from API
                sitemap_content, _ = github_file_get("sitemap.xml", GITHUB_TOKEN)
                if not sitemap_content:
                    sitemap_content = ""
            guide_slugs = re.findall(r'<loc>https://iogameguide\.com/guides/([^<]+)</loc>', sitemap_content)
            print(f"  获取到 {len(guide_slugs)} 个攻略")
            
            # slug 到显示名称的映射函数
            def slug_to_name(slug):
                name = slug.replace('-guide', '').replace('-advanced', '').replace('-builds', '').replace('-boost', '')
                special_map = {
                    'agar-io': 'Agar.io', 'angry-worms-io': 'Angry Worms.io', 'bloxd-io': 'Bloxd.io',
                    'blumgi-rocket': 'Blumgi Rocket', 'brutalmania-io': 'BrutalMania.io',
                    'crazysteve-io': 'CrazySteve.io', 'curser-io': 'Curser.io', 'defend-io': 'Defend.io',
                    'defly-io': 'Defly.io', 'diep-io': 'Diep.io', 'dogod-io': 'Dogod.io',
                    'evowars-io': 'EvoWars.io', 'gartic-io': 'Gartic.io', 'goons-io': 'Goons.io',
                    'gulper-io': 'Gulper.io', 'hole-io': 'Hole.io', 'krunker-io': 'Krunker.io',
                    'liquid-swarm': 'Liquid Swarm', 'littlebigsnake-io': 'LittleBigSnake.io',
                    'medieval-io': 'Medieval.io', 'moomoo-io': 'MooMoo.io', 'mope-io': 'Mope.io',
                    'nobrakes-io': 'NoBrakes.io', 'paper-io': 'Paper.io', 'repuls-io': 'Repuls.io',
                    'sandboxels': 'Sandboxels', 'shell-shockers': 'Shell Shockers', 'skribbl-io': 'Skribbl.io',
                    'slither-io': 'Slither.io', 'smashkarts-io': 'SmashKarts.io', 'snowball-io': 'Snowball.io',
                    'spawner-io': 'Spawner.io', 'spinner-io': 'Spinner.io', 'starblast-io': 'Starblast.io',
                    'superhex-io': 'Superhex.io', 'surviv-io': 'Surviv.io', 'swordz-io': 'Swordz.io',
                    'taming-io': 'Taming.io', 'stickman-hook': 'Stickman Hook', 'venge-io': 'Venge.io',
                    'voxelim-io': 'Voxelim.io', 'warden-io': 'Warden.io', 'wings-io': 'Wings.io',
                    'wormate-io': 'Wormate.io', 'wormax-io': 'Wormax.io', 'yohoho-io': 'Yohoho.io',
                    'zapper-io': 'Zapper.io', 'zombsroyale-io': 'ZombsRoyale.io', 'splix-io': 'Splix.io',
                    'hordes-io': 'Hordes.io', 'poxel-io': 'Poxel.io', 'war-brokers': 'War Brokers',
                    'starve-io': 'Starve.io', '1v1-lol': '1v1.LOL', 'hexanaut-io': 'Hexanaut.io',
                    'deadshot-io': 'DeadShot.io', 'curve-fever-pro': 'Curve Fever Pro', 'deeeep-io': 'Deeeep.io',
                    'kirka-io': 'Kirka.io', 'kour-io': 'Kour.io', 'ninja-io': 'Ninja.io',
                    'arrow-arena': 'Arrow Arena', 'bonk-io': 'Bonk.io', 'florr-io': 'Florr.io',
                    'ev-io': 'Ev.io', 'schoolbreak-io': 'Schoolbreak.io', 'tetr-io': 'TETR.IO',
                    'devast-io': 'Devast.io', 'betrayal-io': 'Betrayal.io', 'snake-io': 'Snake.io',
                    'flyordie-io': 'FlyOrDie.io', 'limax-io': 'Limax.io',
                    'a-slithery-snake-and-snowball-io': 'A Slithery Snake & Snowball.io',
                    'aipaperanimals-io': 'AIPaperAnimals.io', 'arras-io': 'Arras.io', 'amogus-io': 'Amogus.io',
                    'agma-io': 'Agma.io', 'aquapark-io': 'AquaPark.io', 'arena-io': 'Arena.io',
                    'brutal-io': 'Brutal.io'
                }
                return special_map.get(name.lower(), name.replace('-', ' ').title())
            
            # 热门游戏（前6个用于首页 popularGames）
            popular_slugs = [
                "agar-io-guide", "slither-io-guide", "diep-io-guide", "paper-io-guide",
                "hole-io-guide", "krunker-io-guide"
            ]
            # 最新游戏（用于首页 latestUpdateGames）
            latest_slugs = guide_slugs[-3:] if len(guide_slugs) >= 3 else guide_slugs
            
            # 生成卡片 HTML
            def gen_card(slug):
                name = slug_to_name(slug.replace('-guide', ''))
                return f'<a href="/guides/{slug}" class="game-card-static">{name}</a>'
            
            # 更新 index.html
            index_path = os.path.join(REPO_DIR, "index.html")
            with open(index_path, "r") as f:
                index_html = f.read()
            
            # 替换 #popularGames（兼容注释占位符和已有链接两种情况）
            popular_cards = '\n'.join(gen_card(s) for s in popular_slugs)
            index_html = re.sub(
                r'<div class="game-grid" id="popularGames">[\s\S]*?</div>',
                f'<div class="game-grid" id="popularGames">\n{popular_cards}\n</div>',
                index_html, count=1
            )
            # 替换 #latestUpdateGames
            latest_cards = '\n'.join(gen_card(s) for s in latest_slugs)
            index_html = re.sub(
                r'<div class="game-grid" id="latestUpdateGames">[\s\S]*?</div>',
                f'<div class="game-grid" id="latestUpdateGames">\n{latest_cards}\n</div>',
                index_html, count=1
            )
            with open(index_path, "w") as f:
                f.write(index_html)
            print("  ✅ index.html 更新完成")
            
            # 更新 games.html
            games_path = os.path.join(REPO_DIR, "games.html")
            with open(games_path, "r") as f:
                games_html = f.read()
            
            # 替换 #allGames（兼容注释占位符和已有链接两种情况）
            all_cards = '\n'.join(gen_card(s) for s in guide_slugs)
            games_html = re.sub(
                r'<div class="game-grid" id="allGames">[\s\S]*?</div>',
                f'<div class="game-grid" id="allGames">\n{all_cards}\n</div>',
                games_html, count=1
            )
            # 替换 #allGuides
            all_links = '\n'.join(f'<a href="/guides/{s}">{slug_to_name(s.replace("-guide", ""))}</a>' for s in guide_slugs)
            games_html = re.sub(
                r'<div class="guide-list" id="allGuides">[\s\S]*?</div>',
                f'<div class="guide-list" id="allGuides">\n{all_links}\n</div>',
                games_html, count=1
            )
            with open(games_path, "w") as f:
                f.write(games_html)
            print("  ✅ games.html 更新完成")
            
        except Exception as e:
            print(f"  ⚠️ 静态链接更新失败（不影响攻略发布）: {e}")
            # 继续执行，不阻断流程

        # ============================================================
        # Step 10: Upload all files to GitHub via REST API (no git push)
        # ============================================================
        print("[步骤10] 通过 GitHub REST API 上传所有文件...")

        upload_errors = []
        last_commit_sha = ""

        # Helper: upload a single file via Contents API
        def upload_local_file(local_path, remote_path, commit_msg):
            nonlocal last_commit_sha
            if not os.path.exists(local_path):
                print(f"  ⚠️ 跳过 {remote_path}（本地文件不存在）")
                return None
            with open(local_path, "rb") as f:
                file_bytes = f.read()
            # Get current SHA (if file exists on remote)
            _, current_sha = github_file_get(remote_path, GITHUB_TOKEN)
            try:
                result = github_file_put(
                    remote_path, GITHUB_TOKEN, file_bytes,
                    sha=current_sha, message=commit_msg
                )
                commit_info = result.get("commit", {})
                sha = commit_info.get("sha", "")[:7]
                last_commit_sha = sha or last_commit_sha
                print(f"  ✅ {remote_path} ({len(file_bytes)} bytes, commit: {sha})")
                return result
            except Exception as e:
                err = str(e)[:200]
                upload_errors.append(f"{remote_path}: {err}")
                print(f"  ❌ {remote_path}: {err}")
                return None

        # 10a: Upload guide HTML
        print("  [10a] 上传攻略 HTML...")
        guide_local = f"{REPO_DIR}/guides/{game.slug}-guide.html"
        upload_local_file(guide_local, f"guides/{game.slug}-guide.html",
                         f"Add {game.name} guide")

        # 10b: Upload images (only existing ones)
        print("  [10b] 上传图片...")
        img_dir_local = f"{REPO_DIR}/images/games/{game.slug}"
        img_files = ["hero.jpg", "screenshot-1.jpg", "screenshot-2.jpg", "screenshot-3.jpg"]
        for img_name in img_files:
            img_local_path = os.path.join(img_dir_local, img_name)
            if os.path.exists(img_local_path):
                upload_local_file(
                    img_local_path,
                    f"images/games/{game.slug}/{img_name}",
                    f"Add {game.name} {img_name}"
                )

        # 10c: Upload updated main.js (with gamesData + guidesData)
        print("  [10c] 上传 main.js...")
        main_js_local = f"{REPO_DIR}/js/main.js"
        upload_local_file(main_js_local, "js/main.js",
                         f"Update main.js: add {game.name} guide")

        # 10d: Upload updated sitemap.xml
        print("  [10d] 上传 sitemap.xml...")
        sitemap_local = f"{REPO_DIR}/sitemap.xml"
        upload_local_file(sitemap_local, "sitemap.xml",
                         f"Update sitemap: add {game.slug}-guide")

        # 10e: Upload index.html and games.html (if they were modified in 9.7)
        print("  [10e] 上传 index.html 和 games.html...")
        index_local = f"{REPO_DIR}/index.html"
        games_local = f"{REPO_DIR}/games.html"
        upload_local_file(index_local, "index.html",
                         f"Update index.html: latest guides")
        upload_local_file(games_local, "games.html",
                         f"Update games.html: all guides list")

        # Report results
        if upload_errors:
            print(f"  ⚠️ {len(upload_errors)} 个文件上传失败:")
            for err in upload_errors:
                print(f"    - {err}")
        else:
            print("  ✅ 所有文件上传成功")

        commit_hash = last_commit_sha or "api-push"
        print(f"[步骤10] ✅ REST API 上传完成 (最新 commit: {commit_hash})")

        # ============================================================
        # Step 11: Build result and submit
        # ============================================================
        print("[步骤11] 构建返回结果...")
        guide_url = f"{SITE_BASE}/guides/{game.slug}-guide"

        # Generate Pinterest caption
        tag_hashtags = " ".join(f"#{t.lower().replace(' ', '')}" for t in game.tags[:3])
        pinterest_caption = (
            f"{game.name.upper()} COMPLETE GUIDE {game.icon}\n\n"
            f"{game.description}\n\n"
            f"\U0001f3af Tips & Strategies\n"
            f"\U0001f3af Advanced Techniques\n"
            f"\U0001f3af Pro Tips\n\n"
            f"Link in bio \U0001f446\n"
            f"{guide_url}\n\n"
            f"#{game.slug.replace('-', '')} #iogame #browsergame {tag_hashtags}"
        )

        total_downloaded = downloaded + (1 if hero_from_og else 0)
        result_data = {
            "status": "success",
            "game_name": game.name,
            "game_slug": game.slug,
            "game_icon": game.icon,
            "guide_url": guide_url,
            "commit_hash": commit_hash,
            "pinterest_caption": pinterest_caption,
            "images_downloaded": total_downloaded,
            "images_total": 4,
            "missing_images": missing_images,
            "hero_from_og": bool(hero_from_og)
        }

        # Build message
        og_status = "✅ og:image" if hero_from_og else "❌ og:image"
        message = (
            f"✅ {game.name} 攻略已生成并推送\n\n"
            f"🎮 游戏: {game.name} ({game.slug})\n"
            f"🔗 攻略: {guide_url}\n"
            f"📦 Commit: {commit_hash}\n"
            f"🖼️ 图片: {total_downloaded}/4 张下载 ({og_status})"
        )

        # Add MISSING_IMAGES report if any images are missing
        if missing_images:
            missing_str = ",".join(missing_images)
            message += f"\n\nMISSING_IMAGES: {game.name}|{missing_str}"
            # 如果 hero 缺失，明确提示 AI 生成并给出正确 GitHub 路径
            if "hero" in missing_images:
                hero_github_path = f"images/games/{game.slug}/hero.jpg"
                message += f"|hero_path={hero_github_path}"
                message += f"\n⚠️ hero.jpg 缺失，请使用 image_generate 工具生成：游戏名：{game.name}，风格：游戏宣传海报，竖版"
                message += f"\n📥 hero 正确 GitHub 路径: {hero_github_path}"
            message += f"\n（需要主 agent 补生成缺失图片）"

        message += f"\n📝 Pinterest: {pinterest_caption[:100]}..."

        actual_mode = result_mode if result_mode != "auto" else "notify"
        await sdk.submit_result(
            result_mode=actual_mode,
            status="success",
            message=message,
            data=result_data
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        await sdk.submit_result(
            result_mode="notify",
            status="error",
            message=f"每日攻略生成失败: {e}"
        )


if __name__ == "__main__":
    asyncio.run(main())
