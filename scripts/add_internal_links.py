#!/usr/bin/env python3
"""
内链互推脚本 - 为攻略页添加 Related Guides
自动从 main.js 的 guidesData 提取数据，生成相关攻略推荐
支持同游戏多攻略、跨游戏关联
"""
import os
import re
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDES_DIR = os.path.join(BASE_DIR, "guides")
MAIN_JS = os.path.join(BASE_DIR, "js", "main.js")
SITE_URL = "https://iogameguide.com"


def parse_guides_data():
    """解析 main.js 中的 guidesData"""
    with open(MAIN_JS, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 guidesData 数组
    match = re.search(r'const guidesData = \[(.*?)\];', content, re.DOTALL)
    if not match:
        print("❌ 无法找到 guidesData")
        return []
    
    # 简单解析 JSON-like 结构
    data_str = match.group(1)
    
    guides = []
    # 匹配每个攻略对象
    pattern = r"\{\s*id:\s*'([^']+)',\s*title:\s*'([^']+)',\s*game:\s*'([^']+)',\s*gameId:\s*'([^']+)',\s*date:\s*'([^']+)',\s*readTime:\s*'([^']+)',\s*excerpt:\s*'([^']+)',?"
    for m in re.finditer(pattern, data_str):
        guides.append({
            "id": m.group(1),
            "title": m.group(2),
            "game": m.group(3),
            "gameId": m.group(4),
            "date": m.group(5),
            "readTime": m.group(6),
            "excerpt": m.group(7)
        })
    
    return guides


def find_related_guides(current_guide, all_guides, limit=4):
    """
    找出与当前攻略相关的内容
    
    关联策略：
    1. 同一游戏的其他攻略（优先级最高）
    2. 同类型/同标签的游戏
    3. 最新发布的攻略
    """
    related = []
    current_game_id = current_guide.get("gameId", "")
    
    # 1. 同游戏攻略
    same_game = [g for g in all_guides 
                 if g["gameId"] == current_game_id and g["id"] != current_guide["id"]]
    related.extend(same_game[:2])  # 最多加2个
    
    # 2. 填充到 limit 个
    if len(related) < limit:
        # 添加最新攻略（排除自己）
        others = [g for g in all_guides 
                  if g["id"] != current_guide["id"] and g not in related]
        others.sort(key=lambda x: x["date"], reverse=True)
        related.extend(others[:limit - len(related)])
    
    return related[:limit]


def generate_related_html(related_guides):
    """生成 Related Guides HTML"""
    if not related_guides:
        return ""
    
    html_parts = [
        '            <!-- 相关攻略 -->',
        '            <section class="related-guides">',
        '                <div class="section-header">',
        '                    <h2 class="section-title">📚 Related Guides</h2>',
        '                </div>',
        '                <div class="guide-list">'
    ]
    
    for guide in related_guides:
        # 获取游戏图标（从 main.js 的 gamesData）
        icon = "🎮"  # 默认图标
        guide_url = f"https://iogameguide.com/guides/{guide['id']}.html"
        
        html_parts.append(f'''                    <a href="{guide_url}" class="guide-card">
                        <div class="guide-thumb">
                            <span style="font-size: 2rem;">{icon}</span>
                        </div>
                        <div class="guide-content">
                            <h3>{guide['title']}</h3>
                            <div class="guide-meta">
                                <span>🎮 {guide['game']}</span>
                                <span>⏱️ {guide['readTime']}</span>
                            </div>
                            <p class="guide-excerpt">{guide['excerpt']}</p>
                        </div>
                    </a>''')
    
    html_parts.extend([
        '                </div>',
        '            </section>'
    ])
    
    return '\n'.join(html_parts)


def update_guide_with_related(html_content, related_guides, guide_id):
    """更新攻略页，替换 Related Guides 部分"""
    related_html = generate_related_html(related_guides)
    
    # 检查是否有现有的 related-guides 部分
    if '<section class="related-guides">' in html_content:
        # 替换现有部分
        pattern = r'<section class="related-guides">.*?</section>\s*</div>\s*</main>'
        replacement = f'{related_html}\n            </div>\n        </main>'
        new_html = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
    elif '</article>' in html_content:
        # 在 </article> 后插入
        new_html = html_content.replace('</article>', f'</article>\n\n{related_html}')
    else:
        # 在 </div>（container）前插入
        new_html = html_content.replace(
            '        </div>\n    </main>',
            f'        {related_html}\n        </div>\n    </main>'
        )
    
    return new_html


def update_all_guides(dry_run=False):
    """更新所有攻略页的内链"""
    all_guides = parse_guides_data()
    
    print(f"🔍 解析到 {len(all_guides)} 个攻略")
    print("-" * 50)
    
    guides_dir = Path(GUIDES_DIR)
    guide_files = list(guides_dir.glob("*.html"))
    
    results = []
    
    for guide_file in sorted(guide_files):
        try:
            with open(guide_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 找出对应的攻略数据
            guide_id = guide_file.stem  # 文件名去掉 .html
            current_guide = None
            for g in all_guides:
                if guide_id in g["id"] or g["id"] in guide_id:
                    current_guide = g
                    break
            
            if not current_guide:
                # 尝试模糊匹配
                for g in all_guides:
                    if g["id"].replace("-guide", "") in guide_id.replace("-guide", ""):
                        current_guide = g
                        break
            
            if not current_guide:
                # 使用默认攻略数据
                current_guide = {
                    "id": guide_id,
                    "title": guide_file.stem.replace("-", " ").title(),
                    "game": "Game",
                    "gameId": guide_id.split("-")[0] if "-" in guide_id else guide_id
                }
            
            # 找出相关攻略
            related = find_related_guides(current_guide, all_guides, limit=4)
            
            # 更新 HTML
            new_content = update_guide_with_related(content, related, current_guide["id"])
            
            results.append({
                "file": guide_file.name,
                "status": "success",
                "related_count": len(related),
                "related": [g["title"][:40] for g in related]
            })
            
            if not dry_run:
                with open(guide_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            
            print(f"✅ {guide_file.name}")
            print(f"   📎 相关攻略: {len(related)} 个")
            
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
    
    # 统计关联情况
    avg_related = sum(r.get("related_count", 0) for r in results if r["status"] == "success") / max(success, 1)
    print(f"   📈 平均每篇攻略关联: {avg_related:.1f} 个")
    
    if dry_run:
        print("\n⚠️ Dry Run 模式 - 未实际写入文件")
    
    return results


def main():
    import sys
    
    print(f"🔗 内链互推更新工具")
    print(f"📅 日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        print("⚠️ 运行在 Dry Run 模式（只预览，不写入）")
        print("-" * 50)
    
    update_all_guides(dry_run=dry_run)
    
    print("\n💡 内链策略说明:")
    print("   1. 同游戏多攻略优先关联（如 Agar.io 基础+进阶攻略）")
    print("   2. 填充最新攻略确保每篇都有推荐")
    print("   3. 相关推荐可提升页面停留时间和 SEO")
    print("\n📈 预期效果:")
    print("   - 用户浏览路径更深（+30% 页面浏览量）")
    print("   - 搜索引擎爬虫抓取更深入")
    print("   - 页面权重均匀分布")


if __name__ == "__main__":
    main()
