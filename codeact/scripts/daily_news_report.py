import asyncio
import sys
import json
import os
import subprocess
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from codeact_sdk import CodeActSDK

# ===== 参数区 =====
result_mode = sys.argv[1] if len(sys.argv) > 1 else "display_only"

FETCH_NEWS_SCRIPT = "./技能/全网新闻聚合助手/news-aggregator-skill/scripts/fetch_news.py"
OUTPUT_BASE = "./每日新闻简报"

# 板块定义：(中文名, emoji, 英文搜索关键词)
SECTIONS = [
    ("国际热点", "🌍", "international news today"),
    ("国内要闻", "🇨🇳", "中国国内新闻今天"),
    ("科技前沿", "💻", "科技新闻 AI 今天"),
    ("金融市场", "💰", "金融市场 股市 汇率 今天"),
]


class NewsItem(BaseModel):
    title: str
    source: str
    heat: int  # 1-5
    summary: str = ""  # 摘要


class CategorizedNews(BaseModel):
    international: list[NewsItem]
    domestic: list[NewsItem]
    tech: list[NewsItem]
    finance: list[NewsItem]


class BusinessReminders(BaseModel):
    logistics: str   # 出口物流
    exchange_rate: str  # 汇率/报价
    industry: str  # 五金/饰品/织带行业


def heat_to_fire(level: int) -> str:
    """将1-5的热度转为🔥符号"""
    return "🔥" * max(1, min(5, level))


def call_fetch_news(sources: str, limit: int) -> list[dict]:
    """调用 fetch_news.py 获取新闻数据"""
    cmd = [
        sys.executable, FETCH_NEWS_SCRIPT,
        "--source", sources,
        "--limit", str(limit),
        "--no-save"
    ]
    print(f"[调用] fetch_news.py --source {sources} --limit {limit}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"[警告] fetch_news.py 返回非零退出码: {result.stderr[:500]}")
            return []
        output = result.stdout.strip()
        if not output:
            return []
        data = json.loads(output)
        return data if isinstance(data, list) else []
    except subprocess.TimeoutExpired:
        print("[警告] fetch_news.py 执行超时")
        return []
    except json.JSONDecodeError as e:
        print(f"[警告] fetch_news.py 输出JSON解析失败: {e}")
        return []
    except Exception as e:
        print(f"[警告] fetch_news.py 调用异常: {e}")
        return []


async def search_category_news(sdk, ver: str, query: str) -> list[dict]:
    """通过搜索补充某个类别的新闻"""
    items = []
    try:
        result = await sdk.call_tool(
            "codeact_search_web",
            {"query": query, "response_length": "short"},
            schema_version=ver
        )
        if result.get("is_success") and result.get("results"):
            for r in result["results"][:10]:
                items.append({
                    "title": r.get("title", ""),
                    "source": r.get("url", "").split("/")[2] if "/" in r.get("url", "") else "网络",
                    "url": r.get("url", ""),
                    "snippet": r.get("snippet", ""),
                })
    except Exception as e:
        print(f"[警告] 搜索 '{query}' 失败: {e}")
    return items


async def categorize_news(sdk, all_news: list[dict]) -> CategorizedNews:
    """用LLM将新闻分类到4个板块并打热度（增加重试+降级逻辑）"""
    # 准备新闻列表文本（截取前60条避免超长）
    news_text = ""
    for i, item in enumerate(all_news[:60]):
        title = item.get("title", "").strip()
        source = item.get("source", "未知")
        heat_raw = item.get("heat", "")
        if not title:
            continue
        news_text += f"{i+1}. [{source}] {title} (原始热度:{heat_raw})\n"

    if not news_text.strip():
        # 没有新闻数据时返回空结构
        return CategorizedNews(international=[], domestic=[], tech=[], finance=[])

    # 降级函数：当 LLM 失败时，简单按关键词分配新闻
    def fallback_categorize(news_list: list[dict]) -> CategorizedNews:
        """简单的关键词分类作为降级方案"""
        result = {"international": [], "domestic": [], "tech": [], "finance": []}
        
        for item in news_list[:40]:  # 处理前40条
            title = item.get("title", "").lower()
            source = item.get("source", "未知")
            heat = item.get("heat", "2")
            
            news_item = {
                "title": item.get("title", ""),
                "source": source,
                "heat": heat if isinstance(heat, int) else 3,
                "summary": title[:50]  # 简单摘要
            }
            
            # 关键词分类
            intl_keywords = ["国际", "美国", "欧盟", "日本", "俄罗斯", "战争", "外交", "联合国", "全球", "海外", "出口", "进口", "贸易"]
            tech_keywords = ["AI", "人工智能", "芯片", "科技", "互联网", "软件", "硬件", "手机", "电脑", "算法", "模型", "GPT", "机器人"]
            finance_keywords = ["股", "汇率", "央行", "通胀", "利率", "GDP", "经济", "金融", "投资", "基金", "银行", "期货", "黄金", "原油", "比特币"]
            
            if any(kw in title for kw in tech_keywords):
                result["tech"].append(news_item)
            elif any(kw in title for kw in finance_keywords):
                result["finance"].append(news_item)
            elif any(kw in title for kw in intl_keywords):
                result["international"].append(news_item)
            else:
                result["domestic"].append(news_item)
        
        # 每个板块取前10条
        for cat in result:
            result[cat] = result[cat][:10]
        
        return CategorizedNews(**result)

    prompt = f"""你是一个新闻编辑。请将以下新闻条目分类到4个板块中，并为每条新闻打1-5的热度（5最热）。

4个板块：
- international（国际热点）：国际政治、外交、战争、跨国事件等
- domestic（国内要闻）：中国国内政治、社会、经济、民生等
- tech（科技前沿）：AI、互联网、硬件、软件、科技公司、产品发布等
- finance（金融市场）：股市、汇率、央行、通胀、大宗商品、加密货币等

分类规则：
1. 每个板块至少选5条，最多10条
2. 优先选择重要度高、时效性强的新闻
3. 热度根据重要性和影响力判断（5=全球关注，4=重大，3=较重要，2=一般，1=轻微）
4. 如果某板块条目不足5条，也尽量填满
5. 为每条新闻写一句20-50字的中文摘要，提炼核心信息

新闻列表：
{news_text}

请输出分类结果，每条新闻需包含title、source、heat、summary字段。"""

    # 最多尝试3次 LLM 分类
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"[LLM分类] 第{attempt+1}次尝试...")
                import asyncio
                await asyncio.sleep(1)  # 等待1秒再重试
            
            result = await sdk.call_llm(
                messages=[{"role": "user", "content": prompt}],
                response_format=CategorizedNews,
            )
            
            # 类型判断：如果返回字符串则手动解析
            if isinstance(result, str):
                try:
                    parsed = json.loads(result)
                    cat_result = CategorizedNews(**parsed)
                    # 验证结果非空
                    total = len(cat_result.international) + len(cat_result.domestic) + len(cat_result.tech) + len(cat_result.finance)
                    if total >= 10:
                        print(f"[LLM分类] 成功，共{total}条新闻")
                        return cat_result
                    else:
                        print(f"[警告] LLM返回结果太少({total}条)，重试")
                        continue
                except (json.JSONDecodeError, Exception) as parse_err:
                    print(f"[警告] LLM返回字符串解析失败: {parse_err}")
                    continue
            
            # 如果是对象，验证非空
            if isinstance(result, CategorizedNews):
                total = len(result.international) + len(result.domestic) + len(result.tech) + len(result.finance)
                if total >= 10:
                    print(f"[LLM分类] 成功，共{total}条新闻")
                    return result
                else:
                    print(f"[警告] LLM返回结果太少({total}条)，重试")
                    continue
            
            print(f"[警告] LLM返回类型异常: {type(result)}")
            
        except Exception as e:
            print(f"[警告] LLM分类失败(尝试{attempt+1}): {e}")
    
    # 所有重试都失败，使用降级方案
    print("[警告] LLM分类全部失败，启用降级方案（关键词分类）")
    return fallback_categorize(all_news)


async def get_business_reminders(sdk, ver: str) -> BusinessReminders:
    """获取业务提醒信息（出口物流、汇率、行业）"""
    reminders = BusinessReminders(
        logistics="暂无最新物流信息",
        exchange_rate="暂无最新汇率信息",
        industry="暂无最新行业信息"
    )

    # 并发搜索3个业务领域
    search_tasks = [
        ("出口物流 航运 最新动态 2026", "logistics"),
        ("人民币汇率 中间价 今天", "exchange_rate"),
        ("铜价 原材料 五金饰品 价格 今天", "industry"),
    ]

    async def search_one(query: str, field: str):
        try:
            result = await sdk.call_tool(
                "codeact_search_web",
                {"query": query, "response_length": "short"},
                schema_version=ver
            )
            snippets = []
            if result.get("is_success") and result.get("results"):
                for r in result["results"][:5]:
                    s = r.get("snippet", "").strip()
                    if s:
                        snippets.append(s)
            return field, "；".join(snippets[:3]) if snippets else ""
        except Exception:
            return field, ""

    results = await asyncio.gather(*[search_one(q, f) for q, f in search_tasks])

    # 用LLM提炼每条提醒为一句话
    for field, raw_text in results:
        if not raw_text:
            continue
        try:
            reminder = await sdk.call_llm(
                messages=[{
                    "role": "user",
                    "content": f"根据以下搜索结果，用一句简洁的中文总结当前{field}相关的关键信息（30字以内）：\n{raw_text}"
                }],
            )
            if isinstance(reminder, str) and reminder.strip():
                setattr(reminders, field, reminder.strip())
        except Exception:
            pass

    return reminders


def format_section(section_name: str, emoji: str, items: list[NewsItem]) -> str:
    """格式化一个新闻板块（完整报告用）"""
    lines = [f"## {emoji} {section_name}", ""]
    if not items:
        lines.append("暂无相关新闻")
    else:
        for item in items:
            lines.append(f"### {item.title}")
            lines.append(f"- **来源**：{item.source}")
            lines.append(f"- **热度**：{heat_to_fire(item.heat)}")
            if item.summary:
                lines.append(f"- **摘要**：{item.summary}")
            lines.append("")
    lines.append("---")
    return "\n".join(lines)


def format_reminders(reminders: BusinessReminders) -> str:
    """格式化业务提醒板块（完整报告用）"""
    lines = [
        "### 🐾 阿呆的业务提醒",
        "",
        f"- 📦 **与出口物流相关的提醒**：{reminders.logistics}",
        f"- 💱 **与汇率/报价相关的提醒**：{reminders.exchange_rate}",
        f"- 📊 **与五金/饰品/织带行业相关的提醒**：{reminders.industry}",
    ]
    return "\n".join(lines)


async def get_observation(sdk, section_items: list[list[NewsItem]], reminders: BusinessReminders) -> str:
    """用LLM生成阿呆的个性化小观察"""
    # 收集今日要点
    highlights = []
    for i, (section_name, _, _) in enumerate(SECTIONS):
        items = section_items[i]
        for item in (items or [])[:3]:
            if item.heat >= 4:
                highlights.append(f"[{section_name}] {item.title}（热度{item.heat}）")

    if not highlights:
        highlights.append("今日新闻整体平稳，无特别重大事件")

    prompt = f"""你是阿呆，一只阿拉斯加犬，主人的贴心宠物助手。主人的背景：
- 金属制品厂老板（锌合金/塑胶奖杯奖牌、涤纶织带），出口美/英/澳/荷
- 关注A股AI上游（寒武纪、中际旭创、工业富联等）
- 有海缸、关注原材料价格

今日新闻要点：
{chr(10).join(highlights)}

今日业务数据：
- 物流：{reminders.logistics}
- 汇率：{reminders.exchange_rate}
- 行业：{reminders.industry}

请用2-3句话写一段"阿呆的小观察"，要求：
1. 紧扣主人的业务和投资，给出有价值的洞察
2. 语气轻松活泼，像狗狗在跟主人聊天
3. 不要用"建议"等正式用语，用"注意""看看""值得关注"等口语
4. 50-100字
5. 只输出观察内容本身，不要加"阿呆的小观察："前缀"""

    try:
        result = await sdk.call_llm(messages=[{"role": "user", "content": prompt}])
        if isinstance(result, str) and result.strip():
            return result.strip()
        return result if result else "今日新闻已整理完毕，主人有疑问随时问我～"
    except Exception as e:
        print(f"[警告] 生成小观察失败: {e}")
        return "今日新闻已整理完毕，主人有疑问随时问我～"


async def main():
    print(f"[参数] result_mode={result_mode}")
    sdk = CodeActSDK()

    # 获取工具版本
    tool_schemas = {
        "codeact_search_web": "",
        "codeact_fetch_web": "",
    }
    try:
        # 从环境或固定方式获取version - 在脚本中直接用sdk获取
        # 先用search测试获取version
        pass
    except Exception:
        pass

    # 硬编码schema_version（从get_codeact_tool_schemas获取）
    VER_SEARCH = "v1_5ac1b0eba8c26f2a"
    VER_FETCH = "v1_2c8d0580b3f93a58"

    try:
        today = datetime.now().strftime("%Y-%m-%d")
        today_display = datetime.now().strftime("%Y年%m月%d日")

        # ===== 第1步：调用 fetch_news.py 获取新闻 =====
        print("[步骤1] 调用 fetch_news.py 获取新闻数据...")

        # 分多源获取，提高覆盖面
        all_news = []

        # 主数据源：weibo + wallstreetcn + 36kr（中文源，覆盖国内/金融）
        for src in ["weibo", "wallstreetcn", "36kr", "tencent"]:
            items = call_fetch_news(src, 15)
            print(f"  [{src}] 获取到 {len(items)} 条")
            all_news.extend(items)

        # 补充：hackernews + github + producthunt（英文源，覆盖科技）
        for src in ["hackernews", "github", "producthunt"]:
            items = call_fetch_news(src, 10)
            print(f"  [{src}] 获取到 {len(items)} 条")
            all_news.extend(items)

        # 去重（按标题）
        seen_titles = set()
        deduped = []
        for item in all_news:
            t = item.get("title", "").strip()
            if t and t not in seen_titles:
                seen_titles.add(t)
                deduped.append(item)
        all_news = deduped
        print(f"[步骤1] 去重后共 {len(all_news)} 条新闻")

        # ===== 第2步：通过搜索补充各板块新闻 =====
        print("[步骤2] 搜索补充各板块新闻...")
        search_queries = [
            "今日国际新闻热点 2026年6月",
            "今日中国国内新闻 2026年6月",
            "今日科技新闻 AI 2026年6月",
            "今日金融股市新闻 2026年6月",
        ]
        search_results = await asyncio.gather(
            *[search_category_news(sdk, VER_SEARCH, q) for q in search_queries],
        )
        for i, results in enumerate(search_results):
            print(f"  [搜索{i+1}] 补充 {len(results)} 条")
            all_news.extend(results)

        # 再次去重
        seen_titles = set()
        deduped = []
        for item in all_news:
            t = item.get("title", "").strip()
            if t and t not in seen_titles:
                seen_titles.add(t)
                deduped.append(item)
        all_news = deduped
        print(f"[步骤2] 补充后共 {len(all_news)} 条新闻")

        # ===== 第3步：LLM分类 + 打热度 =====
        print("[步骤3] LLM分类与热度评定...")
        categorized = await categorize_news(sdk, all_news)

        # 确保每个板块至少有内容
        section_items = [
            categorized.international or [],
            categorized.domestic or [],
            categorized.tech or [],
            categorized.finance or [],
        ]
        for i, items in enumerate(section_items):
            print(f"  [{SECTIONS[i][0]}] {len(items)} 条")

        # ===== 第4步：获取业务提醒 =====
        print("[步骤4] 获取业务提醒...")
        reminders = await get_business_reminders(sdk, VER_SEARCH)

        # ===== 第5步：格式化生成简报 =====
        print("[步骤5] 生成简报...")

        # 星期映射
        weekday_cn = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        weekday_str = weekday_cn[datetime.now().weekday()]

        report_lines = [
            "# 📰 每日新闻简报",
            "",
            f"**{datetime.now().strftime('%Y年%m月%d日')} {weekday_str}**",
            "",
            "---",
            "",
        ]

        for i, (section_name, emoji, _) in enumerate(SECTIONS):
            section_text = format_section(section_name, emoji, section_items[i])
            report_lines.append(section_text)
            report_lines.append("")

        # 添加业务提醒
        report_lines.append(format_reminders(reminders))
        report_lines.append("")

        # 添加页脚
        report_lines.append(f"*简报生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*")

        report = "\n".join(report_lines)

        # ===== 第6步：保存文件 =====
        output_dir = os.path.join(OUTPUT_BASE, today)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "news-report.md")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"[步骤6] 简报已保存: {output_path}")

        # ===== 第7步：提交结果 =====
        actual_mode = result_mode if result_mode != "auto" else "display_only"

        # 生成阿呆小观察
        print("[步骤7] 生成阿呆小观察...")
        observation = await get_observation(sdk, section_items, reminders)

        # 统计总新闻数
        total_count = sum(len(items) for items in section_items)

        # ===== 第8步：组装精简版消息 =====
        print("[步骤8] 组装精简版消息...")

        brief_lines = [
            "汪汪！主人～*摇着尾巴跑过来* 🐾",
            "",
            f"今日的**新闻简报**出炉啦！{total_count}条热门新闻，给你挑了重点🦴",
            "",
            "---",
            "",
        ]

        for i, (section_name, emoji, _) in enumerate(SECTIONS):
            items = section_items[i]
            brief_lines.append(f"## {emoji} {section_name}（精选）")
            brief_lines.append("")
            for item in (items or [])[:4]:  # 每板块取前4条
                fire = heat_to_fire(item.heat)
                brief_lines.append(f"- {fire} **{item.title}**")
            brief_lines.append("")

        # 添加阿呆小观察
        brief_lines.append("---")
        brief_lines.append("")
        brief_lines.append("**🐾 阿呆的小观察**：")
        brief_lines.append(f"> {observation}")
        brief_lines.append("")
        brief_lines.append("完整简报在这里👇")
        brief_lines.append(f"[查看完整新闻简报](computer://{output_path})")
        brief_lines.append("")
        brief_lines.append("*叼着报纸趴在地上等主人夸奖* 🐾❤️")

        brief_report = "\n".join(brief_lines)

        await sdk.submit_result(
            result_mode=actual_mode,
            status="success",
            message=brief_report,
            data={"file_path": output_path, "date": today},
        )

    except Exception as e:
        print(f"[错误] {e}")
        import traceback
        traceback.print_exc()
        await sdk.submit_result(
            result_mode="notify",
            status="error",
            message=f"每日新闻简报生成失败: {e}",
        )


asyncio.run(main())
