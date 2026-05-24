#!/usr/bin/env python3
"""
IndexNow 提交脚本 - 自动通知 Bing 和 Yandex 搜索引擎
用法: python indexnow.py [URL或文件路径]
示例: 
  python indexnow.py                                    # 提交所有攻略页
  python indexnow.py https://iogameguide.com/guides/xxx  # 提交单个URL
  python indexnow.py guides/new-game-guide.html          # 提交新攻略文件
"""
import os
import sys
import glob
import hashlib
import urllib.request
import urllib.parse
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "https://iogameguide.com"

# IndexNow API 端点
INDEXNOW_ENDPOINTS = {
    "bing": "https://www.bing.com/indexnow",
    "yandex": "https://yandex.com/indexnow"
}

# 可选：如果有 Bing Webmaster API Key，可以添加
# BING_API_KEY = "your-bing-api-key"


def get_url_key(url):
    """生成 URL 的 SHA256 哈希作为 key（IndexNow 要求）"""
    return hashlib.sha256(url.encode()).hexdigest()[:32]


def submit_to_indexnow(urls):
    """
    提交 URLs 到 IndexNow 支持的搜索引擎
    
    Args:
        urls: URL 列表
    
    Returns:
        dict: 各搜索引擎的提交结果
    """
    if not urls:
        print("⚠️ 没有 URL 需要提交")
        return {}
    
    # 准备提交内容
    payload = {
        "host": "iogameguide.com",
        "key": get_url_key(SITE_URL),  # 使用网站首页 URL 生成的 key
        "keyLocation": f"{SITE_URL}/{get_url_key(SITE_URL)}.txt",
        "urlList": urls
    }
    
    import json
    payload_str = json.dumps(payload).encode('utf-8')
    
    results = {}
    
    for engine, endpoint in INDEXNOW_ENDPOINTS.items():
        try:
            req = urllib.request.Request(
                endpoint,
                data=payload_str,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'iogameguide-indexnow-submitter/1.0'
                },
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                status = response.status
                results[engine] = {
                    "status": "success" if status == 200 else status,
                    "urls_count": len(urls)
                }
                print(f"✅ {engine.upper()}: 提交成功 ({len(urls)} URLs)")
                
        except urllib.error.HTTPError as e:
            # 200 = 成功, 403 = key 不匹配, 422 = URL 不匹配
            if e.code == 403:
                results[engine] = {"status": "key_required", "detail": "需要验证 key 文件"}
                print(f"⚠️ {engine.upper()}: 需要验证 key 文件 (https://iogameguide.com/{get_url_key(SITE_URL)}.txt)")
            elif e.code == 422:
                results[engine] = {"status": "invalid_urls", "detail": str(e)}
                print(f"❌ {engine.upper()}: URL 格式无效")
            else:
                results[engine] = {"status": "error", "detail": str(e)}
                print(f"❌ {engine.upper()}: HTTP {e.code} - {e.reason}")
                
        except Exception as e:
            results[engine] = {"status": "error", "detail": str(e)}
            print(f"❌ {engine.upper()}: {e}")
    
    return results


def create_key_file():
    """
    创建 IndexNow key 文件（需要在网站根目录放置验证文件）
    这个文件需要主人手动上传到网站根目录
    """
    key = get_url_key(SITE_URL)
    key_content = key
    key_file = os.path.join(BASE_DIR, f"{key}.txt")
    
    with open(key_file, 'w') as f:
        f.write(key)
    
    print(f"\n📄 Key 文件已创建: {key_file}")
    print(f"📋 请上传此文件到: https://iogameguide.com/{key}.txt")
    print(f"🔑 Key 值: {key}")
    
    return key_file


def scan_guide_files():
    """扫描所有攻略文件"""
    guides_dir = os.path.join(BASE_DIR, "guides")
    if not os.path.exists(guides_dir):
        return []
    
    guide_files = glob.glob(os.path.join(guides_dir, "*.html"))
    urls = []
    for gf in guide_files:
        name = os.path.basename(gf)
        urls.append(f"{SITE_URL}/guides/{name}")
    
    return urls


def main():
    print(f"🚀 IndexNow 提交工具 - iogameguide.com")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    urls = []
    
    if len(sys.argv) > 1:
        # 命令行参数指定 URL
        arg = sys.argv[1]
        if arg.startswith('http'):
            urls = [arg]
        else:
            # 假设是本地文件路径
            if os.path.exists(arg):
                name = os.path.basename(arg)
                urls = [f"{SITE_URL}/{arg.replace(BASE_DIR + '/', '')}"]
            else:
                # 假设是 guides 目录下的文件
                urls = [f"{SITE_URL}/guides/{arg}"]
    else:
        # 扫描所有攻略文件
        urls = scan_guide_files()
        print(f"📂 扫描到 {len(urls)} 个攻略页面")
    
    if not urls:
        print("❌ 没有找到任何 URL")
        return
    
    print(f"\n📤 准备提交 {len(urls)} 个 URL:")
    for url in urls[:5]:
        print(f"   - {url}")
    if len(urls) > 5:
        print(f"   ... 还有 {len(urls) - 5} 个")
    
    print("\n" + "=" * 50)
    
    # 提交到搜索引擎
    results = submit_to_indexnow(urls)
    
    print("\n" + "=" * 50)
    print("📊 提交汇总:")
    print(f"   总 URL 数: {len(urls)}")
    for engine, result in results.items():
        status = "✅" if result.get("status") == "success" else "⚠️"
        print(f"   {status} {engine.upper()}: {result.get('status')}")
    
    # 提示创建 key 文件
    if any(r.get('status') in ['key_required', 'error'] for r in results.values()):
        print("\n💡 提示: 如需验证，请先运行 create_key_file() 并上传 key 文件")


if __name__ == "__main__":
    main()
