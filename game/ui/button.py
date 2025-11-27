"""
UI按钮组件
"""

import pygame
from config.settings import COLOR_WHITE, COLOR_BLACK, COLOR_BLUE, COLOR_GRAY

class Button:
    """可点击的按钮UI组件"""

    def __init__(self, x, y, width, height, text, callback, callback_arg=None):
        """
        初始化按钮

        Args:
            x, y: 按钮位置
            width, height: 按钮尺寸
            text: 按钮文字
            callback: 点击回调函数
            callback_arg: 传递给回调函数的参数
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.callback_arg = callback_arg

        # 状态
        self.is_hovered = False
        self.is_pressed = False

        # 颜色
        self.color_normal = COLOR_BLUE
        self.color_hover = (120, 170, 255)
        self.color_pressed = (80, 130, 255)
        self.text_color = COLOR_WHITE

        # 字体
        self.font = pygame.font.Font(None, 36)

    def handle_click(self, mouse_pos):
        """
        处理鼠标点击

        Args:
            mouse_pos: 鼠标位置元组 (x, y)
        """
        if self.rect.collidepoint(mouse_pos):
            if self.callback:
                if self.callback_arg is not None:
                    self.callback(self.callback_arg)
                else:
                    self.callback()
            return True
        return False

    def update(self, mouse_pos):
        """
        更新按钮状态

        Args:
            mouse_pos: 鼠标位置元组 (x, y)
        """
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def render(self, screen):
        """
        渲染按钮

        Args:
            screen: Pygame屏幕对象
        """
        # 选择颜色
        if self.is_pressed:
            color = self.color_pressed
        elif self.is_hovered:
            color = self.color_hover
        else:
            color = self.color_normal

        # 绘制按钮背景
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, COLOR_BLACK, self.rect, 3, border_radius=10)

        # 绘制文字
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)