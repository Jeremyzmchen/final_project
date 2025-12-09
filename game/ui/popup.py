"""
Game UI - Floating Text / Pop-up Text Effect
Shows a short message that moves upward and fades out
"""

import pygame
# TODO 12.05修改替换
from config.settings import *


class FloatingText:
    """Floating text element that rises and fades out"""

    def __init__(self, x, y, text, color=COLOR_WHITE, duration=1.0):
        """Create a floating text at (x, y) with a lifetime in seconds."""
        self.x = x
        self.y = y - 60 # TODO 12.05修改替换
        self.text = text
        self.color = color

        # Lifetime control
        self.duration = duration
        self.timer = 0

        # Rendering settings
        self.font = pygame.font.Font(FONT_PATH, 36) # TODO 12.05修改替换
        self.alpha = 255  # 255 = opaque, 0 = fully transparent

    def update(self, dt):
        """
        Update animation (move up + fade).
        Returns True if the text should stay alive.
        """
        self.timer += dt

        # Move upward over time
        self.y -= 20 * dt   # TODO 12.05修改替换 12.06把80改为20,要不然看不清

        # Fade out during the second half of the lifetime
        if self.timer > self.duration * 0.5:
            fade_progress = (self.timer - self.duration * 0.5) / (self.duration * 0.5)
            self.alpha = max(0, 255 - int(255 * fade_progress))

        return self.timer < self.duration

    def render(self, screen):
        """Render the floating text centered at x with current alpha."""
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(self.alpha)
        screen.blit(text_surf, (self.x - text_surf.get_width() // 2, self.y))
