"""
HUD (Heads-Up Display) Component
Displays game information: money and remaining time
"""

import pygame
from config.settings import *


class HUD:
    """Display game status information (money and time)"""

    def __init__(self):
        """
        Initialize HUD with background images and font
        
        Loads clock and money icons, scales them to specified size,
        and sets their positions on screen.
        """
        # Load font for displaying values
        self.font = pygame.font.Font(FONT_PATH, 36)

        # TODO 12.04修改替换
        # HUD element size (width, height)
        self.hud_size = (130, 80)

        # TODO 12.04修改替换
        # HUD positions on screen (x, y from top-left)
        self.time_pos = (1430, 740)   # Time display position
        self.money_pos = (1430, 650)  # Money display position

        # Load original icon images
        raw_time_img = pygame.image.load('assets/images/icons/clock.png')
        raw_money_img = pygame.image.load('assets/images/icons/money.png')

        # Scale images to HUD size (Transform Scale)
        self.bg_time = pygame.transform.scale(raw_time_img, self.hud_size)
        self.bg_money = pygame.transform.scale(raw_money_img, self.hud_size)

    def render(self, screen, money, current_time, total_duration):
        """
        Render HUD elements to screen
        
        Args:
            screen (pygame.Surface): Screen to draw on
            money (float): Current money amount
            current_time (float): Elapsed time in seconds
            total_duration (float): Total game duration in seconds
        """
        # Calculate remaining time
        remaining = max(0, total_duration - current_time)
        
        # Format time as MM:SS
        time_str = f"{int(remaining // 60):02}:{int(remaining % 60):02}"
        
        # Format money with dollar sign
        money_str = f"${int(money)}"

        # ==========================================
        # Step 1: Render time HUD
        # ==========================================
        # Draw background icon
        screen.blit(self.bg_time, self.time_pos)

        # Get background rect on screen
        bg_rect_time = self.bg_time.get_rect(topleft=self.time_pos)

        # Render time text
        time_surf = self.font.render(time_str, True, COLOR_WHITE)
        
        # Center text on background
        time_text_rect = time_surf.get_rect(center=bg_rect_time.center)
        
        # Draw text
        screen.blit(time_surf, time_text_rect)

        # ==========================================
        # Step 2: Render money HUD
        # ==========================================
        # Draw background icon
        screen.blit(self.bg_money, self.money_pos)

        # Get background rect on screen
        bg_rect_money = self.bg_money.get_rect(topleft=self.money_pos)

        # Render money text
        money_surf = self.font.render(money_str, True, COLOR_WHITE)
        
        # Center text on background
        money_text_rect = money_surf.get_rect(center=bg_rect_money.center)
        
        # Draw text
        screen.blit(money_surf, money_text_rect)