"""
配置文件
"""

# 飞书机器人 Webhook URL
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/38880b0c-a886-4461-a929-50f021961ec3"

# 推送时间设置
PUSH_HOUR = 9  # 北京时间上午9点

# 重点关注网站
WEBSITES = [
    {"name": "安徽省公共资源交易中心", "url": "https://ggzy.ah.gov.cn"},
    {"name": "合肥市公共资源交易中心", "url": "https://ggzy.hefei.gov.cn"},
    {"name": "安徽招标网", "url": "https://ah.bidcenter.com.cn"},
]

# 重点关注业务
BUSINESS_TYPES = [
    "切扫分（图书扫描）",
    "数据标注",
    "数据录入", 
    "内容审核",
    "文本标注",
]

# 合作目标公司
TARGET_COMPANIES = [
    "科大讯飞",
    "作业帮",
    "小猿搜题",
    "字节跳动",
]
