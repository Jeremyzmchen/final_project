"""
库存管理器 - 管理所有物品的位置和状态 (沉重手感版)
"""

import pygame
import random
import math
from config.settings import DESK_AREA, STORAGE_AREA

class InventoryManager:
    """库存管理器"""

    def __init__(self):
        self.desk_items = []
        self.storage_items = []

    def add_item_to_desk(self, item):
        item.in_storage = False
        # 刚放下时，几乎不给旋转，更稳重
        item.va = random.uniform(-0.2, 0.2)
        self.desk_items.append(item)

    def add_item_to_storage(self, item):
        item.in_storage = True
        item.angle = 0
        item.rotate(0)
        self.storage_items.append(item)
        if item in self.desk_items:
            self.desk_items.remove(item)

    def bring_to_front(self, item):
        if item in self.desk_items:
            self.desk_items.remove(item)
            self.desk_items.append(item)
        elif item in self.storage_items:
            self.storage_items.remove(item)
            self.storage_items.append(item)

    def move_to_storage(self, item):
        if item in self.desk_items:
            self.desk_items.remove(item)
            self.add_item_to_storage(item)
            self._organize_storage()

    def move_to_desk(self, item, x, y):
        if item in self.storage_items:
            self.storage_items.remove(item)
            item.set_position(x, y)
            self.add_item_to_desk(item)

    def _organize_storage(self):
        grid_size = 70
        padding = 10
        items_per_row = 3
        for i, item in enumerate(self.storage_items):
            row = i // items_per_row
            col = i % items_per_row
            x = STORAGE_AREA['x'] + padding + col * grid_size
            y = STORAGE_AREA['y'] + padding + row * grid_size
            item.set_position(x, y)
            item.vx = 0
            item.vy = 0

    def remove_item(self, item):
        if item in self.desk_items:
            self.desk_items.remove(item)
        if item in self.storage_items:
            self.storage_items.remove(item)

    def get_item_at_position(self, pos):
        for item in reversed(self.desk_items):
            if item.contains_point(pos):
                return item
        for item in reversed(self.storage_items):
            if item.contains_point(pos):
                return item
        return None

    def get_all_items(self):
        return self.desk_items + self.storage_items

    def is_position_in_desk(self, pos):
        x, y = pos
        return (DESK_AREA['x'] <= x <= DESK_AREA['x'] + DESK_AREA['width'] and
                DESK_AREA['y'] <= y <= DESK_AREA['y'] + DESK_AREA['height'])

    def is_position_in_storage(self, pos):
        x, y = pos
        return (STORAGE_AREA['x'] <= x <= STORAGE_AREA['x'] + STORAGE_AREA['width'] and
                STORAGE_AREA['y'] <= y <= STORAGE_AREA['y'] + STORAGE_AREA['height'])

    def render(self, screen):
        for item in self.storage_items:
            item.render(screen)
        for item in self.desk_items:
            item.render(screen)

    # --- 核心：物理更新 ---

    def update(self, dt):
        """更新库存中所有物品的物理状态"""

        # 1. 更新位置
        for item in self.desk_items:
            item.update_physics(dt)

            # 边界检查
            desk_rect = pygame.Rect(DESK_AREA['x'], DESK_AREA['y'], DESK_AREA['width'], DESK_AREA['height'])
            if not desk_rect.contains(item.get_rect()):
                # 碰到边界几乎完全吸能，不再反弹乱跳
                if item.x < desk_rect.left:
                    item.x = desk_rect.left
                    item.vx = 0
                elif item.x + item.width > desk_rect.right:
                    item.x = desk_rect.right - item.width
                    item.vx = 0

                if item.y < desk_rect.top:
                    item.y = desk_rect.top
                    item.vy = 0
                elif item.y + item.height > desk_rect.bottom:
                    item.y = desk_rect.bottom - item.height
                    item.vy = 0

                item.set_position(item.x, item.y)

        # 2. 碰撞挤开逻辑
        # [关键修改] 配合高阻尼，推力稍微给一点点劲
        push_strength = 0.3

        for i, item_a in enumerate(self.desk_items):
            for item_b in self.desk_items[i+1:]:
                if item_a.is_selected or item_b.is_selected:
                    continue

                rect_a = item_a.get_rect()
                rect_b = item_b.get_rect()

                hit_rect_a = rect_a.inflate(-5, -5)
                hit_rect_b = rect_b.inflate(-5, -5)

                if hit_rect_a.colliderect(hit_rect_b):
                    center_a = pygame.math.Vector2(rect_a.center)
                    center_b = pygame.math.Vector2(rect_b.center)

                    diff = center_a - center_b
                    dist = diff.length()

                    if dist == 0:
                        force = pygame.math.Vector2(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
                    else:
                        force = diff.normalize()

                    push_force = force * push_strength

                    item_a.vx += push_force.x
                    item_a.vy += push_force.y

                    item_b.vx -= push_force.x
                    item_b.vy -= push_force.y

                    # [关键修改] 极小的旋转力，甚至可以设为0
                    spin = random.uniform(-0.05, 0.05)
                    item_a.va += spin
                    item_b.va -= spin