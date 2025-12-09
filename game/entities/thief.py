# 文件: LBF/game/entities/thief.py

import pygame
import random
from game.entities.customer import Customer
from config.settings import ASSETS, THIEF_WAIT_TIME, THIEF_HP, COLOR_RED


class Thief(Customer):
    """
    小偷实体 (独立逻辑版)
    - 不再随机生成需求，而是固定行为。
    - 拥有 HP (喷雾点击次数)。
    - 独立的等待时间。
    """

    def __init__(self, target_x):
        # 1. 初始化基础位置和移动逻辑 (借用父类代码)
        # 传入 'thief' 作为 item_type 占位，反正我们不查字典
        super().__init__('thief', target_x)

        # 2. [核心修改] 覆盖父类属性，实现独立配置
        self.max_wait_time = THIEF_WAIT_TIME  # 独立的等待时间
        self.wait_time = 0
        self.patience = 1.0

        # 3. 小偷的血量 (点击次数)
        self.hp = THIEF_HP
        self.is_leaving = False  # 被喷跑的状态

        # 4. 强制加载小偷图片
        self._load_thief_image()

        # 5. [重要] 隐藏父类的 "Don't Have" 按钮
        # 我们把按钮移到屏幕外，确保玩家点不到
        if self.reject_button:
            self.reject_button.rect.topleft = (-9999, -9999)

    def update(self, dt):
        """
        [关键修复] 重写 update 方法。
        父类的 update 会每一帧把按钮位置重置回顾客下巴下面。
        所以我们必须在这里再次强制把它移走。
        """
        # 1. 先让父类处理移动和耐心值
        super().update(dt)

        # 2. 再次强制隐藏按钮 (覆盖父类的定位逻辑)
        if self.reject_button:
            self.reject_button.rect.topleft = (-9999, -9999)

    def _load_thief_image(self):
        try:
            path = ASSETS.get('thief', 'assets/images/thief.png')
            img = pygame.image.load(path)
            self.image = pygame.transform.scale(img, (375, 470))
        except Exception as e:
            print(f"Failed to load the conveyor belt image: {e}")

    def _generate_description(self):
        """小偷的台词"""
        return "Bro, give me money!!!"

    def take_damage(self):
        """
        被喷雾击中一次。
        返回: True (如果血量归零，应该滚蛋), False (还没死)
        """
        self.hp -= 1

        # 这里可以加个简单的受击反馈，比如改一下 description
        self.description = f"Ouch! ({self.hp} left)"

        if self.hp <= 0:
            return True
        return False

    def check_item_match(self, item):
        """小偷不仅不买东西，给他东西还会导致被盗 (逻辑在 GameplayState 处理)"""
        return True

    # 保持 update 和 render 复用父类的，这样移动动画和气泡显示都不用重写