"""
顾客实体 - 代表来寻找失物的旅客
"""

import pygame
import random
from config.settings import *

class Customer:
    """顾客类"""

    def __init__(self, sought_item_type):
        """初始化顾客"""
        self.sought_item_type = sought_item_type
        self.item_data = ITEM_DESCRIPTIONS.get(sought_item_type, {})

        # 生成描述
        self.description = self._generate_description()

        # 时间和耐心
        self.wait_time = 0
        self.max_wait_time = CUSTOMER_WAIT_TIME
        self.patience = 1.0

        # 位置
        self.x = WINDOW_WIDTH // 2
        self.y = 120

        # 图像
        self.image = None
        self._load_image()

        # 对话框
        self.dialog_visible = True

        # 字体
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)

        print(f"🧑 顾客创建完成，图像是否加载: {self.image is not None}")

    def _generate_description(self):
        """生成物品描述"""
        keywords = self.item_data.get('keywords', [])

        if not keywords:
            return "I lost something..."

        num_keywords = random.randint(1, min(3, len(keywords)))
        selected_keywords = random.sample(keywords, num_keywords)

        descriptions = [
            f"I lost my {selected_keywords[0]} item",
            f"I'm looking for something {', '.join(selected_keywords[:2])}",
            f"Have you seen my {selected_keywords[0]}?",
            f"My {self.item_data.get('name', 'item')} is missing",
        ]

        return random.choice(descriptions)

    def _load_image(self):
        """加载顾客图片"""
        print(f"🔍 开始加载顾客图片...")
        try:
            # 随机选择顾客外观
            customer_images = ['customer_1', 'customer_2', 'customer_3']
            image_key = random.choice(customer_images)

            print(f"   选择的图片key: {image_key}")

            if image_key in ASSETS:
                image_path = ASSETS[image_key]
                print(f"   尝试加载: {image_path}")
                self.image = pygame.image.load(image_path)
                self.image = pygame.transform.scale(self.image, (300, 300))
                print(f"   ✅ 顾客图片加载成功")
                return
            else:
                print(f"   ⚠️ {image_key} 不在ASSETS中")
        except Exception as e:
            print(f"   ❌ 加载失败: {e}")

        # 占位符
        print(f"   使用占位符图像")
        self.image = pygame.Surface((100, 100))
        self.image.fill((150, 150, 200))

        # 绘制简单笑脸
        pygame.draw.circle(self.image, (255, 200, 150), (50, 50), 40)
        pygame.draw.circle(self.image, (0, 0, 0), (35, 40), 5)
        pygame.draw.circle(self.image, (0, 0, 0), (65, 40), 5)
        pygame.draw.arc(self.image, (0, 0, 0), (30, 45, 40, 30), 3.14, 0, 3)

    def update(self, dt):
        """更新顾客状态"""
        self.wait_time += dt
        self.patience = max(0, 1.0 - (self.wait_time / self.max_wait_time))

    def is_timeout(self):
        """检查是否超时"""
        return self.wait_time >= self.max_wait_time

    def check_item_match(self, item):
        """检查物品是否匹配"""
        return item.item_type == self.sought_item_type

    def get_patience_color(self):
        """获取耐心条颜色"""
        if self.patience > 0.6:
            return COLOR_GREEN
        elif self.patience > 0.3:
            return COLOR_YELLOW
        else:
            return COLOR_RED

    def render(self, screen):
        """渲染顾客"""
        # 绘制顾客图像
        if self.image:
            image_rect = self.image.get_rect(center=(self.x, self.y))
            screen.blit(self.image, image_rect)

        # 绘制对话框
        if self.dialog_visible:
            dialog_width = 300
            dialog_height = 100
            dialog_x = self.x - dialog_width // 2
            dialog_y = 200

            # 对话框背景
            pygame.draw.rect(screen, COLOR_WHITE,
                           (dialog_x, dialog_y, dialog_width, dialog_height),
                           border_radius=10)
            pygame.draw.rect(screen, COLOR_BLACK,
                           (dialog_x, dialog_y, dialog_width, dialog_height), 3,
                           border_radius=10)

            # 对话框文字
            lines = self._wrap_text(self.description, self.font, dialog_width - 40)
            y_offset = dialog_y + 20
            for line in lines:
                text = self.font.render(line, True, COLOR_BLACK)
                text_rect = text.get_rect(centerx=dialog_x + dialog_width//2, y=y_offset)
                screen.blit(text, text_rect)
                y_offset += 30

            # 耐心条
            patience_bar_width = dialog_width - 40
            patience_bar_x = dialog_x + 20
            patience_bar_y = dialog_y + dialog_height - 25

            pygame.draw.rect(screen, COLOR_DARK_GRAY,
                           (patience_bar_x, patience_bar_y, patience_bar_width, 15),
                           border_radius=5)

            patience_fill = int(patience_bar_width * self.patience)
            if patience_fill > 0:
                pygame.draw.rect(screen, self.get_patience_color(),
                               (patience_bar_x, patience_bar_y, patience_fill, 15),
                               border_radius=5)

            pygame.draw.rect(screen, COLOR_BLACK,
                           (patience_bar_x, patience_bar_y, patience_bar_width, 15), 2,
                           border_radius=5)

    def _wrap_text(self, text, font, max_width):
        """文本换行"""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines if lines else [text]