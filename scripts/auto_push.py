"""
自动推送脚本
每2天执行一次，推送提醒消息到飞书
"""
from datetime import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import WEBSITES, BUSINESS_TYPES, TARGET_COMPANIES
from src.tools.feishu import send_message


def generate_report() -> str:
    """
    生成推送报告
    
    Returns:
        Markdown 格式的报告内容
    """
    now = datetime.now()
    
    # 网站列表
    websites_md = "\n".join([f"{i+1}. [{w['name']}]({w['url']})" for i, w in enumerate(WEBSITES)])
    
    # 业务类型
    business_md = "\n".join([f"- {b}" for b in BUSINESS_TYPES])
    
    # 目标公司
    companies_md = "、".join(TARGET_COMPANIES)
    
    content = f"""**📅 {now.year}年{now.month}月{now.day}日 定期提醒**

---

**🔍 请查看以下招标网站**

{websites_md}

搜索关键词：数据服务、外包、招标

---

**📌 重点关注业务**

{business_md}

---

**💡 合作目标公司**

{companies_md}

建议主动联系询问外包需求

---

**📋 最近操作建议**

1. 检查各网站最新招标公告
2. 关注数据标注类采购项目
3. 联系目标公司业务部门

---
⏰ 推送时间: {now.year}年{now.month}月{now.day}日 {now.hour:02d}:{now.minute:02d}
🤖 合皖助联智能助手
📌 频率: 每2天推送一次"""
    
    return content


def main():
    """主函数"""
    print("=" * 50)
    print("开始执行自动推送...")
    print("=" * 50)
    
    # 生成报告
    print("生成报告...")
    content = generate_report()
    
    # 推送到飞书
    print("推送到飞书...")
    success = send_message("📊 合肥市残疾人就业市场提醒", content)
    
    if success:
        print("✅ 推送成功!")
    else:
        print("❌ 推送失败!")
        return 1
    
    print("=" * 50)
    return 0


if __name__ == "__main__":
    exit(main())
