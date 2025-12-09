"""
Menu status: title, button, img, music
"""

import pygame
import sys
from config.settings import *
from game.ui.button import Button

class MenuState:
    def __init__(self, game_manager):
        """
        Menu state

        Args: game_manager: manage game status and data
        """
        self.game_manager = game_manager

        # Initialize UI
        self.font_title = pygame.font.Font(FONT_PATH, 80)
        self.font_subtitle = pygame.font.Font(FONT_PATH, 40)
        self.background = pygame.transform.scale(
            pygame.image.load(ASSETS['bg_menu']),
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )

        # Initialize button
        self.btn_width = 260
        self.btn_height = 60
        self.menu_x = int(WINDOW_WIDTH * 0.75) - (self.btn_width // 2)
        self.start_y = 350
        self.spacing = 70
        self.buttons = self._create_buttons()

        self._play_menu_music()

    def _play_menu_music(self):
        """Play BGM"""
        try:
            pygame.mixer.music.load(SOUNDS['bgm_menu'])
            pygame.mixer.music.set_volume(0.7)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Failed to play BGM: {e}")

    def _create_buttons(self):
        """Create buttons"""
        buttons = []
        options = [
            ("NEW GAME", self._start_game),
            ("QUIT GAME", self._quit_game)
        ]

        for i, (text, func) in enumerate(options):
            # Set button y position
            y = self.start_y + i * self.spacing
            # Instantiate button
            btn = Button(self.menu_x, y, self.btn_width, self.btn_height,
                        text, func, style='transparent')
            buttons.append(btn)
        return buttons

    def _start_game(self):
        """Change game_state"""
        from game.game_manager import GameState
        self.game_manager.change_state(GameState.GAMEPLAY)

    def _quit_game(self):
        """Change game_state"""
        pygame.quit()
        sys.exit()

    def handle_event(self, event):
        """Handle mouse event"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for btn in self.buttons:
                btn.handle_click(mouse_pos)

    def update(self, dt):
        """Update mouse event"""
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)

    def render(self, screen):
        """Render"""
        # 1. Render background
        if self.background: screen.blit(self.background, (0, 0))
        else: screen.fill(COLOR_DARK_GRAY)
        center_x = self.menu_x + self.btn_width // 2

        # 2. Render title
        title_y = 200
        title_surf = self.font_title.render("Lost But Found", True, COLOR_WHITE)
        title_shadow = self.font_title.render("Lost But Found", True, COLOR_BLACK)

        # -2.1. Rotate title
        title_surf = pygame.transform.rotate(title_surf, 2)
        title_shadow = pygame.transform.rotate(title_shadow, 2)
        # -2.2. Render title
        screen.blit(title_shadow, title_shadow.get_rect(center=(center_x + 6, title_y + 6)))
        screen.blit(title_surf, title_surf.get_rect(center=(center_x, title_y)))

        # 3. Render buttons
        for btn in self.buttons:
            btn.render(screen)