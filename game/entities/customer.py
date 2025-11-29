"""
顾客实体 - 多顾客并行版
"""

import pygame
import random
from config.settings import *
from game.ui.button import Button

class Customer:
    """顾客类"""

    def __init__(self, sought_item_type, difficulty='normal', target_x=WINDOW_WIDTH//2):
        """
        初始化顾客
        Args:
            sought_item_type: 寻找的物品类型
            difficulty: 当前游戏难度
            target_x: 目标站位的X坐标
        """
        self.sought_item_type = sought_item_type
        self.item_data = ITEM_DESCRIPTIONS.get(sought_item_type, {})
        self.difficulty = difficulty

        self.description = self._generate_description()

        base_patience = CUSTOMER_WAIT_TIME
        if difficulty == 'chill': self.max_wait_time = base_patience * 1.5
        elif difficulty == 'relax': self.max_wait_time = base_patience * 1.2
        elif difficulty == 'mayhem': self.max_wait_time = base_patience * 0.7
        else: self.max_wait_time = base_patience

        self.wait_time = 0
        self.patience = 1.0

        # --- 位置与运动 ---
        self.x = target_x
        self.y = -200  # 起始位置
        self.target_y = CUSTOMER_Y # 120
        self.speed = 300

        self.state = 'walking_in'
        self.image = None
        self._load_image()
        self.dialog_visible = False

        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)

        # --- [新增] 自带拒绝按钮 ---
        # 按钮位置会在 update 里根据顾客位置动态更新
        self.reject_button = Button(0, 0, 60, 40, "NO", None)
        # 标记该顾客是否应被移除
        self.should_leave = False
        # 记录离开原因 (timeout, wrong, correct, reject)
        self.leave_reason = None

    @property
    def is_arrived(self):
        return self.state == 'waiting'

    def get_delivery_rect(self):
        """获取交付区域 (用于判断物品拖拽)"""
        # 以顾客为中心的一个区域
        return pygame.Rect(self.x - 100, self.y - 100, 200, 250)

    def _generate_description(self):
        keywords = self.item_data.get('keywords', [])
        if not keywords: return "I lost something..."
        num_keywords = random.randint(1, min(3, len(keywords)))
        selected_keywords = random.sample(keywords, num_keywords)
        descriptions = [
            f"I lost my {selected_keywords[0]}",
            f"Looking for {', '.join(selected_keywords[:2])}",
            f"Seen my {selected_keywords[0]}?",
            f"My {self.item_data.get('name', 'item')} missing",
        ]
        return random.choice(descriptions)

    def _load_image(self):
        try:
            customer_images = ['customer_1', 'customer_2', 'customer_3']
            image_key = random.choice(customer_images)
            if image_key in ASSETS:
                image_path = ASSETS[image_key]
                self.image = pygame.image.load(image_path)
                self.image = pygame.transform.scale(self.image, (250, 250)) #稍微缩小一点适应多人
                return
        except Exception: pass

        self.image = pygame.Surface((100, 100))
        self.image.fill((150, 150, 200))
        pygame.draw.circle(self.image, (255, 200, 150), (50, 50), 40)

    def update(self, dt):
        """更新顾客状态"""
        if self.state == 'walking_in':
            self.y += self.speed * dt
            if self.y >= self.target_y:
                self.y = self.target_y
                self.state = 'waiting'
                self.dialog_visible = True

        elif self.state == 'waiting':
            self.wait_time += dt
            self.patience = max(0, 1.0 - (self.wait_time / self.max_wait_time))

            # 更新按钮位置 (放在对话框右下角)
            dialog_x = self.x - 120
            dialog_y = 200
            self.reject_button.rect.topleft = (dialog_x + 180, dialog_y + 70)
            self.reject_button.update(pygame.mouse.get_pos())

    def is_timeout(self):
        return self.wait_time >= self.max_wait_time

    def check_item_match(self, item):
        return item.item_type == self.sought_item_type

    def get_patience_color(self):
        if self.patience > 0.6: return COLOR_GREEN
        elif self.patience > 0.3: return COLOR_YELLOW
        else: return COLOR_RED

    def render(self, screen):
        if self.image:
            image_rect = self.image.get_rect(center=(self.x, self.y))
            screen.blit(self.image, image_rect)

        # 调试：绘制交付区域框
        # pygame.draw.rect(screen, (0, 255, 0), self.get_delivery_rect(), 1)

        if self.dialog_visible:
            # 对话框稍微做小一点，适配3个并排
            dialog_width = 240
            dialog_height = 120
            dialog_x = self.x - dialog_width // 2
            dialog_y = 200

            # 气泡背景
            pygame.draw.rect(screen, COLOR_WHITE, (dialog_x, dialog_y, dialog_width, dialog_height), border_radius=10)
            pygame.draw.rect(screen, COLOR_BLACK, (dialog_x, dialog_y, dialog_width, dialog_height), 2, border_radius=10)

            # 文字
            lines = self._wrap_text(self.description, self.font, dialog_width - 20)
            y_offset = dialog_y + 15
            for line in lines:
                text = self.font.render(line, True, COLOR_BLACK)
                text_rect = text.get_rect(centerx=dialog_x + dialog_width//2, y=y_offset)
                screen.blit(text, text_rect)
                y_offset += 25

            # 耐心条
            bar_w = dialog_width - 80 # 留出按钮位置
            bar_x = dialog_x + 10
            bar_y = dialog_y + dialog_height - 20

            pygame.draw.rect(screen, COLOR_DARK_GRAY, (bar_x, bar_y, bar_w, 10), border_radius=5)
            fill = int(bar_w * self.patience)
            if fill > 0:
                pygame.draw.rect(screen, self.get_patience_color(), (bar_x, bar_y, fill, 10), border_radius=5)

            # 绘制自带的拒绝按钮
            self.reject_button.render(screen)

    def _wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line: lines.append(' '.join(current_line))
                current_line = [word]
        if current_line: lines.append(' '.join(current_line))
        return lines if lines else [text]