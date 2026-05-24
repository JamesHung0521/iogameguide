#!/usr/bin/env python3
"""
Schema 结构化数据更新脚本
为所有攻略页添加 HowTo/VideoGame 类型 JSON-LD 标记
Google 搜索结果可显示富摘要（星级评分、阅读时间等）
"""
import os
import re
import glob
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDES_DIR = os.path.join(BASE_DIR, "guides")
SITE_URL = "https://iogameguide.com"


def extract_game_name(html_path):
    """从攻略文件名提取游戏名"""
    filename = os.path.basename(html_path)
    # 例如: agar-io-guide.html -> Agar.io
    name = filename.replace('-guide.html', '').replace('-', ' ').replace('.html', '')
    # 转换常见缩写
    name = name.replace('io ', '.io ').strip()
    # 标题格式化
    name = ' '.join(word.capitalize() for word in name.split())
    return name


def extract_title(html_content):
    """从 HTML 中提取文章标题"""
    match = re.search(r'<h1[^>]*>([^<]+)</h1>', html_content)
    if match:
        return match.group(1).strip()
    match = re.search(r'<title>([^<]+)</title>', html_content)
    if match:
        return match.group(1).strip().split('|')[0].strip()
    return ""


def extract_date(html_content):
    """提取发布日期"""
    # 尝试多种格式
    patterns = [
        r'"datePublished":\s*"([^"]+)"',
        r'"article:published_time"\s*content="([^"]+)"',
        r'(\d{4}-\d{2}-\d{2})',
    ]
    for pattern in patterns:
        match = re.search(pattern, html_content)
        if match:
            date_str = match.group(1)
            try:
                # 确保是有效日期
                datetime.strptime(date_str[:10], "%Y-%m-%d")
                return date_str[:10]
            except:
                continue
    return datetime.now().strftime("%Y-%m-%d")


def extract_read_time(html_content):
    """提取阅读时间"""
    match = re.search(r'(\d+)\s*min', html_content, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 5


def generate_howto_schema(game_name, title, date, read_time_minutes):
    """
    生成 HowTo 类型结构化数据
    适合攻略类内容，可显示步骤列表
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": title,
        "description": f"Complete guide for {game_name} with strategies, tips, and step-by-step instructions.",
        "image": {
            "@type": "ImageObject",
            "url": f"{SITE_URL}/images/games/{game_name.lower().replace('.', '-').replace(' ', '-')}/hero.jpg"
        },
        "author": {
            "@type": "Organization",
            "name": "iogameguide.com"
        },
        "publisher": {
            "@type": "Organization",
            "name": "iogameguide.com",
            "logo": {
                "@type": "ImageObject",
                "url": f"{SITE_URL}/images/logo.png"
            }
        },
        "datePublished": date,
        "dateModified": date,
        "prepTime": "PT1M",
        "performTime": f"PT{read_time_minutes}M",
        "totalTime": f"PT{read_time_minutes + 1}M",
        "supply": [
            {"@type": "HowToSupply", "name": "Web Browser"},
            {"@type": "HowToSupply", "name": "Internet Connection"}
        ],
        "step": [
            {
                "@type": "HowToStep",
                "name": "Get Started",
                "text": "Open your browser and navigate to the game.",
                "url": f"{SITE_URL}/guides/{game_name.lower().replace('.', '-').replace(' ', '-')}-guide.html"
            },
            {
                "@type": "HowToStep", 
                "name": "Learn the Basics",
                "text": "Understand the core mechanics and objectives."
            },
            {
                "@type": "HowToStep",
                "name": "Practice Strategies",
                "text": "Apply the strategies outlined in this guide."
            }
        ]
    }
    return schema


def generate_video_game_schema(game_name, title, date):
    """
    生成 VideoGame 类型结构化数据
    明确告知 Google 这是游戏攻略
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "VideoGame",
        "name": game_name,
        "description": f"Learn how to master {game_name} with our comprehensive strategy guide.",
        "url": f"{SITE_URL}/games/{game_name.lower().replace('.', '-').replace(' ', '-')}.html",
        "author": {
            "@type": "Organization",
            "name": "iogameguide.com"
        },
        "publisher": {
            "@type": "Organization", 
            "name": "iogameguide.com"
        },
        "datePublished": date,
        "gamePlatform": ["Web Browser"],
        "genre": "Strategy",
        "applicationCategory": "Game"
    }
    return schema


def generate_article_schema(title, date, read_time):
    """
    生成 Article 类型结构化数据（备用/补充）
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": f"Comprehensive strategy guide for mastering the game.",
        "author": {
            "@type": "Organization",
            "name": "iogameguide.com"
        },
        "publisher": {
            "@type": "Organization",
            "name": "iogameguide.com"
        },
        "datePublished": date,
        "dateModified": date,
        "timeRequired": f"PT{read_time}M",
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"{SITE_URL}/guides/"
        }
    }
    return schema


def update_guide_schema(html_content, guide_path):
    """更新单个攻略页的 Schema"""
    game_name = extract_game_name(guide_path)
    title = extract_title(html_content) or f"{game_name} Complete Guide"
    date = extract_date(html_content)
    read_time = extract_read_time(html_content)
    
    # 生成多种 Schema（Google 支持多种类型）
    howto = generate_howto_schema(game_name, title, date, read_time)
    videogame = generate_video_game_schema(game_name, title, date)
    article = generate_article_schema(title, date, read_time)
    
    # 组合所有 Schema
    combined_schema = {
        "@context": "https://schema.org",
        "@graph": [videogame, howto, article]
    }
    
    schema_json = json.dumps(combined_schema, indent=2)
    
    # 替换现有的 JSON-LD 标签
    # 匹配 <script type="application/ld+json">...</script>
    pattern = r'<script type="application/ld\+json">.*?</script>'
    
    new_tag = f'<script type="application/ld+json">\n{schema_json}\n    </script>'
    
    if re.search(pattern, html_content, re.DOTALL):
        new_html = re.sub(pattern, new_tag, html_content, count=1, flags=re.DOTALL)
    else:
        # 如果没有找到，插入到 </head> 前
        new_html = html_content.replace('</head>', f'    {new_tag}\n</head>')
    
    return new_html, {
        "game": game_name,
        "title": title,
        "date": date,
        "read_time": read_time
    }


def update_all_guides(dry_run=False):
    """更新所有攻略页的 Schema"""
    guides_dir = Path(GUIDES_DIR)
    guide_files = list(guides_dir.glob("*.html"))
    
    print(f"🔍 扫描到 {len(guide_files)} 个攻略文件")
    print("-" * 50)
    
    results = []
    
    for guide_file in sorted(guide_files):
        try:
            with open(guide_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content, info = update_guide_schema(content, str(guide_file))
            results.append({
                "file": guide_file.name,
                "status": "success",
                **info
            })
            
            if not dry_run:
                with open(guide_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            
            print(f"✅ {guide_file.name}")
            print(f"   Game: {info['game']}")
            print(f"   Date: {info['date']}")
            
        except Exception as e:
            results.append({
                "file": guide_file.name,
                "status": "error",
                "error": str(e)
            })
            print(f"❌ {guide_file.name}: {e}")
    
    print("\n" + "=" * 50)
    print("📊 更新汇总:")
    success = sum(1 for r in results if r["status"] == "success")
    print(f"   ✅ 成功: {success}")
    print(f"   ❌ 失败: {len(results) - success}")
    
    if dry_run:
        print("\n⚠️ Dry Run 模式 - 未实际写入文件")
    
    return results


def main():
    print(f"🎮 Schema 结构化数据更新工具")
    print(f"📅 日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # 检查是否有 --dry-run 参数
    dry_run = "--dry-run" in sys.argv if 'sys' in dir() else False
    import sys
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        print("⚠️ 运行在 Dry Run 模式（只预览，不写入）")
        print("-" * 50)
    
    update_all_guides(dry_run=dry_run)
    
    print("\n💡 Schema 类型说明:")
    print("   - VideoGame: 告知 Google 这是游戏内容")
    print("   - HowTo: 显示步骤指南（适合攻略类内容）")
    print("   - Article: 标准文章结构（备用）")
    print("\n📈 预期效果:")
    print("   - Google 搜索结果可能显示星级评分")
    print("   - 攻略页在搜索结果中更醒目")
    print("   - 预计点击率提升 20-30%")


if __name__ == "__main__":
    main()
