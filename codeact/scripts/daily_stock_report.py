#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日股票期货综合分析报告

品种覆盖:
- 港股: 美高梅中国(02282.HK), 金沙中国(01928.HK) — 休市时跳过
- A股AI上游: 工业富联/中际旭创/寒武纪/海光信息/新易盛/浪潮信息/胜宏科技/润泽科技 — 休市时跳过
- 期货: 黄金/铜/原油/锌/塑料 — 每日必出

数据源: 已有技能脚本(subprocess) + codeact_search_web(消息面) + codeact_llm(建议)
"""

import asyncio
import sys
import os
import json
import subprocess
import re
import time
from datetime import datetime, date, timedelta
from pathlib import Path
from codeact_sdk import CodeActSDK, ToolError, LLMError

# ==================== 配置 ====================

SKILL_DIR = os.path.abspath("./技能/股票个股分析/stock-analysis/scripts")
REPORT_BASE = os.path.abspath("./每日股票期货综合分析")

# 港股列表
HK_STOCKS = [
    {"code": "02282.HK", "name": "美高梅中国", "short": "02282"},
    {"code": "01928.HK", "name": "金沙中国", "short": "01928"},
]

# A股AI上游列表
A_STOCKS = [
    {"code": "601138", "name": "工业富联"},
    {"code": "300308", "name": "中际旭创"},
    {"code": "688256", "name": "寒武纪"},
    {"code": "688041", "name": "海光信息"},
    {"code": "300502", "name": "新易盛"},
    {"code": "000977", "name": "浪潮信息"},
    {"code": "300476", "name": "胜宏科技"},
    {"code": "300442", "name": "润泽科技"},
]

# 期货列表 (symbol 映射到 fetch_futures_data.py 的品种代码)
FUTURES_LIST = [
    {"symbol": "AU", "name": "黄金期货", "unit": "元/克"},
    {"symbol": "CU", "name": "铜期货", "unit": "元/吨"},
    {"symbol": "SC", "name": "原油期货", "unit": "元/桶"},
    {"symbol": "ZN", "name": "锌合金期货", "unit": "元/吨"},
    {"symbol": "L",  "name": "ABS塑料期货", "unit": "元/吨"},
]

# 2026年休市日（法定节假日，不含周末）
HOLIDAYS_2026 = {
    "2026-01-01", "2026-01-02",
    "2026-02-16", "2026-02-17", "2026-02-18", "2026-02-19", "2026-02-20",
    "2026-04-04", "2026-04-05", "2026-04-06",
    "2026-05-01", "2026-05-02", "2026-05-03", "2026-05-04", "2026-05-05",
    "2026-05-30", "2026-05-31",
    "2026-09-25", "2026-09-26", "2026-09-27",
    "2026-10-01", "2026-10-02", "2026-10-03", "2026-10-04",
    "2026-10-05", "2026-10-06", "2026-10-07",
}


# ==================== 工具函数 ====================

def is_trading_day(d: date = None) -> tuple:
    """判断是否为交易日，返回 (is_trading, reason)"""
    if d is None:
        d = date.today()
    if d.weekday() >= 5:
        return False, "周末"
    if d.isoformat() in HOLIDAYS_2026:
        return False, "法定节假日"
    return True, ""


def run_cmd(cmd: list, timeout: int = 30) -> tuple:
    """运行子进程命令，返回 (stdout, returncode, stderr)"""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=timeout, cwd=SKILL_DIR,
        )
        return result.stdout, result.returncode, result.stderr
    except subprocess.TimeoutExpired:
        return "", -1, "timeout"
    except Exception as e:
        return str(e), -1, str(e)


def safe_float(val, default=0.0):
    try:
        v = float(val)
        return v
    except (ValueError, TypeError):
        return default


def fmt_pct(val: float) -> str:
    if val >= 0:
        return f"+{val:.2f}%"
    return f"{val:.2f}%"


def fmt_price(val: float, decimals: int = 2) -> str:
    return f"{val:.{decimals}f}"


def parse_kv_lines(text: str) -> dict:
    """解析 LLM 输出的 key: value 格式行，兼容中英文冒号和列表标记"""
    result = {}
    for line in text.strip().split("\n"):
        line = line.strip()
        # 去掉列表标记
        line = re.sub(r'^[-*•]\s*', '', line).strip()
        line = re.sub(r'^\d+\.\s*', '', line).strip()
        if not line:
            continue
        # 兼容中英文冒号
        for sep in ["：", ":"]:
            if sep in line:
                name_part, rest = line.split(sep, 1)
                name_part = name_part.strip()
                rest = rest.strip()
                if name_part and rest:
                    result[name_part] = rest
                break
    return result


# ==================== 数据获取 ====================

async def fetch_hk_stock_data(code: str, short: str) -> dict:
    """获取港股实时数据"""
    stdout, rc, stderr = run_cmd(
        ["python", "fetch_hk_stock_data.py", "--stock_code", code, "--save"],
        timeout=20,
    )
    json_path = os.path.join(SKILL_DIR, f"hk_{short}_data.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 修正 change_pct：新浪港股 raw_fields[8] 是涨跌幅
            raw = data.get("raw_fields", [])
            if len(raw) > 8:
                correct_pct = safe_float(raw[8])
                data["change_pct"] = correct_pct
            # 二次校正：如果 change_pct 绝对值>50，从价格推算
            cur = safe_float(data.get("current_price"))
            prev = safe_float(data.get("prev_close"))
            if prev > 0 and abs(data.get("change_pct", 0)) > 50:
                data["change_pct"] = (cur - prev) / prev * 100
            data["_success"] = True
            return data
        except Exception as e:
            print(f"[港股] 读取JSON失败 {code}: {e}")
    return {"stock_code": code, "_success": False}


async def fetch_a_stock_data(code: str) -> dict:
    """获取A股数据 + 技术分析（含重试）"""
    result = {"stock_code": code, "_success": False}

    # 1) 获取行情 + 历史K线（最多重试2次）
    data_path = os.path.join(SKILL_DIR, f"stock_data_{code}.json")
    for attempt in range(2):
        if attempt > 0:
            print(f"[A股] 重试获取 {code} (第{attempt+1}次)...")
            time.sleep(1)
        stdout, rc, stderr = run_cmd(
            ["python", "fetch_stock_data.py", "--stock_code", code, "--days", "60"],
            timeout=35,
        )
        if os.path.exists(data_path):
            # 验证JSON可读
            try:
                with open(data_path, "r", encoding="utf-8") as f:
                    d = json.load(f)
                if d.get("real_time") or d.get("historical"):
                    result["stock_data"] = d
                    break
            except Exception:
                continue

    if "stock_data" not in result:
        print(f"[A股] 数据获取失败 {code}")
        return result

    # 2) 技术分析（最多重试2次）
    analysis_path = os.path.join(SKILL_DIR, f"analysis_{code}.json")
    for attempt in range(2):
        if attempt > 0:
            print(f"[A股] 重试分析 {code} (第{attempt+1}次)...")
            time.sleep(1)
        stdout2, rc2, stderr2 = run_cmd(
            ["python", "analyze_stock.py",
             "--data_file", f"./stock_data_{code}.json",
             "--output", f"./analysis_{code}.json"],
            timeout=35,
        )
        if os.path.exists(analysis_path):
            try:
                with open(analysis_path, "r", encoding="utf-8") as f:
                    result["analysis"] = json.load(f)
                break
            except Exception:
                continue

    if "analysis" not in result:
        print(f"[A股] 技术分析失败 {code}，继续使用行情数据")

    result["_success"] = True
    return result


async def fetch_future_data(symbol: str) -> dict:
    """获取期货行情（含重试）"""
    for attempt in range(3):
        if attempt > 0:
            print(f"[期货] 重试 {symbol} (第{attempt+1}次)...")
            time.sleep(2)
        stdout, rc, stderr = run_cmd(
            ["python", "fetch_futures_data.py", "--symbol", symbol, "--json"],
            timeout=25,
        )
        if stdout and stdout.strip():
            # 策略1: 直接整体解析 stdout 为 JSON
            try:
                data = json.loads(stdout.strip())
                if data.get("price") and safe_float(data["price"]) > 0:
                    return {"symbol": symbol, "_success": True, "quote": data}
            except json.JSONDecodeError:
                pass
            # 策略2: 从 stdout 中找 JSON 块（多行）
            text = stdout.strip()
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end > start:
                try:
                    data = json.loads(text[start:end+1])
                    if data.get("price") and safe_float(data["price"]) > 0:
                        return {"symbol": symbol, "_success": True, "quote": data}
                except Exception:
                    pass
        print(f"[期货] {symbol} 获取失败 (attempt {attempt+1}), rc={rc}")
    return {"symbol": symbol, "_success": False}


# ==================== 消息面搜索 ====================

async def search_news(sdk, query: str, ver: str) -> str:
    """搜索新闻摘要"""
    try:
        result = await sdk.call_tool(
            "codeact_search_web",
            {"query": query, "response_length": "short"},
            schema_version=ver,
        )
        if result.get("is_success") and result.get("results"):
            snippets = []
            for r in result["results"][:3]:
                s = r.get("snippet", "").strip()
                if s:
                    snippets.append(s)
            return "；".join(snippets)
        return ""
    except Exception as e:
        print(f"[搜索] 失败 {query}: {e}")
        return ""


# ==================== 报告段落生成 ====================

def build_hk_section(hk_results: list, is_trading: bool, reason: str) -> str:
    """生成港股报告段落"""
    lines = ["## 🇭🇰 港股"]

    if not is_trading:
        lines.append("")
        lines.append("今日港股休市" + (f"（{reason}）" if reason else ""))
        return "\n".join(lines)

    for i, item in enumerate(hk_results, 1):
        stock = item["stock"]
        data = item["data"]
        news = item.get("news", "")
        suggestion = item.get("suggestion", "观望")
        name = stock["name"]
        code = stock["code"]

        if not data.get("_success"):
            lines.append(f"\n### {i}. {name} ({code})")
            lines.append("**数据获取失败**")
            continue

        price = safe_float(data.get("current_price") or data.get("display_price"))
        pct = safe_float(data.get("change_pct"))
        data_valid = data.get("data_valid", True)
        data_note = data.get("data_note", "")

        lines.append(f"\n### {i}. {name} ({code})")
        if not data_valid:
            # 数据获取异常（修复：不再误判为停牌）
            ref = safe_float(data.get("prev_close") or data.get("reference_price", 0))
            lines.append(f"**状态**：数据暂缺 | {data_note}")
            if ref > 0:
                lines.append(f"**昨收价**：{fmt_price(ref)}港元")
            cleaned_news = clean_news_text(news)
            lines.append(f"**消息面**：{cleaned_news if cleaned_news else '暂无'}")
            lines.append(f"**操作建议**：数据异常，暂无法分析")
        else:
            lines.append(f"**收盘价**：{fmt_price(price)}港元 | **涨跌**：{fmt_pct(pct)}")
            cleaned_news = clean_news_text(news)
            lines.append(f"**消息面**：{cleaned_news if cleaned_news else '暂无重要消息'}")
            lines.append(f"**操作建议**：{suggestion}")

    return "\n".join(lines)


def build_a_section(a_results: list, is_trading: bool, reason: str) -> str:
    """生成A股报告段落"""
    lines = ["## 🇨🇳 A股AI上游"]

    if not is_trading:
        lines.append("")
        lines.append("今日A股休市" + (f"（{reason}）" if reason else ""))
        return "\n".join(lines)

    for i, item in enumerate(a_results, 1):
        stock = item["stock"]
        data = item["data"]
        news = item.get("news", "")
        suggestion = item.get("suggestion", "观望")
        name = stock["name"]
        code = stock["code"]

        if not data.get("_success"):
            lines.append(f"\n### {i}. {name} ({code})")
            lines.append("**数据获取失败**")
            continue

        sd = data.get("stock_data", {})
        rt = sd.get("real_time", {})
        analysis = data.get("analysis", {})

        price = safe_float(rt.get("current") or analysis.get("current_price"))
        pct = safe_float(rt.get("change_pct"))
        prev = safe_float(rt.get("pre_close"))
        if pct == 0 and prev > 0 and price > 0:
            pct = (price - prev) / prev * 100

        lines.append(f"\n### {i}. {name} ({code})")
        lines.append(f"**收盘价**：{fmt_price(price)}元 | **涨跌**：{fmt_pct(pct)}")

        # 技术面摘要
        tech_parts = []
        ti = analysis.get("technical_indicators", {})
        ma5 = ti.get("ma5")
        ma10 = ti.get("ma10")
        ma20 = ti.get("ma20")
        if ma5 and ma10 and ma20:
            tech_parts.append(f"MA5={fmt_price(ma5)}/MA10={fmt_price(ma10)}/MA20={fmt_price(ma20)}")

        trend = analysis.get("trend_analysis", {})
        t = trend.get("trend", "")
        s = trend.get("strength", "")
        if t:
            tech_parts.append(f"趋势: {t}({s})")

        macd_info = ti.get("macd", {})
        sig_list = macd_info.get("signal", [])
        if sig_list:
            tech_parts.append(sig_list[0])

        rsi_info = ti.get("rsi", {})
        if rsi_info:
            tech_parts.append(f"RSI={rsi_info.get('value', 'N/A')}({rsi_info.get('signal', '')})")

        # 支撑/压力位
        sr = analysis.get("support_resistance", {})
        supports = sr.get("support_levels", [])
        resistances = sr.get("resistance_levels", [])
        if supports:
            tech_parts.append(f"支撑{fmt_price(supports[0].get('price', 0))}")
        if resistances:
            tech_parts.append(f"压力{fmt_price(resistances[0].get('price', 0))}")

        if tech_parts:
            lines.append(f"**技术面**：{'；'.join(tech_parts)}")
        else:
            lines.append("**技术面**：数据不足")

        cleaned_news = clean_news_text(news)
        lines.append(f"**消息面**：{cleaned_news if cleaned_news else '暂无重要消息'}")
        lines.append(f"**操作建议**：{suggestion}")

    return "\n".join(lines)


def clean_news_text(text: str) -> str:
    """清洗消息面文本，去除表格数据、版权声明、博主引导、重复段落"""
    if not text:
        return ""
    
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        # 跳过纯数字行（如 "3.2", "850.0" 等）
        if re.match(r'^[\d.,;()（）\-\s]+$', stripped) and not re.search(r'[a-zA-Z\u4e00-\u9fff]', stripped):
            continue
        # 跳过纯数字+年份行（如 "2024(E)", "2025(F)"）
        if re.match(r'^\d{4}\s*\([EF]\)\s*$', stripped):
            continue
        # 跳过版权/合规声明
        if '风险提示' in stripped and '本报告' in stripped:
            continue
        if '本公司及本公司有关' in stripped:
            continue
        if '不得承担' in stripped or '不承担任何' in stripped:
            continue
        if '投资咨询业务资格' in stripped:
            continue
        if '证监许可' in stripped:
            continue
        if '投资咨询证书' in stripped:
            continue
        # 跳过博主关注引导
        if re.search(r'大家好我是|点个关注|随缘更|掏干货|对生活有用', stripped):
            continue
        # 跳过微博超话标签
        if re.search(r'#.*\[超话\]#', stripped):
            continue
        # 跳过联系邮箱/作者署名行
        if re.search(r'联系邮箱|@[\w.]+\.\w+', stripped) and len(stripped) < 80:
            continue
        # 跳过孤立的摘要标记词
        if stripped in ('摘要', '主要观点', '摘要\n主要观点'):
            continue
        # 跳过来源标记
        if stripped.startswith('来源:') or stripped.startswith('来源：'):
            continue
        
        cleaned.append(line)
    
    # 去除所有重复段落（不只连续的，任意位置重复都去）
    seen = set()
    result = []
    for line in cleaned:
        stripped = line.strip()
        if stripped and stripped in seen:
            continue
        if stripped:
            seen.add(stripped)
        result.append(line)
    
    # 截断过长的消息面（保留前3段，约500字）
    final_text = "\n".join(result).strip()
    if len(final_text) > 500:
        # 按句号分段，保留前500字不截断句子
        truncate_at = final_text[:500].rfind('。')
        if truncate_at > 200:
            final_text = final_text[:truncate_at + 1]
        else:
            final_text = final_text[:500] + "..."
    
    return final_text


def build_futures_section(f_results: list) -> str:
    """生成期货报告段落"""
    lines = ["## 💰 期货分析（每日必出）"]

    for i, item in enumerate(f_results, 1):
        future = item["future"]
        data = item["data"]
        news = item.get("news", "")
        prediction = item.get("prediction", "震荡")
        name = future["name"]
        unit = future["unit"]

        if not data.get("_success"):
            lines.append(f"\n### {i}. {name}")
            lines.append("**数据获取失败**")
            continue

        q = data.get("quote", {})
        price = safe_float(q.get("price"))
        pct = safe_float(q.get("change_pct"))

        lines.append(f"\n### {i}. {name}")
        lines.append(f"**最新价**：{fmt_price(price, 2)}{unit} | **涨跌**：{fmt_pct(pct)}")

        # 技术形态
        high = safe_float(q.get("high"))
        low = safe_float(q.get("low"))
        open_ = safe_float(q.get("open"))
        shape_parts = []
        if price > 0 and open_ > 0:
            if price > open_:
                shape_parts.append("阳线")
            elif price < open_:
                shape_parts.append("阴线")
            else:
                shape_parts.append("十字星")
            if high > 0 and low > 0:
                amplitude = (high - low) / price * 100
                shape_parts.append(f"振幅{amplitude:.1f}%")
            # 上下影线
            upper_shadow = high - max(price, open_)
            lower_shadow = min(price, open_) - low
            if upper_shadow > 0 and (high - low) > 0:
                shape_parts.append(f"上影{(upper_shadow/(high-low)*100):.0f}%")
            if lower_shadow > 0 and (high - low) > 0:
                shape_parts.append(f"下影{(lower_shadow/(high-low)*100):.0f}%")

        if shape_parts:
            lines.append(f"**技术形态**：{'；'.join(shape_parts)}")
        else:
            lines.append("**技术形态**：—")

        cleaned_news = clean_news_text(news)
        lines.append(f"**消息面**：{cleaned_news if cleaned_news else '暂无'}")
        lines.append(f"**短期预测**：{prediction}")

    return "\n".join(lines)


def build_impact_section(impact_text: str) -> str:
    """生成业务影响段落"""
    lines = ["## 📊 对主人业务的影响", ""]
    if impact_text:
        lines.append(impact_text)
    else:
        lines.append("- 📦 **物流/出口影响**：—")
        lines.append("- 💱 **汇率影响**：—")
        lines.append("- 🔩 **原材料采购建议**：—")
    return "\n".join(lines)


# ==================== 主流程 ====================

async def main():
    result_mode = sys.argv[1] if len(sys.argv) > 1 else "display_only"

    today = date.today()
    today_str = today.strftime("%Y%m%d")
    today_display = today.strftime("%Y年%m月%d日")
    weekday_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][today.weekday()]

    print(f"[参数] result_mode={result_mode}, 日期={today_str}({weekday_cn})")

    sdk = CodeActSDK()

    # 工具版本号
    SEARCH_VER = "v1_5ac1b0eba8c26f2a"
    FETCH_VER = "v1_2c8d0580b3f93a58"

    # 判断交易日
    is_stock_trading, stock_reason = is_trading_day(today)

    try:
        # ========== Phase 1: 数据获取 ==========

        # --- 港股 ---
        hk_results = []
        if is_stock_trading:
            for stock in HK_STOCKS:
                print(f"[港股] 获取 {stock['name']}...")
                data = await fetch_hk_stock_data(stock["code"], stock["short"])
                hk_results.append({"stock": stock, "data": data, "news": "", "suggestion": "观望"})
        else:
            print(f"[港股] 今日休市: {stock_reason}")

        # --- A股 ---
        a_results = []
        if is_stock_trading:
            for stock in A_STOCKS:
                print(f"[A股] 获取 {stock['name']}({stock['code']})...")
                data = await fetch_a_stock_data(stock["code"])
                a_results.append({"stock": stock, "data": data, "news": "", "suggestion": "观望"})
        else:
            print(f"[A股] 今日休市: {stock_reason}")

        # --- 期货 ---
        f_results = []
        for f in FUTURES_LIST:
            print(f"[期货] 获取 {f['name']}...")
            data = await fetch_future_data(f["symbol"])
            f_results.append({"future": f, "data": data, "news": "", "prediction": "震荡"})

        # ========== Phase 2: 消息面搜索 ==========

        print("[消息面] 搜索新闻...")
        sem = asyncio.Semaphore(3)

        async def lim_search(q):
            async with sem:
                return await search_news(sdk, q, SEARCH_VER)

        search_tasks = []
        search_keys = []

        if is_stock_trading:
            for i, stock in enumerate(HK_STOCKS):
                search_keys.append(f"hk_{i}")
                search_tasks.append(lim_search(f"{stock['name']} 港股 最新消息 2026"))
            for i, stock in enumerate(A_STOCKS):
                search_keys.append(f"a_{i}")
                search_tasks.append(lim_search(f"{stock['name']} AI 最新消息 2026"))

        for i, f in enumerate(FUTURES_LIST):
            search_keys.append(f"f_{i}")
            search_tasks.append(lim_search(f"{f['name']} 行情走势 2026"))

        search_outputs = await asyncio.gather(*search_tasks, return_exceptions=True)
        news_map = {}
        for k, v in zip(search_keys, search_outputs):
            news_map[k] = v if isinstance(v, str) else ""

        if is_stock_trading:
            for i in range(len(hk_results)):
                hk_results[i]["news"] = news_map.get(f"hk_{i}", "")
            for i in range(len(a_results)):
                a_results[i]["news"] = news_map.get(f"a_{i}", "")
        for i in range(len(f_results)):
            f_results[i]["news"] = news_map.get(f"f_{i}", "")

        # ========== Phase 3: LLM 生成建议 ==========

        print("[LLM] 生成操作建议...")

        # --- 股票建议（一次LLM调用） ---
        if is_stock_trading and (hk_results or a_results):
            stock_summary_parts = []

            for item in hk_results:
                s = item["stock"]
                d = item["data"]
                if d.get("_success") and not d.get("suspended"):
                    p = safe_float(d.get("current_price") or d.get("display_price"))
                    pct = safe_float(d.get("change_pct"))
                    stock_summary_parts.append(
                        f"- {s['name']}({s['code']}): 港股, 价格{fmt_price(p)}港元, 涨跌{fmt_pct(pct)}"
                    )

            for item in a_results:
                s = item["stock"]
                d = item["data"]
                if d.get("_success"):
                    sd = d.get("stock_data", {})
                    rt = sd.get("real_time", {})
                    analysis = d.get("analysis", {})
                    p = safe_float(rt.get("current") or analysis.get("current_price"))
                    prev = safe_float(rt.get("pre_close"))
                    pct = safe_float(rt.get("change_pct"))
                    if pct == 0 and prev > 0 and p > 0:
                        pct = (p - prev) / prev * 100
                    trend = analysis.get("trend_analysis", {}).get("trend", "N/A")
                    rsi_val = analysis.get("technical_indicators", {}).get("rsi", {}).get("value", "N/A")
                    stock_summary_parts.append(
                        f"- {s['name']}({s['code']}): A股, 价格{fmt_price(p)}元, 涨跌{fmt_pct(pct)}, 趋势{trend}, RSI{rsi_val}"
                    )

            if stock_summary_parts:
                stock_summary = "\n".join(stock_summary_parts)
                try:
                    raw = await sdk.call_llm(
                        messages=[{
                            "role": "user",
                            "content": f"""根据以下股票数据，为每只股票给出操作建议。

{stock_summary}

要求：
- 建议2-8字，如：持有/观望/减仓/加仓/短线/空仓/逢低布局
- 附一句理由
- 严格每行一只，格式：股票名 | 建议 | 理由
- 不要输出其他内容"""
                        }]
                    )
                    sug_map = parse_kv_lines(raw)
                    # 也尝试 | 分隔格式
                    for line in raw.strip().split("\n"):
                        line = re.sub(r'^[-*•\d.]\s*', '', line).strip()
                        if " | " in line:
                            parts = [p.strip() for p in line.split("|")]
                            if len(parts) >= 2:
                                name_part = parts[0].strip()
                                sug = parts[1].strip()
                                reason = parts[2].strip() if len(parts) > 2 else ""
                                sug_map[name_part] = f"{sug} | {reason}" if reason else sug

                    # 匹配建议到结果
                    for item in hk_results + a_results:
                        n = item["stock"]["name"]
                        if n in sug_map:
                            item["suggestion"] = sug_map[n]
                        else:
                            # 模糊匹配
                            for key in sug_map:
                                if n in key or key in n:
                                    item["suggestion"] = sug_map[key]
                                    break

                    print(f"[LLM] 股票建议解析: {len(sug_map)} 条")

                except LLMError as e:
                    print(f"[LLM] 股票建议生成失败: {e}")

        # --- 期货短期预测（一次LLM调用） ---
        futures_summary_parts = []
        for item in f_results:
            f = item["future"]
            d = item["data"]
            if d.get("_success"):
                q = d.get("quote", {})
                p = safe_float(q.get("price"))
                pct = safe_float(q.get("change_pct"))
                futures_summary_parts.append(
                    f"- {f['name']}({f['symbol']}): 价格{fmt_price(p)}, 涨跌{fmt_pct(pct)}"
                )

        if futures_summary_parts:
            futures_summary = "\n".join(futures_summary_parts)
            try:
                raw = await sdk.call_llm(
                    messages=[{
                        "role": "user",
                        "content": f"""根据以下期货行情数据，为每个品种给出短期预测。

{futures_summary}

要求：
- 预测2-10字，如：偏强震荡/弱势下行/高位盘整/短线偏多/谨慎观望
- 附一句理由
- 严格每行一个，格式：品种名 | 预测 | 理由
- 不要输出其他内容"""
                    }]
                )
                pred_map = {}
                for line in raw.strip().split("\n"):
                    line = re.sub(r'^[-*•\d.]\s*', '', line).strip()
                    if " | " in line:
                        parts = [p.strip() for p in line.split("|")]
                        if len(parts) >= 2:
                            name_part = parts[0].strip()
                            pred = parts[1].strip()
                            reason = parts[2].strip() if len(parts) > 2 else ""
                            pred_map[name_part] = f"{pred}（{reason}）" if reason else pred

                for item in f_results:
                    n = item["future"]["name"]
                    if n in pred_map:
                        item["prediction"] = pred_map[n]
                    else:
                        for key in pred_map:
                            if n in key or key in n:
                                item["prediction"] = pred_map[key]
                                break

                print(f"[LLM] 期货预测解析: {len(pred_map)} 条")

            except LLMError as e:
                print(f"[LLM] 期货预测生成失败: {e}")

        # --- 业务影响（一次LLM调用） ---
        print("[LLM] 生成业务影响分析...")
        impact_context_parts = []
        for item in f_results:
            f = item["future"]
            d = item["data"]
            if d.get("_success"):
                q = d.get("quote", {})
                p = safe_float(q.get("price"))
                pct = safe_float(q.get("change_pct"))
                impact_context_parts.append(f"{f['name']}: {fmt_price(p)} ({fmt_pct(pct)})")
        # 加入股价整体趋势
        if is_stock_trading:
            a_pcts = []
            for item in a_results:
                d = item["data"]
                if d.get("_success"):
                    rt = d.get("stock_data", {}).get("real_time", {})
                    pct = safe_float(rt.get("change_pct"))
                    a_pcts.append(pct)
            if a_pcts:
                avg_pct = sum(a_pcts) / len(a_pcts)
                impact_context_parts.append(f"A股AI上游平均涨跌: {fmt_pct(avg_pct)}")

        impact_context = "；".join(impact_context_parts)
        impact_text = ""
        try:
            impact_text = await sdk.call_llm(
                messages=[{
                    "role": "user",
                    "content": f"""根据以下行情数据，分析对跨境电商/物流出口业务的影响，给出简要建议。

当前行情: {impact_context}

请按以下格式输出（每个一行，简洁，每条不超过30字）：
- 📦 **物流/出口影响**：...
- 💱 **汇率影响**：...
- 🔩 **原材料采购建议**：..."""
                }]
            )
        except LLMError as e:
            print(f"[LLM] 业务影响生成失败: {e}")

        # ========== Phase 4: 组装报告 ==========

        print("[报告] 组装...")

        # 完整报告（保存到文件）
        full_report_lines = [
            f"# 每日股票期货综合分析",
            f"> {today_display}（{weekday_cn}）",
            "",
            "---",
            "",
            build_hk_section(hk_results, is_stock_trading, stock_reason),
            "",
            "---",
            "",
            build_a_section(a_results, is_stock_trading, stock_reason),
            "",
            "---",
            "",
            build_futures_section(f_results),
            "",
            "---",
            "",
            build_impact_section(impact_text),
            "",
            "---",
            "",
            "⚠️ *以上分析仅供参考，不构成投资建议*",
        ]
        full_report = "\n".join(full_report_lines)

        # ========== Phase 5: 保存 ==========

        report_dir = os.path.join(REPORT_BASE, today_str)
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, "股票分析报告.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(full_report)
        print(f"[保存] 报告已保存到: {report_path}")

        # ========== Phase 6: 组装精简版消息 ==========

        brief_lines = [
            f"[主人](at://owner) 🐾 每日股票期货报告来啦！",
            "",
            f"> {today_display}（{weekday_cn}）",
            "",
            "---",
        ]

        # --- 港股精简 ---
        brief_lines.append("")
        if not is_stock_trading:
            brief_lines.append("### 🎰 港股博彩")
            reason_suffix = f"（{stock_reason}）" if stock_reason else ""
            brief_lines.append(f"今日休市{reason_suffix}")
        else:
            brief_lines.append("### 🎰 港股博彩")
            brief_lines.append("")
            for item in hk_results:
                s = item["stock"]
                d = item["data"]
                if d.get("_success") and d.get("data_valid", True):
                    # 数据正常：显示价格和涨跌
                    p = safe_float(d.get("current_price") or d.get("display_price"))
                    pct = safe_float(d.get("change_pct"))
                    brief_lines.append(f"- {s['name']} {fmt_price(p)}港元（{fmt_pct(pct)}）")
                elif d.get("_success") and not d.get("data_valid", True):
                    # 数据获取异常：显示"数据暂缺"（修复：不再误判为停牌）
                    brief_lines.append(f"- {s['name']} 数据暂缺")
                else:
                    # 数据完全获取失败
                    brief_lines.append(f"- {s['name']} 数据暂缺")

        # --- A股精简 ---
        brief_lines.append("")
        if not is_stock_trading:
            brief_lines.append("### 🔥 A股AI板块")
            reason_suffix2 = f"（{stock_reason}）" if stock_reason else ""
            brief_lines.append(f"今日休市{reason_suffix2}")
        else:
            # 找出亮点
            a_highlights = []
            for item in a_results:
                s = item["stock"]
                d = item["data"]
                sug = item.get("suggestion", "观望")
                if d.get("_success"):
                    sd = d.get("stock_data", {})
                    rt = sd.get("real_time", {})
                    analysis = d.get("analysis", {})
                    p = safe_float(rt.get("current") or analysis.get("current_price"))
                    prev = safe_float(rt.get("pre_close"))
                    pct = safe_float(rt.get("change_pct"))
                    if pct == 0 and prev > 0 and p > 0:
                        pct = (p - prev) / prev * 100
                    highlight = ""
                    if abs(pct) >= 5:
                        highlight = " 🔥" if pct > 0 else " ⚠️"
                    a_highlights.append((s["name"], pct, p, sug, highlight))

            # 表格
            brief_lines.append("")
            brief_lines.append("| 股票 | 涨跌幅 | 价格 | 建议 |")
            brief_lines.append("|------|--------|------|------|")
            for name, pct, p, sug, hl in a_highlights:
                brief_lines.append(f"| {name}{hl} | {fmt_pct(pct)} | {fmt_price(p)}元 | {sug} |")

        # --- 期货精简 ---
        brief_lines.append("")
        brief_lines.append("### 💰 期货")
        brief_lines.append("")
        brief_lines.append("| 品种 | 价格 | 涨跌 |")
        brief_lines.append("|------|------|------|")
        for item in f_results:
            f = item["future"]
            d = item["data"]
            pred = item.get("prediction", "震荡")
            if d.get("_success"):
                q = d.get("quote", {})
                p = safe_float(q.get("price"))
                pct = safe_float(q.get("change_pct"))
                brief_lines.append(f"| {f['name']} | {fmt_price(p, 2)}{f['unit']} | {fmt_pct(pct)} |")
            else:
                brief_lines.append(f"| {f['name']} | — | — |")

        # --- 业务影响 ---
        brief_lines.append("")
        if impact_text:
            brief_lines.append(f"📦 **对主人业务影响**：{impact_text.strip().split(chr(10))[0].lstrip('- ').strip()}")
        else:
            brief_lines.append("📦 **对主人业务影响**：—")

        brief_lines.append("")
        brief_lines.append(f"完整报告：[股票分析报告](computer://{report_path})")
        brief_lines.append("")
        brief_lines.append("⚠️ *以上分析仅供参考，不构成投资建议* 🦴")

        brief_report = "\n".join(brief_lines)

        # ========== Phase 7: 提交结果 ==========

        actual_mode = result_mode if result_mode != "auto" else "display_only"
        await sdk.submit_result(
            result_mode=actual_mode,
            status="success",
            message=brief_report,
            data={"report_path": report_path, "date": today_str},
        )

    except Exception as e:
        print(f"[异常] {e}")
        import traceback
        traceback.print_exc()
        actual_mode = result_mode if result_mode not in ("auto",) else "notify"
        await sdk.submit_result(
            result_mode=actual_mode,
            status="error",
            message=f"每日股票报告生成失败: {e}",
        )


if __name__ == "__main__":
    asyncio.run(main())
