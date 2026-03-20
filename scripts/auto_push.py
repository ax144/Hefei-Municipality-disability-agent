"""
自动推送脚本
搜索招标/招聘信息并推送到飞书
"""
import requests
from datetime import datetime
import os

# 配置
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")
BING_API_KEY = os.getenv("BING_API_KEY", "")

# 搜索关键词配置
SEARCH_KEYWORDS = {
    "招标": [
        "安徽省 数据标注 招标",
        "合肥市 数据服务 外包 招标",
        "安徽省 数字化建设 采购",
        "合肥市 内容审核 外包",
    ],
    "招聘": [
        "合肥市 残疾人招聘",
        "合肥市 数据标注 招聘",
    ]
}

# 政府采购网站
GOV_WEBSITES = [
    {"name": "安徽省公共资源交易中心", "url": "http://ggzy.ah.gov.cn"},
    {"name": "合肥市公共资源交易中心", "url": "http://ggzy.hefei.gov.cn"},
    {"name": "安徽招标网", "url": "http://ah.bidcenter.com.cn"},
]

# 重点关注业务类型
BUSINESS_TYPES = [
    "切扫分（图书扫描）",
    "数据标注",
    "数据录入",
    "内容审核",
    "文本标注",
    "2D/3D标注",
]

# 目标合作公司
TARGET_COMPANIES = [
    "科大讯飞",
    "作业帮",
    "小猿搜题",
    "字节跳动",
    "百度",
    "华为",
]


def search_with_bing_api(keyword: str) -> list:
    """使用 Bing Search API 搜索"""
    results = []
    
    if not BING_API_KEY:
        return results
    
    try:
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
        params = {"q": keyword, "count": 5, "mkt": "zh-CN"}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        
        if "webPages" in data:
            for item in data["webPages"]["value"][:5]:
                results.append({
                    "title": item.get("name", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("snippet", "")[:100]
                })
    except Exception as e:
        print(f"Bing API 搜索失败: {e}")
    
    return results


def generate_report() -> str:
    """生成推送报告"""
    now = datetime.now()
    
    # 尝试Bing API搜索
    all_bids = []
    for keyword in SEARCH_KEYWORDS["招标"][:2]:
        results = search_with_bing_api(keyword)
        all_bids.extend(results)
    
    # 构建报告
    content_parts = [
        f"**📅 {now.year}年{now.month}月{now.day}日 扫描报告**",
        "",
        "---",
        "",
        "## 🔍 请手动检查以下网站",
        ""
    ]
    
    # 网站列表
    for site in GOV_WEBSITES:
        content_parts.append(f"- [{site['name']}]({site['url']})")
    
    content_parts.extend([
        "",
        "**搜索关键词建议：**",
        ""
    ])
    
    for keyword in SEARCH_KEYWORDS["招标"][:4]:
        content_parts.append(f"- `{keyword}`")
    
    content_parts.extend([
        "",
        "---",
        "",
        "## 📌 重点关注业务",
        ""
    ])
    
    for biz in BUSINESS_TYPES:
        content_parts.append(f"- {biz}")
    
    content_parts.extend([
        "",
        "---",
        "",
        "## 🎯 目标合作公司",
        ""
    ])
    
    for company in TARGET_COMPANIES:
        content_parts.append(f"- {company}")
    
    content_parts.extend([
        "",
        "---",
        "",
        "## 💡 本周操作建议",
        "",
        "1. **检查政府网站**：访问上述招标网站搜索最新项目",
        "2. **联系目标公司**：主动询问外包需求",
        "3. **关注业务类型**：数据标注、内容审核等适合残疾人的岗位",
        "",
        "---",
        "",
        f"⏰ 推送时间: {now.year}年{now.month}月{now.day}日 {now.hour:02d}:{now.minute:02d}",
        "",
        "🤖 合皖助联智能助手",
        "",
        "📌 频率: 每2天推送一次",
        "",
        "---",
        "",
        "> ⚠️ 由于网络限制，请手动访问上述网站查看最新信息"
    ])
    
    return "\n".join(content_parts)


def send_to_feishu(title: str, content: str) -> bool:
    """发送消息到飞书"""
    if not FEISHU_WEBHOOK:
        print("❌ 未配置飞书Webhook!")
        return False
    
    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": content}
                }
            ]
        }
    }
    
    try:
        response = requests.post(FEISHU_WEBHOOK, json=payload, timeout=15)
        result = response.json()
        return result.get("StatusCode", -1) == 0
    except Exception as e:
        print(f"推送失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("开始执行信息扫描和推送...")
    print("=" * 60)
    
    # 生成报告
    print("\n正在生成推送报告...")
    report = generate_report()
    
    # 推送到飞书
    print("\n正在推送到飞书...")
    success = send_to_feishu("📊 合肥市残疾人就业市场提醒", report)
    
    if success:
        print("\n✅ 推送成功!")
        print("=" * 60)
        return 0
    else:
        print("\n❌ 推送失败!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    exit(main())
