"""
物品实体 - 代表失物招领处的各种物品 (沉重手感版)
"""

import pygame
import random
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

        target_size = self.data.get('size', ITEM_SIZE)
        self.width = target_size[0]
        self.height = target_size[1]

        self.x = 0
        self.y = 0

        # 物理属性
        self.angle = random.uniform(-5, 5) # 初始角度也稍微收敛一点
        self.vx = 0.0
        self.vy = 0.0
        self.va = 0.0

        # [关键修改] 摩擦力 0.6 (非常大的阻力)
        # 这会让物品被撞开后迅速停下，不会滑很远，感觉更"重"
        self.friction = 0.6
        self.mass = 1.0

        # 视觉
        self.image = None
        self.original_image = None
        self.rect = None
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

        self.rotate(0)

    def _load_image(self):
        try:
            image_key = f'item_{self.item_type}'
            if image_key in ASSETS:
                image_path = ASSETS[image_key]
                self.original_image = pygame.image.load(image_path)
                self.original_image = pygame.transform.scale(self.original_image, (self.width, self.height))
            else:
                raise Exception("Image key not found")
        except Exception as e:
            self.original_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.original_image.fill((100, 100, 200))
            font = pygame.font.Font(None, 16)
            text = font.render(self.item_type[:8], True, COLOR_WHITE)
            text_rect = text.get_rect(center=(self.width//2, self.height//2))
            self.original_image.blit(text, text_rect)

        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def set_position(self, x, y):
        self.x = x
        self.y = y
        if self.rect:
            self.rect.topleft = (int(x), int(y))

    def get_position(self):
        return (self.x, self.y)

    def get_rect(self):
        if self.rect:
            return self.rect
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def rotate(self, angle_change=0):
        self.angle = (self.angle + angle_change) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)

        if self.rect:
            old_center = self.rect.center
            self.rect = self.image.get_rect(center=old_center)
            self.x = self.rect.x
            self.y = self.rect.y
            self.width = self.rect.width
            self.height = self.rect.height
        else:
            self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def update_physics(self, dt):
        """更新物理状态"""
        if self.is_selected or self.on_conveyor or self.in_storage:
            self.vx = 0
            self.vy = 0
            self.va = 0
            return

        # 只有当速度大于一定阈值时才移动，防止微小抖动
        if abs(self.vx) > 0.1 or abs(self.vy) > 0.1:
            self.x += self.vx * dt * 60
            self.y += self.vy * dt * 60
            self.rect.topleft = (int(self.x), int(self.y))

            # 强阻尼衰减
            self.vx *= self.friction
            self.vy *= self.friction
        else:
            self.vx = 0
            self.vy = 0

        # 旋转阻尼
        if abs(self.va) > 0.1:
            self.rotate(self.va * dt * 60)
            self.va *= self.friction
        else:
            self.va = 0

    def update_conveyor_movement(self, dt, speed, path, pause_flag=None):
        if not self.on_conveyor: return True
        if pause_flag and pause_flag.get('paused', False): return False

        old_y = self.y
        self.conveyor_progress += dt
        time_offset = self.conveyor_start_offset / speed
        effective_time = self.conveyor_progress - time_offset
        if effective_time < 0: return False

        segment_distances = [0]
        for i in range(len(path) - 1):
            dx = path[i+1][0] - path[i][0]
            dy = path[i+1][1] - path[i][1]
            length = (dx * dx + dy * dy) ** 0.5
            segment_distances.append(segment_distances[-1] + length)

        total_distance = segment_distances[-1]
        current_distance = effective_time * speed

        if current_distance > total_distance + 100: return True

        current_segment = 0
        for i in range(len(segment_distances) - 1):
            if current_distance < segment_distances[i + 1]:
                current_segment = i
                break
        else:
            current_segment = len(path) - 2

        start_point = path[current_segment]
        end_point = path[current_segment + 1]
        segment_start_distance = segment_distances[current_segment]
        segment_length = segment_distances[current_segment + 1] - segment_start_distance

        if segment_length == 0: segment_progress = 0
        else:
            distance_in_segment = current_distance - segment_start_distance
            segment_progress = distance_in_segment / segment_length
            segment_progress = max(0, min(1, segment_progress))

        base_x = start_point[0] + (end_point[0] - start_point[0]) * segment_progress
        base_y = start_point[1] + (end_point[1] - start_point[1]) * segment_progress

        offset_factor = 0
        if current_segment == 0:
            if segment_progress > 0.6: offset_factor = (segment_progress - 0.6) / 0.4
        elif current_segment == 1: offset_factor = 1.0
        elif 2 <= current_segment <= 5: offset_factor = 1.0
        elif current_segment == 6: offset_factor = 1.0 - segment_progress
        elif current_segment == 7: offset_factor = 0

        smooth_offset = self.conveyor_vertical_offset * offset_factor
        self.x = base_x - self.width // 2
        self.y = base_y + smooth_offset - self.height // 2

        if self.rect:
            self.rect.topleft = (int(self.x), int(self.y))
        return False

    def contains_point(self, point):
        if self.rect:
            return self.rect.collidepoint(point)
        return self.get_rect().collidepoint(point)

    def matches_keywords(self, keywords):
        if not keywords: return 0
        matches = sum(1 for kw in keywords if kw in self.keywords)
        return matches / len(keywords)

    def render(self, screen, alpha=255):
        if self.image:
            render_rect = self.rect if self.rect else pygame.Rect(self.x, self.y, self.width, self.height)
            if alpha < 255:
                temp = self.image.copy()
                temp.set_alpha(alpha)
                screen.blit(temp, render_rect)
            else:
                screen.blit(self.image, render_rect)

        if self.is_selected:
            sel_rect = self.rect if self.rect else pygame.Rect(self.x, self.y, self.width, self.height)
            pygame.draw.rect(screen, (255, 255, 0), sel_rect, 3)

    def __repr__(self):
        return f"Item({self.item_type})"