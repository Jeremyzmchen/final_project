"""
游戏UI - 浮动文字/飘字效果
"""
import pygame
from config.settings import COLOR_GREEN, COLOR_RED, COLOR_WHITE


class FloatingText:
    def __init__(self, x, y, text, color=COLOR_WHITE, duration=1.0):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.duration = duration
        self.timer = 0
        self.font = pygame.font.Font(None, 36)
        self.alpha = 255

    def update(self, dt):
        self.timer += dt
        # 向上飘动
        self.y -= 30 * dt

        # 淡出效果
        if self.timer > self.duration * 0.5:
            fade_progress = (self.timer - self.duration * 0.5) / (self.duration * 0.5)
            self.alpha = max(0, 255 - int(255 * fade_progress))

        return self.timer < self.duration

    def render(self, screen):
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(self.alpha)
        screen.blit(text_surf, (self.x - text_surf.get_width() // 2, self.y))