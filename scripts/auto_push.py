#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合皖助联 - 就业市场动态自动推送脚本
每2天推送一次
格式：招聘 → 政策 → 招标 → 产品
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context

# 飞书 Webhook URL
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/38880b0c-a886-4461-a929-50f021961ec3"

# 数据文件路径
DATA_FILE = "assets/push_history.json"

# 排除关键词（垃圾信息）
EXCLUDE_KEYWORDS = [
    "研究报告", "行业分析", "白皮书", "榜单", "排行榜", "TOP10", "十大",
    "推荐榜", "服务商推荐", "厂家推荐", "服务商排名", "哪家好",
    "测评", "选择指南", "选型指南", "值得托付", "服务商排行"
]

# 信息有效期（只推送最近30天内的信息）
EFFECTIVE_DAYS = 30


class JobMarketScanner:
    """就业市场扫描器"""
    
    def __init__(self):
        self.ctx = new_context(method="search.web")
        self.client = SearchClient(ctx=self.ctx)
    
    def is_valid_result(self, title: str, snippet: str = "") -> bool:
        """判断是否是有效结果"""
        text = f"{title} {snippet}".lower()
        for keyword in EXCLUDE_KEYWORDS:
            if keyword.lower() in text:
                return False
        return True
    
    def is_recent(self, date_str: str) -> bool:
        """判断日期是否在有效期内（最近30天）"""
        if not date_str:
            return True  # 没有日期的保留
        try:
            publish_date = datetime.strptime(date_str, "%Y-%m-%d")
            days_diff = (datetime.now() - publish_date).days
            return days_diff <= EFFECTIVE_DAYS
        except:
            return True  # 日期解析失败的保留
    
    def search_jobs(self) -> List[Dict]:
        """搜索招聘信息"""
        print("\n🔍 搜索招聘信息...")
        results = []
        
        queries = [
            "残疾人 招聘 合肥 2026",
            "数据标注 残疾人 专属岗位",
            "残疾人 工作 招聘 安徽"
        ]
        
        for query in queries:
            try:
                response = self.client.web_search(query=query, count=5)
                if response.web_items:
                    for item in response.web_items:
                        if "招聘" in item.title or "zhipin" in item.url:
                            if not self.is_valid_result(item.title, item.snippet):
                                continue
                            date_str = item.publish_time[:10] if item.publish_time else ""
                            if not self.is_recent(date_str):
                                print(f"  跳过过期: {item.title[:30]}...")
                                continue
                            results.append({
                                "title": item.title,
                                "company": item.site_name,
                                "date": date_str,
                                "snippet": item.snippet[:100] if item.snippet else "",
                                "url": item.url
                            })
            except Exception as e:
                print(f"  搜索失败: {e}")
        
        # 去重
        seen = set()
        unique = []
        for r in results:
            if r["title"] not in seen:
                seen.add(r["title"])
                unique.append(r)
        
        print(f"  找到 {len(unique)} 条有效招聘")
        return unique[:5]
    
    def search_policy(self) -> List[Dict]:
        """搜索政策信息"""
        print("\n📋 搜索政策信息...")
        results = []
        
        queries = [
            "合肥市 残疾人 就业补贴 2026",
            "安徽省 残疾人 就业扶持 政策"
        ]
        
        for query in queries:
            try:
                response = self.client.web_search(query=query, count=5)
                if response.web_items:
                    for item in response.web_items:
                        if ".gov.cn" in item.url or "残联" in item.site_name:
                            if not self.is_valid_result(item.title, item.snippet):
                                continue
                            date_str = item.publish_time[:10] if item.publish_time else ""
                            if not self.is_recent(date_str):
                                print(f"  跳过过期: {item.title[:30]}...")
                                continue
                            results.append({
                                "title": item.title,
                                "source": item.site_name,
                                "date": date_str,
                                "snippet": item.snippet[:100] if item.snippet else "",
                                "url": item.url
                            })
            except Exception as e:
                print(f"  搜索失败: {e}")
        
        # 去重
        seen = set()
        unique = []
        for r in results:
            if r["title"] not in seen:
                seen.add(r["title"])
                unique.append(r)
        
        print(f"  找到 {len(unique)} 条有效政策")
        return unique[:3]
    
    def search_bidding(self) -> List[Dict]:
        """搜索招标/外包信息 - 只要甲方发包的"""
        print("\n📄 搜索招标信息...")
        results = []
        
        # 只搜索甲方发包的关键词
        queries = [
            "数据标注外包 寻找团队 提供 项目",
            "外包需求 寻服务商 合作",
            "手工活外发 加工订单 长期"
        ]
        
        # 招标信息专属排除词（服务商推荐、排行榜等）
        BIDDING_EXCLUDE = [
            "承接", "寻求合作", "找活", "接单", "团队承接",
            "十大", "排行榜", "服务商排名", "哪家好", "值得托付"
        ]
        
        for query in queries:
            try:
                response = self.client.web_search(query=query, count=5)
                if response.web_items:
                    for item in response.web_items:
                        title = item.title.lower()
                        # 排除乙方找活和服务商推荐信息
                        if any(kw in title for kw in BIDDING_EXCLUDE):
                            print(f"  跳过无效: {item.title[:30]}...")
                            continue
                        if not self.is_valid_result(item.title, item.snippet):
                            continue
                        date_str = item.publish_time[:10] if item.publish_time else ""
                        if not self.is_recent(date_str):
                            print(f"  跳过过期: {item.title[:30]}...")
                            continue
                        results.append({
                            "title": item.title,
                            "source": item.site_name,
                            "date": date_str,
                            "snippet": item.snippet[:80] if item.snippet else "",
                            "url": item.url
                        })
            except Exception as e:
                print(f"  搜索失败: {e}")
        
        # 去重
        seen = set()
        unique = []
        for r in results:
            if r["title"] not in seen:
                seen.add(r["title"])
                unique.append(r)
        
        print(f"  找到 {len(unique)} 条有效招标")
        return unique[:6]
    
    def search_products(self) -> List[Dict]:
        """搜索产品信息 - 辅助设备、智能硬件、专用软件"""
        print("\n🛍️ 搜索产品信息...")
        results = []
        
        # 搜索关键词：新品发布、产品推荐、优惠活动
        queries = [
            "残疾人 辅助设备 新品发布 2026",
            "无障碍 智能硬件 助听器 假肢",
            "残疾人 专用软件 语音识别 读屏",
            "讯飞听见 语音转文字 残疾人",
            "助残科技 产品 推荐",
            "残疾人 智能轮椅 盲文显示器"
        ]
        
        for query in queries:
            try:
                response = self.client.web_search(query=query, count=5)
                if response.web_items:
                    for item in response.web_items:
                        title = item.title.lower()
                        # 排除无关内容
                        if any(kw in title for kw in ["招聘", "求职", "中标公告"]):
                            continue
                        if not self.is_valid_result(item.title, item.snippet):
                            continue
                        date_str = item.publish_time[:10] if item.publish_time else ""
                        if not self.is_recent(date_str):
                            print(f"  跳过过期: {item.title[:30]}...")
                            continue
                        results.append({
                            "title": item.title,
                            "source": item.site_name,
                            "date": date_str,
                            "snippet": item.snippet[:80] if item.snippet else "",
                            "url": item.url
                        })
            except Exception as e:
                print(f"  搜索失败: {e}")
        
        # 去重
        seen = set()
        unique = []
        for r in results:
            if r["title"] not in seen:
                seen.add(r["title"])
                unique.append(r)
        
        print(f"  找到 {len(unique)} 条有效产品")
        return unique[:5]
    
    def scan_all(self) -> Dict:
        """执行扫描"""
        print("=" * 60)
        print("合皖助联 - 就业市场扫描")
        print("=" * 60)
        
        return {
            "jobs": self.search_jobs(),
            "policy": self.search_policy(),
            "bidding": self.search_bidding(),
            "products": self.search_products(),
            "scan_time": datetime.now().isoformat()
        }


def format_message(data: Dict) -> str:
    """格式化消息：招聘 → 政策 → 招标 → 产品"""
    now = datetime.now()
    
    lines = [f"**📅 {now.year}年{now.month}月{now.day}日 合皖助联就业市场动态**", "", "---"]
    
    # ===== 招聘信息 =====
    lines.append("")
    lines.append("## 💼 招聘信息")
    lines.append("")
    if data.get("jobs"):
        for i, j in enumerate(data["jobs"], 1):
            lines.append(f"**{i}. {j['title']}**")
            if j.get('company'):
                lines.append(f"📍 {j['company']}")
            if j.get('snippet'):
                lines.append(f"📝 {j['snippet']}")
            lines.append(f"🔗 [查看详情]({j['url']})")
            lines.append("")
    else:
        lines.append("_暂无新招聘信息_")
        lines.append("")
    
    lines.append("---")
    
    # ===== 政策信息 =====
    lines.append("")
    lines.append("## 📋 政策信息")
    lines.append("")
    if data.get("policy"):
        for i, p in enumerate(data["policy"], 1):
            lines.append(f"**{i}. {p['title']}**")
            if p.get('source'):
                lines.append(f"📍 {p['source']}")
            if p.get('snippet'):
                lines.append(f"📝 {p['snippet']}")
            lines.append(f"🔗 [查看详情]({p['url']})")
            lines.append("")
    else:
        lines.append("_暂无新政策信息_")
        lines.append("")
    
    lines.append("---")
    
    # ===== 招标信息 =====
    lines.append("")
    lines.append("## 📄 招标信息")
    lines.append("")
    if data.get("bidding"):
        for i, b in enumerate(data["bidding"], 1):
            lines.append(f"**{i}. {b['title']}**")
            if b.get('source'):
                lines.append(f"📍 {b['source']}")
            if b.get('snippet'):
                lines.append(f"📝 {b['snippet']}")
            lines.append(f"🔗 [查看详情]({b['url']})")
            lines.append("")
    else:
        lines.append("_暂无新招标信息_")
        lines.append("")
    
    lines.append("---")
    
    # ===== 产品信息 =====
    lines.append("")
    lines.append("## 🛍️ 产品信息")
    lines.append("")
    if data.get("products"):
        for i, pr in enumerate(data["products"], 1):
            lines.append(f"**{i}. {pr['title']}**")
            if pr.get('source'):
                lines.append(f"📍 {pr['source']}")
            if pr.get('snippet'):
                lines.append(f"📝 {pr['snippet']}")
            lines.append(f"🔗 [查看详情]({pr['url']})")
            lines.append("")
    else:
        lines.append("_暂无新产品信息_")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append(f"⏰ 扫描时间: {now.year}年{now.month}月{now.day}日 {now.hour:02d}:{now.minute:02d}")
    lines.append("")
    lines.append("📌 仅推送近30天内的有效信息")
    lines.append("")
    lines.append("🤖 合皖助联智能助手 | 每2天推送一次")
    
    return "\n".join(lines)


def push_to_feishu(data: Dict) -> bool:
    """推送到飞书"""
    content = format_message(data)
    
    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": "📊 合皖助联就业市场动态"},
                "template": "blue"
            },
            "elements": [{"tag": "div", "text": {"tag": "lark_md", "content": content}}]
        }
    }
    
    try:
        response = requests.post(FEISHU_WEBHOOK, json=payload, timeout=15)
        return response.json().get("StatusCode", -1) == 0
    except Exception as e:
        print(f"推送失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("合皖助联 - 就业市场动态推送")
    print("=" * 60)
    
    scanner = JobMarketScanner()
    data = scanner.scan_all()
    
    print("\n📤 推送到飞书群...")
    if push_to_feishu(data):
        print("✅ 推送成功！")
        # 保存历史
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({"last_push_time": datetime.now().isoformat()}, f)
    else:
        print("❌ 推送失败")


if __name__ == "__main__":
    main()
