#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股数据获取脚本 - 支持停牌检测
用于替代核心模块处理港股数据

用法：
    python fetch_hk_stock_data.py --stock_code 02282.HK --days 30
    python fetch_hk_stock_data.py --stock_code 02282.HK,01928.HK --days 30
"""

import sys
import os
import json
import argparse
import subprocess
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, List

# 尝试导入可选依赖
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class HKStockDataFetcher:
    """港股数据获取器 - 支持停牌检测"""
    
    # 新浪财经港股API
    SINA_BASE_URL = "https://hq.sinajs.cn/list="
    
    # 东方财富港股API
    EASTMONEY_URL = "https://push2.eastmoney.com/api/qt/stock/get"
    
    def __init__(self):
        self.headers = {
            "Referer": "https://finance.sina.com.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def is_hk_stock(self, stock_code: str) -> bool:
        """判断是否为港股"""
        stock_code = stock_code.upper().strip()
        # 港股格式：4-5位数字.HK 或 rt_hkXXXX 或 纯4-5位数字
        return bool(re.match(r'^\d{4,5}\.HK$', stock_code)) or \
               stock_code.upper().startswith('RT_HK') or \
               bool(re.match(r'^\d{4,5}$', stock_code))
    
    def normalize_code(self, stock_code: str) -> str:
        """标准化港股代码格式"""
        stock_code = stock_code.strip().upper()
        # 移除可能的 rt_hk 前缀
        stock_code = re.sub(r'^RT_HK', '', stock_code)
        # 确保是4-5位数字
        match = re.search(r'(\d{4,5})', stock_code)
        if match:
            return match.group(1)
        return stock_code
    
    def parse_sina_data(self, response_text) -> Optional[Dict]:
        """解析新浪财经返回的港股数据"""
        try:
            # 编码处理：新浪港股返回GBK编码
            if isinstance(response_text, bytes):
                try:
                    text = response_text.decode('gbk')
                except:
                    text = response_text.decode('utf-8', errors='replace')
            else:
                # 如果是字符串，尝试编码转换
                try:
                    text = response_text.encode('latin1').decode('gbk')
                except:
                    text = str(response_text)
            
            # 格式: var hq_str_rt_hk02282="英文名,中文名,现价,昨收,涨跌幅%,今开,昨收价,涨跌额,涨跌幅,买价,卖价,成交量,...
            match = re.search(r'hq_str_[^=]+="([^"]+)"', text)
            if not match:
                return None
            
            fields = match.group(1).split(',')
            if len(fields) < 15:
                return None
            
            # 新浪港股字段解析
            # [0] 英文名称, [1] 中文名称, [2] 现价, [3] 昨收, [4] 涨跌幅%,
            # [5] 今开, [6] 昨收价(备用), [7] 涨跌额, [8] 涨跌幅(备用),
            # [9] 买价, [10] 卖价, [11] 成交量
            name_en = fields[0]
            name_cn = fields[1]
            current_price = self._safe_float(fields[2])
            prev_close = self._safe_float(fields[3])
            change_pct = self._safe_float(fields[4])
            open_price = self._safe_float(fields[5])
            change = self._safe_float(fields[7])
            
            # 尝试从其他位置获取最高最低价
            # 根据成交量后的字段判断
            high_price = current_price  # 临时用现价
            low_price = current_price   # 临时用现价
            for i in range(12, min(20, len(fields))):
                try:
                    val = float(fields[i])
                    if val > current_price * 0.9 and val < current_price * 1.1:
                        if high_price == current_price or val > high_price:
                            high_price = val
                        if low_price == current_price or val < low_price:
                            low_price = val
                except:
                    continue
            
            # 日期时间位置：字段[17]是日期，字段[18]是时间
            date_str = fields[17] if len(fields) > 17 and re.match(r'\d{4}/\d{2}/\d{2}', fields[17]) else ''
            time_str = fields[18] if len(fields) > 18 and re.match(r'\d{2}:\d{2}:\d{2}', fields[18]) else ''
            
            return {
                'name': f"{name_en} ({name_cn})",
                'name_en': name_en,
                'name_cn': name_cn,
                'current_price': current_price,
                'prev_close': prev_close,
                'change_pct': change_pct,
                'change': change,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'volume': self._safe_float(fields[11]) if len(fields) > 11 else 0,
                'date': date_str,
                'time': time_str,
                'raw_fields': fields
            }
        except Exception as e:
            print(f"解析新浪数据失败: {e}", file=sys.stderr)
            return None
    
    def _safe_float(self, val: str, default: float = 0.0) -> float:
        """安全转换为浮点数"""
        try:
            return float(val)
        except:
            return default
    
    def fetch_from_sina(self, stock_code: str) -> Optional[Dict]:
        """从新浪财经获取港股数据"""
        code = self.normalize_code(stock_code)
        sina_code = f'rt_hk{code}'
        
        try:
            if HAS_REQUESTS:
                response = requests.get(
                    f"{self.SINA_BASE_URL}{sina_code}",
                    headers=self.headers,
                    timeout=10
                )
                # 保持原始bytes，不自动解码
                raw_text = response.content
            else:
                # 使用curl作为备用
                result = subprocess.run(
                    ['curl', '-s', f'https://hq.sinajs.cn/list={sina_code}',
                     '-H', 'Referer: https://finance.sina.com.cn',
                     '--compressed'],
                    capture_output=True, timeout=10
                )
                raw_text = result.stdout
            
            return self.parse_sina_data(raw_text)
        except Exception as e:
            print(f"新浪财经获取失败: {e}", file=sys.stderr)
            return None
    
    def fetch_from_eastmoney(self, stock_code: str) -> Optional[Dict]:
        """从东方财富获取港股数据"""
        code = self.normalize_code(stock_code)
        
        # 东方财富港股代码格式: 116.MGMLLIS (MGM美高梅), 139.SANDSLIS (金沙)
        # 美高梅中国 02282 -> 116.MGMLLIS
        # 金沙中国 01928 -> 139.SANDSLIS
        em_codes = {
            '02282': '116.MGMLLIS',
            '01928': '139.SANDSLIS'
        }
        em_code = em_codes.get(code, f'{code}.HK')
        
        try:
            params = {
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                'fields': 'f43,f44,f45,f46,f47,f48,f57,f58,f60,f169,f170',
                'secid': f'116.{em_code}'
            }
            
            if HAS_REQUESTS:
                response = requests.get(
                    self.EASTMONEY_URL,
                    params=params,
                    headers={'User-Agent': 'Mozilla/5.0'},
                    timeout=10
                )
                data = response.json()
                
                if data.get('data'):
                    d = data['data']
                    return {
                        'current_price': d.get('f43', 0) / 100 if d.get('f43') else 0,
                        'change': d.get('f44', 0) / 100 if d.get('f44') else 0,
                        'change_pct': d.get('f45', 0) / 100 if d.get('f45') else 0,
                        'open': d.get('f46', 0) / 100 if d.get('f46') else 0,
                        'prev_close': d.get('f60', 0) / 100 if d.get('f60') else 0,
                        'high': d.get('f44', 0) / 100 if d.get('f44') else 0,
                        'low': d.get('f47', 0) / 100 if d.get('f47') else 0,
                        'volume': d.get('f48', 0) if d.get('f48') else 0,
                        'source': 'eastmoney'
                    }
        except Exception as e:
            print(f"东方财富获取失败: {e}", file=sys.stderr)
        
        return None
    
    def check_suspension(self, stock_code: str, data: Dict) -> Dict:
        """检测股票数据质量（修复：价格为0时不直接判断为停牌，标记为数据异常）"""
        current_price = data.get('current_price', 0)
        prev_close = data.get('prev_close', 0)
        volume = data.get('volume', 0)
        name = data.get('name', '')
        
        # 数据质量判断（不再误判为停牌）
        data_valid = True
        data_note = ''
        
        # 情况1: 现价和昨收都为0 → 数据获取失败，不是停牌
        if current_price == 0 and prev_close == 0:
            data_valid = False
            data_note = '数据获取异常（价格为0）'
        # 情况2: 现价=0但昨收>0 → 可能是数据问题，优先显示数据异常
        elif current_price == 0 and prev_close > 0:
            data_valid = False
            data_note = '数据获取异常（现价为0）'
        # 情况3: 正常数据
        else:
            data_valid = True
        
        # 标记数据状态
        data['data_valid'] = data_valid
        data['data_note'] = data_note
        data['suspended'] = False  # 不再误判为停牌
        data['display_price'] = current_price if data_valid else prev_close
        data['tech_analysis_available'] = data_valid
        
        if not data_valid:
            data['tech_analysis_note'] = data_note
        
        return data
    
    def fetch(self, stock_code: str, days: int = 30) -> Dict:
        """
        获取港股数据
        
        Args:
            stock_code: 股票代码，如 02282.HK
            days: 获取历史数据天数（用于技术分析）
        
        Returns:
            包含股票数据的字典
        """
        result = {
            'stock_code': stock_code,
            'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': 'sina',
            'days': days
        }
        
        # 优先从新浪获取
        data = self.fetch_from_sina(stock_code)
        
        if not data:
            # 备用：东方财富
            data = self.fetch_from_eastmoney(stock_code)
            if data:
                result['source'] = 'eastmoney'
        
        if not data:
            result['error'] = f'无法获取 {stock_code} 的数据'
            result['success'] = False
            return result
        
        # 合并数据
        result.update(data)
        
        # 停牌检测
        result = self.check_suspension(stock_code, result)
        
        # 生成简要报告
        if result.get('suspended'):
            status = f"【停牌】{result.get('suspension_reason', '停牌中')}"
            if result.get('reference_price'):
                status += f"，昨收价: {result['reference_price']:.3f}"
        else:
            change_sign = '+' if result.get('change', 0) >= 0 else ''
            status = f"现价: {result.get('current_price', 0):.3f} ({change_sign}{result.get('change_pct', 0):.2f}%)"
        
        result['status_summary'] = status
        result['success'] = True
        
        return result
    
    def save_to_file(self, data: Dict, stock_code: str) -> str:
        """保存数据到文件"""
        code = self.normalize_code(stock_code)
        filename = f"hk_{code}_data.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        return filename


def main():
    parser = argparse.ArgumentParser(description='港股数据获取 - 支持停牌检测')
    parser.add_argument('--stock_code', required=True, help='股票代码，如 02282.HK 或 02282,01928')
    parser.add_argument('--days', type=int, default=30, help='历史数据天数')
    parser.add_argument('--save', action='store_true', help='保存到文件')
    
    args = parser.parse_args()
    
    fetcher = HKStockDataFetcher()
    
    # 支持批量获取
    codes = [c.strip() for c in args.stock_code.split(',')]
    
    results = []
    for code in codes:
        if not fetcher.is_hk_stock(code):
            print(f"跳过非港股代码: {code}", file=sys.stderr)
            continue
        
        print(f"\n{'='*50}")
        print(f"获取港股数据: {code}")
        print('='*50)
        
        result = fetcher.fetch(code, args.days)
        results.append(result)
        
        if result.get('success'):
            print(f"股票名称: {result.get('name', 'N/A')}")
            print(f"当前状态: {result['status_summary']}")
            print(f"数据来源: {result.get('source', 'unknown')}")
            print(f"获取时间: {result.get('fetch_time', 'N/A')}")
            
            if result.get('suspended'):
                print(f"\n⚠️ 停牌提示: {result.get('suspension_reason', '停牌中')}")
                print(f"   {result.get('tech_analysis_note', '')}")
            else:
                print(f"昨收价: {result.get('prev_close', 0):.3f}")
                print(f"今开价: {result.get('open', 0):.3f}")
                print(f"最高价: {result.get('high', 0):.3f}")
                print(f"最低价: {result.get('low', 0):.3f}")
                print(f"成交量: {result.get('volume', 0):,.0f}")
        else:
            print(f"❌ 获取失败: {result.get('error', '未知错误')}")
        
        if args.save:
            filename = fetcher.save_to_file(result, code)
            print(f"\n数据已保存到: {filename}")
    
    # 如果是批量，输出汇总
    if len(results) > 1:
        print(f"\n{'='*50}")
        print(f"批量获取汇总 ({len(results)} 只股票)")
        print('='*50)
        for r in results:
            status = '✅' if r.get('success') else '❌'
            suspended = ' [停牌]' if r.get('suspended') else ''
            print(f"{status} {r.get('stock_code', 'N/A')}: {r.get('status_summary', '')}{suspended}")


if __name__ == '__main__':
    main()
