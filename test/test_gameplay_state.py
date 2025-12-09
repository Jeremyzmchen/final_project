import unittest
import sys
import os
from unittest.mock import MagicMock

# ==========================================
# 1. 基础配置 (路径修复 + 屏蔽 Pygame)
# ==========================================
# 修复路径，确保能找到 game 文件夹
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# 全局 Mock Pygame (核武器级屏蔽，防止报错)
mock_pygame = MagicMock()
sys.modules['pygame'] = mock_pygame
sys.modules['pygame.mixer'] = mock_pygame.mixer
sys.modules['pygame.image'] = mock_pygame.image
sys.modules['pygame.font'] = mock_pygame.font
sys.modules['pygame.mouse'] = mock_pygame.mouse

# 导入你的类
try:
    from game.states.gameplay_state import GameplayState
except ImportError:
    # 兼容直接在 IDE 打开的情况
    from game.states.gameplay_state import GameplayState


# ==========================================
# 2. 测试类定义
# ==========================================
class TestGameplayState(unittest.TestCase):

    def setUp(self):
        """每个测试前自动运行：初始化环境"""
        self.mock_game_manager = MagicMock()
        self.game = GameplayState(self.mock_game_manager)

        # 重置关键组件的 Mock，方便统计调用次数
        self.game.sfx_money = MagicMock()
        self.game.sfx_deny = MagicMock()
        self.game._remove_customer = MagicMock()

        # 初始金钱归零，方便计算
        self.game.money = 0

    def test_delivery_correct_item(self):
        """测试 1: 给对物品 -> 加钱 + 播放金币音效"""
        print("\n正在测试: 顾客收到正确物品...")

        # 1. 准备 (Arrange)
        # 模拟一个顾客，强制让他说“我对这个物品满意”
        customer = MagicMock()
        customer.check_item_match.return_value = True

        item = MagicMock()

        # 2. 执行 (Act)
        self.game._handle_delivery(customer, item)

        # 3. 验证 (Assert)
        # 验证钱变多了 (假设 REWARD_CORRECT 是正数)
        self.assertGreater(self.game.money, 0, "错误：交付正确物品应该加钱")

        # 验证播放了 'cha-ching' 音效
        self.game.sfx_money.play.assert_called_once()

        # 验证顾客被移除了 (交易完成)
        self.game._remove_customer.assert_called_with(customer)
        print("Pass: ✅")

    def test_delivery_wrong_item(self):
        """测试 2: 给错物品 -> 扣钱 + 播放拒绝音效"""
        print("\n正在测试: 顾客收到错误物品...")

        # 1. 准备
        # 模拟一个顾客，强制让他说“我不想要这个”
        customer = MagicMock()
        customer.check_item_match.return_value = False

        item = MagicMock()

        # 2. 执行
        self.game._handle_delivery(customer, item)

        # 3. 验证
        # 验证钱变少了 (或者是加上了一个负数的惩罚值)
        self.assertLess(self.game.money, 0, "错误：交付错误物品应该扣钱")

        # 验证播放了 'buzz' 音效
        self.game.sfx_deny.play.assert_called_once()

        # 验证顾客没有被移除 (应该还在原地生气)
        self.game._remove_customer.assert_not_called()
        print("Pass: ✅")

    def test_customer_timeout(self):
        """测试 3: 顾客等太久 -> 扣钱 + 离开"""
        print("\n正在测试: 顾客超时离场...")

        # 1. 准备
        customer = MagicMock()
        customer.is_timeout.return_value = True  # 模拟时间到了

        # 把这个假顾客塞进列表里
        self.game.customers = [customer]

        # 2. 执行 (这里我们调用 update，模拟游戏过了一帧)
        dt = 0.1
        self.game.update(dt)

        # 3. 验证
        # 验证钱变少了 (超时惩罚)
        self.assertLess(self.game.money, 0, "错误：顾客超时应该扣钱")

        # 验证顾客被移除了
        self.game._remove_customer.assert_called_with(customer)
        print("Pass: ✅")


if __name__ == '__main__':
    unittest.main()