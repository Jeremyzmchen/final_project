"""
物品实体 - 代表失物招领处的各种物品
"""

import pygame
from config.settings import ITEM_SIZE, ITEM_DESCRIPTIONS, ASSETS, COLOR_WHITE

class Item:
    """物品类"""

    def __init__(self, item_type):
        """初始化物品"""
        self.item_type = item_type
        self.data = ITEM_DESCRIPTIONS.get(item_type, {})
        self.name = self.data.get('name', 'Unknown Item')
        self.keywords = self.data.get('keywords', [])
        self.category = self.data.get('category', 'unknown')

        # 位置和尺寸
        self.x = 0
        self.y = 0
        self.width = ITEM_SIZE[0]
        self.height = ITEM_SIZE[1]

        # 视觉
        self.image = None
        self._load_image()

        # 状态
        self.is_selected = False
        self.in_storage = False

        # 传送带状态
        self.on_conveyor = False
        self.conveyor_progress = 0
        self.conveyor_start_offset = 0
        self.conveyor_vertical_offset = 0
        self.item_index = 0
        self.batch_id = 0

    def _load_image(self):
        """加载物品图片"""
        try:
            image_key = f'item_{self.item_type}'
            if image_key in ASSETS:
                image_path = ASSETS[image_key]
                self.image = pygame.image.load(image_path)
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
                return
        except Exception as e:
            print(f"❌ 加载图片失败: {e}")

        # 占位符
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((100, 100, 200))
        font = pygame.font.Font(None, 16)
        text = font.render(self.item_type[:8], True, COLOR_WHITE)
        text_rect = text.get_rect(center=(self.width//2, self.height//2))
        self.image.blit(text, text_rect)

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def get_position(self):
        return (self.x, self.y)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update_conveyor_movement(self, dt, speed, path, pause_flag=None):
        """更新传送带移动"""
        if not self.on_conveyor:
            return True

        # 检查暂停
        if pause_flag and pause_flag.get('paused', False):
            return False

        old_y = self.y

        # 更新进度
        self.conveyor_progress += dt
        time_offset = self.conveyor_start_offset / speed
        effective_time = self.conveyor_progress - time_offset

        if effective_time < 0:
            return False

        # 计算路径距离
        segment_distances = [0]
        for i in range(len(path) - 1):
            dx = path[i+1][0] - path[i][0]
            dy = path[i+1][1] - path[i][1]
            length = (dx * dx + dy * dy) ** 0.5
            segment_distances.append(segment_distances[-1] + length)

        total_distance = segment_distances[-1]
        current_distance = effective_time * speed

        if current_distance > total_distance + 100:
            return True

        # 找到当前路径段
        current_segment = 0
        for i in range(len(segment_distances) - 1):
            if current_distance < segment_distances[i + 1]:
                current_segment = i
                break
        else:
            current_segment = len(path) - 2

        # 计算位置
        start_point = path[current_segment]
        end_point = path[current_segment + 1]
        segment_start_distance = segment_distances[current_segment]
        segment_length = segment_distances[current_segment + 1] - segment_start_distance

        if segment_length == 0:
            segment_progress = 0
        else:
            distance_in_segment = current_distance - segment_start_distance
            segment_progress = distance_in_segment / segment_length
            segment_progress = max(0, min(1, segment_progress))

        base_x = start_point[0] + (end_point[0] - start_point[0]) * segment_progress
        base_y = start_point[1] + (end_point[1] - start_point[1]) * segment_progress

        # 计算偏移系数（确保跨段连续）
        offset_factor = 0

        if current_segment == 0:
            # 水平进入段后60%开始过渡
            if segment_progress > 0.6:
                offset_factor = (segment_progress - 0.6) / 0.4  # 0.6→1.0映射到0→1
        elif current_segment == 1:
            # 转角：从上一段的结束值继续（不是从0开始！）
            # 段0结束时offset_factor已经是1了，段1应该保持1
            offset_factor = 1.0
        elif 2 <= current_segment <= 5:
            # 垂直段：完全偏移
            offset_factor = 1.0
        elif current_segment == 6:
            # 转角退出：从1逐渐到0
            offset_factor = 1.0 - segment_progress
        elif current_segment == 7:
            # 水平离开：继续从上一段的结束值减少
            if segment_progress < 0.4:
                offset_factor = 0  # 段6已经减到0了
            else:
                offset_factor = 0

        # 应用偏移
        smooth_offset = self.conveyor_vertical_offset * offset_factor
        self.x = base_x - self.width // 2
        self.y = base_y + smooth_offset - self.height // 2

        # 调试
        y_change = self.y - old_y
        if abs(y_change) > 25 and effective_time > 1:
            print(f"⚠️ 物品{self.item_index+1} 跳变:")
            print(f"   段:{current_segment}, 进度:{segment_progress:.3f}")
            print(f"   base_y:{base_y:.1f}, 偏移值:{self.conveyor_vertical_offset}, 系数:{offset_factor:.3f}")
            print(f"   平滑偏移:{smooth_offset:.1f}, old_y:{old_y:.1f}, new_y:{self.y:.1f}")

        return False

    def contains_point(self, point):
        return self.get_rect().collidepoint(point)

    def matches_keywords(self, keywords):
        if not keywords:
            return 0
        matches = sum(1 for kw in keywords if kw in self.keywords)
        return matches / len(keywords)

    def render(self, screen, alpha=255):
        if self.image:
            if alpha < 255:
                temp = self.image.copy()
                temp.set_alpha(alpha)
                screen.blit(temp, (self.x, self.y))
            else:
                screen.blit(self.image, (self.x, self.y))

        if self.is_selected:
            pygame.draw.rect(screen, (255, 255, 0),
                           (self.x, self.y, self.width, self.height), 3)

    def __repr__(self):
        return f"Item({self.item_type})"