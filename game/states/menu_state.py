"""
主菜单状态 - 游戏开始界面
"""

import pygame
from config.settings import *
from game.ui.button import Button

class MenuState:
    """主菜单状态"""

    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.font_title = pygame.font.Font(None, 72)
        self.font_subtitle = pygame.font.Font(None, 36)

        # 背景图片
        self.background = None
        self._load_background()

        # 创建难度选择按钮
        self.difficulty_buttons = []
        button_width = 250
        button_height = 80
        start_y = 350
        spacing = 100

        difficulties = ['chill', 'relax', 'normal', 'mayhem']
        for i, diff in enumerate(difficulties):
            x = WINDOW_WIDTH // 2 - button_width // 2
            y = start_y + i * spacing
            btn = Button(
                x, y, button_width, button_height,
                DIFFICULTY_SETTINGS[diff]['name'],
                self._start_game,
                diff
            )
            self.difficulty_buttons.append(btn)

            # 播放菜单音乐
            try:
                pygame.mixer.music.load('assets/sounds/bgm_menu.mp3')
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
            except:
                pass

    def _load_background(self):
        """加载背景图片"""
        try:
            bg_path = ASSETS.get('bg_menu')
            if bg_path:
                print(f"尝试加载菜单背景: {bg_path}")
                self.background = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
                print(f"✅ 菜单背景加载成功: {bg_path}")
        except Exception as e:
            print(f"❌ 菜单背景加载失败: {e}")
            self.background = None

    def _start_game(self, difficulty):
        """开始游戏"""
        from game.game_manager import GameState
        self.game_manager.change_state(
            GameState.GAMEPLAY,
            difficulty=difficulty
        )

    def enter(self, **kwargs):
        """进入菜单状态"""
        pass

    def exit(self):
        """退出菜单状态"""
        pygame.mixer.music.stop()

    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.difficulty_buttons:
                button.handle_click(mouse_pos)

    def update(self, dt):
        """更新菜单"""
        mouse_pos = pygame.mouse.get_pos()
        for button in self.difficulty_buttons:
            button.update(mouse_pos)

    def render(self, screen):
        """渲染菜单"""
        # 绘制背景
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            # 如果没有背景图，使用纯色
            screen.fill(COLOR_DARK_GRAY)

        # 标题
        title_text = self.font_title.render("Lost & Found Office", True, COLOR_WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
        screen.blit(title_text, title_rect)

        # 副标题
        subtitle = self.font_subtitle.render("Airport Lost & Found Office", True, COLOR_YELLOW)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 220))
        screen.blit(subtitle, subtitle_rect)

        # 难度选择提示
        prompt = self.font_subtitle.render("Choose Difficulty:", True, COLOR_WHITE)
        prompt_rect = prompt.get_rect(center=(WINDOW_WIDTH // 2, 280))
        screen.blit(prompt, prompt_rect)

        # 渲染按钮
        for button in self.difficulty_buttons:
            button.render(screen)