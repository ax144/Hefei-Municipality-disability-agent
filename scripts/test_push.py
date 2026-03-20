"""
手动测试推送脚本
用于本地测试飞书推送功能
"""
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.feishu import get_bot


def test_basic_push():
    """测试基础推送"""
    print("\n1️⃣ 测试基础推送...")
    bot = get_bot()
    
    result = bot.send_text("🧪 这是一条测试消息")
    
    if bot.is_success(result):
        print("   ✅ 文本消息推送成功")
        return True
    else:
        print(f"   ❌ 推送失败: {result}")
        return False


def test_card_push():
    """测试卡片推送"""
    print("\n2️⃣ 测试卡片推送...")
    bot = get_bot()
    
    now = datetime.now()
    content = f"""**🧪 测试卡片消息**

这是一条测试消息，用于验证飞书推送功能。

---

**测试信息**
- 时间: {now.year}年{now.month}月{now.day}日 {now.hour:02d}:{now.minute:02d}:{now.second:02d}
- 状态: 正常

---

✅ 如果您收到此消息，说明推送功能正常工作！"""
    
    result = bot.send_card(title="🧪 合皖助联测试推送", content=content)
    
    if bot.is_success(result):
        print("   ✅ 卡片消息推送成功")
        return True
    else:
        print(f"   ❌ 推送失败: {result}")
        return False


def test_report_push():
    """测试完整报告推送"""
    print("\n3️⃣ 测试完整报告推送...")
    
    # 导入自动推送模块
    from auto_push import generate_report
    from src.tools.feishu import send_message
    
    content = generate_report()
    success = send_message("📊 测试报告推送", content)
    
    if success:
        print("   ✅ 完整报告推送成功")
        return True
    else:
        print("   ❌ 推送失败")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("       合皖助联 - 飞书推送测试")
    print("=" * 60)
    
    results = []
    
    # 运行测试
    results.append(("基础推送", test_basic_push()))
    results.append(("卡片推送", test_card_push()))
    results.append(("报告推送", test_report_push()))
    
    # 输出结果
    print("\n" + "=" * 60)
    print("       测试结果汇总")
    print("=" * 60)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    print("=" * 60)
    if all_passed:
        print("✅ 所有测试通过!")
    else:
        print("❌ 部分测试失败!")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
