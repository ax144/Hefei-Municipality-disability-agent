"""
飞书推送工具
支持发送文本、卡片消息
"""
import requests
from typing import Optional, Dict, Any
from datetime import datetime


class FeishuBot:
    """飞书机器人"""
    
    def __init__(self, webhook: str):
        self.webhook = webhook
        self.headers = {"Content-Type": "application/json"}
    
    def send_text(self, text: str) -> Dict[str, Any]:
        """
        发送文本消息
        
        Args:
            text: 文本内容
        
        Returns:
            飞书返回结果
        """
        payload = {
            "msg_type": "text",
            "content": {"text": text}
        }
        response = requests.post(self.webhook, json=payload, headers=self.headers, timeout=15)
        return response.json()
    
    def send_card(self, title: str, content: str, color: str = "blue") -> Dict[str, Any]:
        """
        发送卡片消息
        
        Args:
            title: 卡片标题
            content: 卡片内容（支持Markdown）
            color: 卡片颜色
        
        Returns:
            飞书返回结果
        """
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": title},
                    "template": color
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {"tag": "lark_md", "content": content}
                    }
                ]
            }
        }
        response = requests.post(self.webhook, json=payload, headers=self.headers, timeout=15)
        return response.json()
    
    def is_success(self, result: Dict[str, Any]) -> bool:
        """检查是否发送成功"""
        return result.get("StatusCode", -1) == 0


# 默认机器人实例
_bot: Optional[FeishuBot] = None


def get_bot(webhook: Optional[str] = None) -> FeishuBot:
    """
    获取飞书机器人实例
    
    Args:
        webhook: Webhook URL，不传则使用配置文件中的
    
    Returns:
        FeishuBot 实例
    """
    global _bot
    if _bot is None or webhook:
        if webhook is None:
            from config import FEISHU_WEBHOOK
            webhook = FEISHU_WEBHOOK
        _bot = FeishuBot(webhook)
    return _bot


def send_message(title: str, content: str) -> bool:
    """
    发送卡片消息（简化接口）
    
    Args:
        title: 标题
        content: 内容
    
    Returns:
        是否成功
    """
    bot = get_bot()
    result = bot.send_card(title, content)
    return bot.is_success(result)


# 测试代码
if __name__ == "__main__":
    print("测试飞书推送...")
    bot = get_bot()
    
    result = bot.send_card(
        title="🧪 测试推送",
        content=f"**测试消息**\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    if bot.is_success(result):
        print("✅ 推送成功!")
    else:
        print(f"❌ 推送失败: {result}")
