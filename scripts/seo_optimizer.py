#!/usr/bin/env python3
"""
iogameguide.com 流量优化一键脚本
整合 IndexNow + Schema + 内链三大优化
"""
import os
import sys
import subprocess
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_script(script_name, description):
    """运行脚本并报告结果"""
    script_path = os.path.join(SCRIPT_DIR, script_name)
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=120
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ 超时")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def main():
    print(f"""
╔══════════════════════════════════════════════════════════╗
║       🎮 iogameguide.com 流量优化工具                      ║
║                                                          ║
║   功能:                                                  ║
║   1️⃣  IndexNow - 即时通知 Bing/Yandex 搜索引擎            ║
║   2️⃣  Schema - JSON-LD 结构化数据 (HowTo/VideoGame)       ║
║   3️⃣  内链 - Related Guides 互推                         ║
║                                                          ║
║   预期效果:                                              ║
║   ✅ 搜索引擎秒级发现新内容                                ║
║   ✅ Google 富摘要，点击率+20-30%                         ║
║   ✅ 页面浏览量+30%，SEO权重提升                           ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # 1. IndexNow
    if "--skip-indexnow" not in sys.argv:
        results["indexnow"] = run_script("indexnow.py", "Step 1: IndexNow 即时提交")
    else:
        print("\n⏭️ 跳过 IndexNow")
    
    # 2. Schema 更新
    if "--skip-schema" not in sys.argv:
        results["schema"] = run_script("update_schema.py", "Step 2: Schema 结构化数据更新")
    else:
        print("\n⏭️ 跳过 Schema")
    
    # 3. 内链更新
    if "--skip-links" not in sys.argv:
        results["links"] = run_script("add_internal_links.py", "Step 3: 内链互推更新")
    else:
        print("\n⏭️ 跳过内链")
    
    # 汇总
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                    📊 执行汇总                           ║
╠══════════════════════════════════════════════════════════╣
║   IndexNow:     {'✅ 成功' if results.get('indexnow') else '❌ 失败':<10}                                  ║
║   Schema:       {'✅ 成功' if results.get('schema') else '❌ 失败':<10}                                  ║
║   内链:         {'✅ 成功' if results.get('links') else '❌ 失败':<10}                                  ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    print(f"⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 提示后续操作
    print("""
📋 后续操作:
   1. 验证更改: git diff
   2. 提交代码: git add . && git commit -m "SEO优化: IndexNow + Schema + 内链"
   3. 推送部署: git push
   4. 等待搜索引擎更新（通常 1-7 天）
   
💡 IndexNow Key 验证:
   首次运行需要创建并上传 key 文件到网站根目录
   运行: python indexnow.py --create-key
""")

if __name__ == "__main__":
    main()
