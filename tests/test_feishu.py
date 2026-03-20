"""
单元测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.feishu import get_bot


def test_bot_creation():
    """测试机器人创建"""
    bot = get_bot()
    assert bot.webhook is not None
    assert bot.webhook.startswith("https://")
    print("✅ 机器人创建测试通过")


def test_send_text():
    """测试发送文本"""
    bot = get_bot()
    result = bot.send_text("测试消息")
    assert "StatusCode" in result
    print("✅ 文本发送测试通过")


def test_send_card():
    """测试发送卡片"""
    bot = get_bot()
    result = bot.send_card("测试标题", "测试内容")
    assert "StatusCode" in result
    print("✅ 卡片发送测试通过")


if __name__ == "__main__":
    test_bot_creation()
    test_send_text()
    test_send_card()
    print("\n✅ 所有测试通过!")
