"""
库存管理器 - 管理所有物品的位置和状态
"""

import pygame
from config.settings import DESK_AREA, STORAGE_AREA


class InventoryManager:
    """库存管理器 - 负责管理工作台和储物柜中的物品"""

    def __init__(self):
        """初始化库存管理器"""
        self.desk_items = []  # 工作台上的物品
        self.storage_items = []  # 储物柜中的物品

    def add_item_to_desk(self, item):
        """
        添加物品到工作台

        Args:
            item: Item对象
        """
        item.in_storage = False
        self.desk_items.append(item)

    def add_item_to_storage(self, item):
        """
        添加物品到储物柜

        Args:
            item: Item对象
        """
        item.in_storage = True
        self.storage_items.append(item)

        # 移除工作台上的物品
        if item in self.desk_items:
            self.desk_items.remove(item)

    def move_to_storage(self, item):
        """
        将物品从工作台移动到储物柜

        Args:
            item: Item对象
        """
        if item in self.desk_items:
            self.desk_items.remove(item)
            self.add_item_to_storage(item)

            # 自动整理储物柜位置
            self._organize_storage()

    def move_to_desk(self, item, x, y):
        """
        将物品从储物柜移动到工作台

        Args:
            item: Item对象
            x, y: 目标位置
        """
        if item in self.storage_items:
            self.storage_items.remove(item)
            item.set_position(x, y)
            self.add_item_to_desk(item)

    def _organize_storage(self):
        """自动整理储物柜中的物品排列"""
        grid_size = 70
        padding = 10
        items_per_row = 3

        for i, item in enumerate(self.storage_items):
            row = i // items_per_row
            col = i % items_per_row

            x = STORAGE_AREA['x'] + padding + col * grid_size
            y = STORAGE_AREA['y'] + padding + row * grid_size

            item.set_position(x, y)

    def remove_item(self, item):
        """
        从库存中完全移除物品（例如归还给顾客）

        Args:
            item: Item对象
        """
        if item in self.desk_items:
            self.desk_items.remove(item)
        if item in self.storage_items:
            self.storage_items.remove(item)

    def get_item_at_position(self, pos):
        """
        获取指定位置的物品

        Args:
            pos: (x, y) 坐标元组

        Returns:
            Item对象或None
        """
        # 先检查工作台（因为在上层）
        for item in reversed(self.desk_items):  # 从上往下查找
            if item.contains_point(pos):
                return item

        # 再检查储物柜
        for item in reversed(self.storage_items):
            if item.contains_point(pos):
                return item

        return None

    def get_all_items(self):
        """获取所有物品"""
        return self.desk_items + self.storage_items

    def search_items(self, keywords):
        """
        根据关键词搜索物品

        Args:
            keywords: 关键词列表

        Returns:
            匹配的物品列表，按匹配度排序
        """
        all_items = self.get_all_items()
        results = []

        for item in all_items:
            match_score = item.matches_keywords(keywords)
            if match_score > 0:
                results.append((item, match_score))

        # 按匹配度排序
        results.sort(key=lambda x: x[1], reverse=True)
        return [item for item, score in results]

    def is_position_in_desk(self, pos):
        """检查位置是否在工作台区域内"""
        x, y = pos
        return (DESK_AREA['x'] <= x <= DESK_AREA['x'] + DESK_AREA['width'] and
                DESK_AREA['y'] <= y <= DESK_AREA['y'] + DESK_AREA['height'])

    def is_position_in_storage(self, pos):
        """检查位置是否在储物柜区域内"""
        x, y = pos
        return (STORAGE_AREA['x'] <= x <= STORAGE_AREA['x'] + STORAGE_AREA['width'] and
                STORAGE_AREA['y'] <= y <= STORAGE_AREA['y'] + STORAGE_AREA['height'])

    def render(self, screen):
        """
        渲染所有物品

        Args:
            screen: Pygame屏幕对象
        """
        # 先渲染储物柜中的物品（在下层）
        for item in self.storage_items:
            item.render(screen)

        # 再渲染工作台上的物品（在上层）
        for item in self.desk_items:
            item.render(screen)

    def get_desk_item_count(self):
        """获取工作台物品数量"""
        return len(self.desk_items)

    def get_storage_item_count(self):
        """获取储物柜物品数量"""
        return len(self.storage_items)

    def clear_all(self):
        """清空所有物品"""
        self.desk_items.clear()
        self.storage_items.clear()