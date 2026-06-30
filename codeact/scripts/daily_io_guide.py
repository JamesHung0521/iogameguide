#!/usr/bin/env python3
"""
Daily .io Game Guide Generator (Hybrid Mode)
- Fetches existing games from GitHub main.js
- Searches for new popular .io games
- Generates complete guide HTML + screenshots
- Commits and pushes to GitHub
- Returns result for main agent to generate Pinterest images
- Reports MISSING_IMAGES if not enough real screenshots found
"""

import asyncio
import sys
import re
import json
import os
import subprocess
import requests
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
    <meta name="author" content="iogameguide.com">
    <meta name="robots" content="index, follow">
    <meta property="og:type" content="article">
    <meta property="og:title" content="__GAME_NAME__ Complete Guide: Tips, Tricks & Strategies">
    <meta property="og:description" content="Master __GAME_NAME__ with our complete guide covering gameplay mechanics, advanced strategies, and pro tips.">
    <meta property="og:url" content="https://iogameguide.com/guides/__GAME_SLUG__-guide">
    <meta property="article:published_time" content="__DATE__">
    <meta property="article:modified_time" content="__DATE__">
    <link rel="canonical" href="https://iogameguide.com/guides/__GAME_SLUG__-guide">
    <link rel="stylesheet" href="../css/style.css">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1074835585646908" crossorigin="anonymous"></script>
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
                "author": {"@type": "Organization", "name": "iogameguide.com"},
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
                "author": {"@type": "Organization", "name": "iogameguide"},
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
                <p class="guide-meta"><span>Updated: __DATE__</span><span>&#8226;</span><span>__READING_TIME__ min read</span></p>
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
    """Replace __KEY__ placeholders with values."""
    result = template
    for key, value in kwargs.items():
        result = result.replace(f"__{key}__", str(value))
    return result


def escape_js_string(s: str) -> str:
    """Escape a string for use in a JavaScript single-quoted string literal."""
    return s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ")


def validate_guide_images(img_dir, game_name):
    """
    校验攻略图片质量，防止重复/低质图片被推送。
    返回 (passed: bool, errors: list[str], missing: list[str])
    missing: 缺失的图片文件名列表 (e.g. ["hero.jpg", "screenshot-1.jpg"])
    """
    required_files = ["hero.jpg", "screenshot-1.jpg", "screenshot-2.jpg", "screenshot-3.jpg"]
    min_size_kb = 50
    errors = []
    missing = []
    sizes = []

    for fname in required_files:
        fpath = os.path.join(img_dir, fname)
        # 检查文件是否存在
        if not os.path.exists(fpath):
            errors.append(f"缺失: {fname}")
            missing.append(fname)
            continue
        # 检查文件大小
        size_kb = os.path.getsize(fpath) / 1024
        sizes.append((fname, os.path.getsize(fpath)))
        if size_kb < min_size_kb:
            errors.append(f"{fname} 过小 ({size_kb:.1f}KB < {min_size_kb}KB)")
            missing.append(fname)

    # 检查是否有重复（任意两张图大小完全一样 → 可能是同一张图）
    for i in range(len(sizes)):
        for j in range(i + 1, len(sizes)):
            if sizes[i][1] == sizes[j][1]:
                errors.append(f"重复: {sizes[i][0]} 和 {sizes[j][0]} 大小完全相同 ({sizes[i][1]} bytes)")

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
        resp = requests.get(GITHUB_RAW_MAINJS, timeout=30)
        resp.raise_for_status()
        main_js_text = resp.text

        # Parse gamesData — extract all id values
        games_match = re.search(r'const gamesData\s*=\s*\[([\s\S]*?)\n\];', main_js_text)
        if not games_match:
            raise Exception("无法解析 gamesData，正则未匹配")

        existing_ids = set(re.findall(r"id:\s*['\"]([^'\"]+)['\"]", games_match.group(1)))
        print(f"[步骤1] 已有 {len(existing_ids)} 个游戏")

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

        # 3c: Use LLM to rank candidates by popularity and pick the best one
        # Take up to 15 candidates for LLM to rank
        top_candidates = candidates[:15]
        candidate_names = [name for name, slug in top_candidates]

        print(f"  候选游戏 (前15): {candidate_names}")

        ranking_result = await sdk.call_llm(
            messages=[{
                "role": "user",
                "content": f"""Rank these .io browser games by how well-known and popular they are.
Games: {json.dumps(candidate_names)}

Return ONLY the name of the MOST popular/well-known game from this list.
Consider: active player base, cultural recognition, Google search volume, YouTube content.
Just return the game name, nothing else."""
            }]
        )

        # Parse the LLM's pick
        picked_name = candidate_names[0]  # Default to first
        if isinstance(ranking_result, str):
            picked = ranking_result.strip()
            # Find matching candidate
            for name, slug in top_candidates:
                if name.lower() == picked.lower() or picked.lower() in name.lower():
                    picked_name = name
                    break
            else:
                # Try partial match
                for name, slug in top_candidates:
                    base = name.replace('.io', '').lower()
                    if base in picked.lower() or picked.lower().replace('.io', '') in base:
                        picked_name = name
                        break

        # Find the slug for the picked name
        selected_name = picked_name
        selected_slug = None
        for name, slug in top_candidates:
            if name == selected_name:
                selected_slug = slug
                break
        if not selected_slug:
            selected_name, selected_slug = candidates[0]
        print(f"  选择: {selected_name} ({selected_slug})")

        # Enrich the selected game with details using LLM
        game_info_result = await sdk.call_llm(
            messages=[{
                "role": "user",
                "content": f"""Provide details for the .io browser game "{selected_name}":
- icon: A single emoji that best represents this game
- icon_color: A hex color code that matches the game's theme (e.g., "#FF6B6B")
- difficulty: Integer 1-5 (1=very easy, 5=very hard)
- tags: Array of 2-3 English category tags
- description: One short sentence describing the game's core gameplay
- game_url: The game's official website URL

If you're not sure about the game, provide your best guess based on the name and common .io game patterns."""
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
            game.slug = selected_slug  # Ensure our slug is used
        else:
            game = GameCandidate(
                name=selected_name, slug=selected_slug, icon='🎮',
                icon_color='#6366F1', difficulty=3, tags=['Multiplayer', 'Browser'],
                description=f'Play {selected_name} online for free.',
                game_url=f'https://{selected_name.lower().replace(" ", "")}'
            )

        print(f"[步骤3] ✅ 选择游戏: {game.name} (slug: {game.slug}, difficulty: {game.difficulty})")

        # ============================================================
        # Step 4: Clone repo
        # ============================================================
        print("[步骤4] 克隆仓库...")
        subprocess.run(["rm", "-rf", REPO_DIR], check=False, capture_output=True)

        if github_token:
            auth_repo = GITHUB_REPO.replace("https://", f"https://{github_token}@")
        else:
            auth_repo = GITHUB_REPO

        clone_result = subprocess.run(
            ["git", "clone", "--depth", "1", auth_repo, REPO_DIR],
            capture_output=True, text=True, timeout=120
        )
        if clone_result.returncode != 0:
            raise Exception(f"Git clone 失败: {clone_result.stderr[:300]}")

        # Configure git
        subprocess.run(["git", "config", "user.name", "JamesHung0521"],
                        cwd=REPO_DIR, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "JamesHung0521@users.noreply.github.com"],
                        cwd=REPO_DIR, check=True, capture_output=True)

        print("[步骤4] ✅ 仓库克隆成功")

        # ============================================================
        # Step 5: Download game screenshots (search-based, no HTML parsing)
        # ============================================================
        print("[步骤5] 搜索并下载游戏截图...")
        img_dir = f"{REPO_DIR}/images/games/{game.slug}"
        os.makedirs(img_dir, exist_ok=True)

        image_names = ["hero.jpg", "screenshot-1.jpg", "screenshot-2.jpg", "screenshot-3.jpg"]
        downloaded = 0
        candidate_img_urls = []

        # 5a: Search for gameplay screenshots using image search
        print(f"  搜索图片: '{game.name} gameplay screenshot'")
        try:
            img_search_1 = await sdk.call_tool(
                "codeact_search_web",
                {"query": f"{game.name} gameplay screenshot", "engine": "image"},
                schema_version=SEARCH_VER
            )
            if img_search_1.get("is_success") and img_search_1.get("results"):
                for r in img_search_1["results"]:
                    url = r.get("url", "")
                    snippet = r.get("snippet", "")
                    # Extract image URLs from the result URL itself
                    if url and any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif']):
                        if url not in candidate_img_urls:
                            candidate_img_urls.append(url)
                    # Also extract image URLs from snippet text
                    snippet_urls = extract_image_urls_from_text(snippet)
                    for u in snippet_urls:
                        if u not in candidate_img_urls:
                            candidate_img_urls.append(u)
                print(f"    图片搜索1: 获得 {len(candidate_img_urls)} 个候选URL")
        except Exception as e:
            print(f"  图片搜索1失败: {e}")

        # 5b: If not enough, search with broader query
        if len(candidate_img_urls) < 4:
            print(f"  候选不足，扩展搜索: '{game.name} io game screenshot'")
            try:
                img_search_2 = await sdk.call_tool(
                    "codeact_search_web",
                    {"query": f"{game.name} io game screenshot", "engine": "image"},
                    schema_version=SEARCH_VER
                )
                if img_search_2.get("is_success") and img_search_2.get("results"):
                    for r in img_search_2["results"]:
                        url = r.get("url", "")
                        snippet = r.get("snippet", "")
                        if url and any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif']):
                            if url not in candidate_img_urls:
                                candidate_img_urls.append(url)
                        snippet_urls = extract_image_urls_from_text(snippet)
                        for u in snippet_urls:
                            if u not in candidate_img_urls:
                                candidate_img_urls.append(u)
                    print(f"    图片搜索2: 共 {len(candidate_img_urls)} 个候选URL")
            except Exception as e:
                print(f"  图片搜索2失败: {e}")

        # 5c: If still not enough, try visual search as additional source
        if len(candidate_img_urls) < 4:
            print(f"  候选仍不足，尝试视觉搜索: '{game.name} gameplay'")
            try:
                img_search_3 = await sdk.call_tool(
                    "codeact_search_web",
                    {"query": f"{game.name} gameplay", "engine": "visual"},
                    schema_version=SEARCH_VER
                )
                if img_search_3.get("is_success") and img_search_3.get("results"):
                    for r in img_search_3["results"]:
                        url = r.get("url", "")
                        snippet = r.get("snippet", "")
                        if url and any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif']):
                            if url not in candidate_img_urls:
                                candidate_img_urls.append(url)
                        snippet_urls = extract_image_urls_from_text(snippet)
                        for u in snippet_urls:
                            if u not in candidate_img_urls:
                                candidate_img_urls.append(u)
                    print(f"    视觉搜索: 共 {len(candidate_img_urls)} 个候选URL")
            except Exception as e:
                print(f"  视觉搜索失败: {e}")

        # 5d: If still not enough from image/visual search, try general search and extract URLs from snippets
        if len(candidate_img_urls) < 4:
            print(f"  候选仍不足，尝试通用搜索提取图片URL")
            try:
                general_search = await sdk.call_tool(
                    "codeact_search_web",
                    {"query": f"{game.name} gameplay screenshot images"},
                    schema_version=SEARCH_VER
                )
                if general_search.get("is_success") and general_search.get("results"):
                    for r in general_search["results"]:
                        snippet = r.get("snippet", "")
                        snippet_urls = extract_image_urls_from_text(snippet)
                        for u in snippet_urls:
                            if u not in candidate_img_urls:
                                candidate_img_urls.append(u)
                        # Also try the page URL itself — some search results may link to images
                        url = r.get("url", "")
                        if url and any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                            if url not in candidate_img_urls:
                                candidate_img_urls.append(url)
                    print(f"    通用搜索: 共 {len(candidate_img_urls)} 个候选URL")
            except Exception as e:
                print(f"  通用搜索失败: {e}")

        print(f"  总候选截图 URL: {len(candidate_img_urls)} 个")

        # 5e: Download images from candidate URLs
        # 区分 hero 和 screenshot 的质量要求：
        # - hero.jpg: >3KB 即可（Logo/宣传图/美化图都接受）
        # - screenshot-1/2/3: >30KB（必须是游戏实际画面截图，排除小图标和Logo）
        MIN_SIZE_HERO = 3000  # 3KB for hero
        MIN_SIZE_SCREENSHOT = 30000  # 30KB for screenshots (real gameplay)
        
        screenshot_downloaded = 0
        
        for img_url in candidate_img_urls:
            if downloaded >= 4:
                break
            try:
                img_resp = requests.get(
                    img_url, timeout=15, allow_redirects=True,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                )
                content_type = img_resp.headers.get("content-type", "")
                img_size = len(img_resp.content)
                is_not_html = b"<html" not in img_resp.content[:500].lower()
                
                # 判断当前要下载的是 hero 还是 screenshot
                current_fname = image_names[downloaded]
                is_hero = (downloaded == 0)
                min_size = MIN_SIZE_HERO if is_hero else MIN_SIZE_SCREENSHOT
                
                if img_resp.status_code == 200 and img_size > min_size and is_not_html:
                    with open(f"{img_dir}/{current_fname}", "wb") as f:
                        f.write(img_resp.content)
                    img_type = "hero" if is_hero else "screenshot"
                    print(f"  ✅ 下载: {current_fname} ({img_size} bytes, {img_type}, {content_type})")
                    downloaded += 1
                    if not is_hero:
                        screenshot_downloaded += 1
                else:
                    reason = "非图片" if not is_not_html else f"太小({img_size}b<{min_size}b)"
                    print(f"  跳过: {reason} ({content_type}, {img_size} bytes)")
            except Exception as e:
                print(f"  跳过: {e}")

        # Record which images are missing (no placeholder creation)
        missing_images = []
        for i in range(downloaded, 4):
            missing_images.append(image_names[i].replace('.jpg', ''))  # e.g. "screenshot-2", "screenshot-3"

        if downloaded < 4:
            print(f"  ⚠️ 已下载 {downloaded}/4 张，缺失: {missing_images}（不创建占位图，继续流程）")
        else:
            print(f"  ✅ 已下载全部 4/4 张图片")

        print(f"[步骤5] ✅ 图片完成 ({downloaded}/4 张下载)")

        # ============================================================
        # Step 6: Generate guide content via LLM
        # ============================================================
        print("[步骤6] 生成攻略内容...")

        # Fetch reference info about the game
        game_info = ""
        try:
            info_search = await sdk.call_tool(
                "codeact_search_web",
                {"query": f"{game.name} wiki guide tips strategies gameplay mechanics"},
                schema_version=SEARCH_VER
            )
            if info_search.get("is_success") and info_search.get("results"):
                top_url = info_search["results"][0].get("url", "")
                if top_url:
                    page = await sdk.call_tool(
                        "codeact_fetch_web",
                        {"url": top_url},
                        schema_version=FETCH_VER
                    )
                    if page.get("is_success"):
                        game_info = page.get("content", "")[:4000]
        except Exception as e:
            print(f"  信息获取失败: {e}")

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
6. conclusion (50-100 words): Summary and encouragement to try the game."""
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
            TIMESTAMP=timestamp
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
        guides_start = main_js_content.find("const guidesData")
        if guides_start == -1:
            raise Exception("找不到 guidesData")

        guides_closing = main_js_content.find("\n];", guides_start)
        if guides_closing == -1:
            raise Exception("找不到 guidesData 的 ];")

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

        # Smart comma handling for guidesData too
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

        new_url_entry = f"""  <url>
    <loc>{SITE_BASE}/guides/{game.slug}-guide</loc>
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
        else:
            print("[步骤9.5] ✅ 图片质量校验通过（4张图均>50KB且各不相同）")


        # ============================================================
        # Step 9.7: Update static links in index.html and games.html
        # ============================================================
        print("[步骤9.7] 更新首页和游戏页静态链接...")
        try:
            # 获取所有攻略列表（从 sitemap.xml）
            import base64
            api_headers = {"Authorization": f"token {github_token}", "Accept": "application/vnd.github.v3+json"}
            
            # 获取 sitemap.xml
            resp = requests.get(
                "https://api.github.com/repos/JamesHung0521/iogameguide/contents/sitemap.xml",
                headers=api_headers, timeout=30
            )
            sitemap_content = base64.b64decode(resp.json()['content']).decode('utf-8')
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
            
            # 替换 #popularGames
            popular_cards = '\n'.join(gen_card(s) for s in popular_slugs)
            index_html = re.sub(
                r'<div class="game-grid" id="popularGames">\s*<!--.*?-->\s*</div>',
                f'<div class="game-grid" id="popularGames">\n{popular_cards}\n</div>',
                index_html, flags=re.DOTALL
            )
            # 替换 #latestUpdateGames
            latest_cards = '\n'.join(gen_card(s) for s in latest_slugs)
            index_html = re.sub(
                r'<div class="game-grid" id="latestUpdateGames">\s*<!--.*?-->\s*</div>',
                f'<div class="game-grid" id="latestUpdateGames">\n{latest_cards}\n</div>',
                index_html, flags=re.DOTALL
            )
            with open(index_path, "w") as f:
                f.write(index_html)
            print("  ✅ index.html 更新完成")
            
            # 更新 games.html
            games_path = os.path.join(REPO_DIR, "games.html")
            with open(games_path, "r") as f:
                games_html = f.read()
            
            # 替换 #allGames
            all_cards = '\n'.join(gen_card(s) for s in guide_slugs)
            games_html = re.sub(
                r'<div class="game-grid" id="allGames">\s*<!--.*?-->\s*</div>',
                f'<div class="game-grid" id="allGames">\n{all_cards}\n</div>',
                games_html, flags=re.DOTALL
            )
            # 替换 #allGuides
            all_links = '\n'.join(f'<a href="/guides/{s}">{slug_to_name(s.replace("-guide", ""))}</a>' for s in guide_slugs)
            games_html = re.sub(
                r'<div class="guide-list" id="allGuides">\s*<!--.*?-->\s*</div>',
                f'<div class="guide-list" id="allGuides">\n{all_links}\n</div>',
                games_html, flags=re.DOTALL
            )
            with open(games_path, "w") as f:
                f.write(games_html)
            print("  ✅ games.html 更新完成")
            
        except Exception as e:
            print(f"  ⚠️ 静态链接更新失败（不影响攻略发布）: {e}")
            # 继续执行，不阻断流程

        # ============================================================
        # Step 10: Validate, commit, and push
        # ============================================================
        print("[步骤10] 验证数据完整性...")
        val_result = subprocess.run(
            ["node", "scripts/validate-guides-data.js"],
            cwd=REPO_DIR, capture_output=True, text=True, timeout=30
        )
        print(val_result.stdout)
        if val_result.returncode != 0:
            print(f"❌ 验证失败:\n{val_result.stderr}")
            raise Exception(f"数据验证失败: {val_result.stderr[:300]}")

        print("[步骤10] 数据验证通过 ✅")

        # Git add, commit, push
        subprocess.run(["git", "add", "."], cwd=REPO_DIR, check=True, capture_output=True)
        commit_result = subprocess.run(
            ["git", "commit", "-m", f"Add {game.name} guide"],
            cwd=REPO_DIR, capture_output=True, text=True
        )
        if commit_result.returncode != 0:
            raise Exception(f"Git commit 失败: {commit_result.stderr[:300]}")

        print("[步骤10] Git commit 成功，推送中...")
        push_result = subprocess.run(
            ["git", "push"],
            cwd=REPO_DIR, capture_output=True, text=True, timeout=60
        )
        if push_result.returncode != 0:
            raise Exception(f"Git push 失败: {push_result.stderr[:300]}")

        # Get commit hash
        hash_result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_DIR, capture_output=True, text=True
        )
        commit_hash = hash_result.stdout.strip()

        print(f"[步骤10] ✅ 推送成功 (commit: {commit_hash})")

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

        result_data = {
            "status": "success",
            "game_name": game.name,
            "game_slug": game.slug,
            "game_icon": game.icon,
            "guide_url": guide_url,
            "commit_hash": commit_hash,
            "pinterest_caption": pinterest_caption,
            "images_downloaded": downloaded,
            "images_total": 4,
            "missing_images": missing_images
        }

        # Build message
        message = (
            f"✅ {game.name} 攻略已生成并推送\n\n"
            f"🎮 游戏: {game.name} ({game.slug})\n"
            f"🔗 攻略: {guide_url}\n"
            f"📦 Commit: {commit_hash}\n"
            f"🖼️ 图片: {downloaded}/4 张下载"
        )

        # Add MISSING_IMAGES report if any images are missing
        if missing_images:
            missing_str = ",".join(missing_images)
            message += f"\n\nMISSING_IMAGES: {game.name}|{missing_str}"
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
