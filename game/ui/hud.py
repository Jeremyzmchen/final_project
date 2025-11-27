"""
游戏HUD（Heads-Up Display）- 显示游戏信息
"""

import pygame
from config.settings import *

class HUD:
    """游戏HUD - 显示金钱、时间等信息"""

    def __init__(self):
        """初始化HUD"""
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)

    def _format_time(self, seconds):
        """
        格式化时间显示

        Args:
            seconds: 秒数

        Returns:
            格式化的时间字符串 "MM:SS"
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def render(self, screen, money, day, shift_time, shift_duration):
        """
        渲染HUD

        Args:
            screen: Pygame屏幕对象
            money: 当前金钱
            day: 当前天数
            shift_time: 已工作时间（秒）
            shift_duration: 班次总时长（秒）
        """
        # 右上角 - 金钱显示
        money_text = self.font_large.render(f"${money}", True, COLOR_GREEN)
        money_rect = money_text.get_rect(topright=(WINDOW_WIDTH - 20, 20))

        # 绘制金钱背景
        bg_rect = money_rect.inflate(20, 10)
        pygame.draw.rect(screen, COLOR_BLACK, bg_rect, border_radius=5)
        pygame.draw.rect(screen, COLOR_WHITE, bg_rect, 2, border_radius=5)
        screen.blit(money_text, money_rect)

        # 右下角 - 天数显示
        day_text = self.font_medium.render(f"Day {day}", True, COLOR_WHITE)
        day_rect = day_text.get_rect(bottomright=(WINDOW_WIDTH - 20, WINDOW_HEIGHT - 80))

        day_bg = day_rect.inflate(20, 10)
        pygame.draw.rect(screen, COLOR_BLACK, day_bg, border_radius=5)
        pygame.draw.rect(screen, COLOR_WHITE, day_bg, 2, border_radius=5)
        screen.blit(day_text, day_rect)

        # 右下角 - 时间显示
        time_text = self.font_medium.render(
            self._format_time(shift_time),
            True,
            COLOR_WHITE
        )
        time_rect = time_text.get_rect(bottomright=(WINDOW_WIDTH - 20, WINDOW_HEIGHT - 20))

        time_bg = time_rect.inflate(20, 10)
        pygame.draw.rect(screen, COLOR_BLACK, time_bg, border_radius=5)
        pygame.draw.rect(screen, COLOR_WHITE, time_bg, 2, border_radius=5)
        screen.blit(time_text, time_rect)

        # 上方中间 - 进度条（班次进度）
        progress = min(1.0, shift_time / shift_duration)
        bar_width = 300
        bar_height = 30
        bar_x = WINDOW_WIDTH // 2 - bar_width // 2
        bar_y = 20

        # 进度条背景
        pygame.draw.rect(screen, COLOR_DARK_GRAY,
                        (bar_x, bar_y, bar_width, bar_height),
                        border_radius=5)

        # 进度条填充
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            pygame.draw.rect(screen, COLOR_BLUE,
                           (bar_x, bar_y, fill_width, bar_height),
                           border_radius=5)

        # 进度条边框
        pygame.draw.rect(screen, COLOR_WHITE,
                        (bar_x, bar_y, bar_width, bar_height), 3,
                        border_radius=5)

        # 进度条文字
        progress_text = self.font_small.render("Shift Progress", True, COLOR_WHITE)
        progress_text_rect = progress_text.get_rect(
            center=(bar_x + bar_width // 2, bar_y + bar_height // 2)
        )
        screen.blit(progress_text, progress_text_rect)

        # 左上角 - 提示信息
        hint_text = self.font_small.render(
            "Drag items to organize | Right-click for details",
            True,
            COLOR_GRAY
        )
        screen.blit(hint_text, (20, 20))