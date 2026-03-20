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

# 招标搜索关键词
BID_KEYWORDS = [
    "安徽省 数据标注 招标",
    "合肥市 数据服务 外包 招标",
    "安徽省 数字化建设 采购",
    "合肥市 内容审核 外包 招标",
    "安徽省 数据录入 服务 采购",
    "合肥市 档案数字化 招标",
]

# 招聘搜索关键词（适合残疾人）
JOB_KEYWORDS = [
    "合肥市 残疾人 招聘",
    "合肥市 数据标注 招聘",
    "安徽省 内容审核 招聘",
    "合肥市 文员 残疾人",
    "安徽省 客服 居家办公",
    "合肥市 数据录入 兼职",
]

# 政府采购网站
GOV_WEBSITES = [
    {"name": "安徽省公共资源交易中心", "url": "http://ggzy.ah.gov.cn"},
    {"name": "合肥市公共资源交易中心", "url": "http://ggzy.hefei.gov.cn"},
    {"name": "安徽招标网", "url": "http://ah.bidcenter.com.cn"},
]

# 招聘网站
JOB_WEBSITES = [
    {"name": "安徽公共招聘网", "url": "https://www.ah.gov.cn"},
    {"name": "合肥市人力资源和社会保障局", "url": "https://rsj.hefei.gov.cn"},
    {"name": "安徽省残疾人就业服务中心", "url": "https://cdpf.ah.gov.cn"},
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
        print(f"搜索失败: {e}")
    
    return results


def generate_report() -> str:
    """生成推送报告"""
    now = datetime.now()
    
    # 搜索招标信息
    print("正在搜索招标信息...")
    bid_results = []
    for keyword in BID_KEYWORDS[:3]:
        results = search_with_bing_api(keyword)
        bid_results.extend(results)
    
    # 搜索招聘信息
    print("正在搜索招聘信息...")
    job_results = []
    for keyword in JOB_KEYWORDS[:3]:
        results = search_with_bing_api(keyword)
        job_results.extend(results)
    
    # 构建报告
    content_parts = [
        f"**📅 {now.year}年{now.month}月{now.day}日 扫描报告**",
        "",
        "---",
        "",
        "## 📋 招标信息",
        ""
    ]
    
    if bid_results:
        for i, item in enumerate(bid_results[:5], 1):
            content_parts.append(f"**{i}. [{item['title'][:50]}]({item['url']})**")
            content_parts.append(f"   {item['snippet']}")
            content_parts.append("")
    else:
        content_parts.append("> 请手动检查以下招标网站：")
        content_parts.append("")
        for site in GOV_WEBSITES:
            content_parts.append(f"- [{site['name']}]({site['url']})")
        content_parts.append("")
        content_parts.append("**搜索关键词：**")
        for kw in BID_KEYWORDS[:3]:
            content_parts.append(f"- `{kw}`")
        content_parts.append("")
    
    content_parts.extend([
        "---",
        "",
        "## 👥 招聘信息",
        ""
    ])
    
    if job_results:
        for i, item in enumerate(job_results[:5], 1):
            content_parts.append(f"**{i}. [{item['title'][:50]}]({item['url']})**")
            content_parts.append(f"   {item['snippet']}")
            content_parts.append("")
    else:
        content_parts.append("> 请手动检查以下招聘网站：")
        content_parts.append("")
        for site in JOB_WEBSITES:
            content_parts.append(f"- [{site['name']}]({site['url']})")
        content_parts.append("")
        content_parts.append("**搜索关键词：**")
        for kw in JOB_KEYWORDS[:3]:
            content_parts.append(f"- `{kw}`")
        content_parts.append("")
    
    content_parts.extend([
        "---",
        "",
        "## 💡 操作建议",
        "",
        "1. 访问上述网站查看详细信息",
        "2. 关注适合残疾人的岗位：数据标注、内容审核、数据录入等",
        "3. 如有合适项目，及时联系相关部门",
        "",
        "---",
        "",
        f"⏰ 扫描时间: {now.year}年{now.month}月{now.day}日 {now.hour:02d}:{now.minute:02d}",
        "",
        "🤖 合皖助联智能助手",
        "📌 每2天推送一次"
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
