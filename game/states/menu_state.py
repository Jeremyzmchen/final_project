"""
主菜单状态 - 游戏开始界面 (专注 Normal 模式版)
"""

import pygame
import sys
from config.settings import *
from game.ui.button import Button

class MenuState:
    """主菜单状态"""

    def __init__(self, game_manager):
        self.game_manager = game_manager

        # 字体设置
        self.font_title = pygame.font.Font(None, 80)
        self.font_subtitle = pygame.font.Font(None, 32)
        self.font_version = pygame.font.Font(None, 24)

        # 背景图片
        self.background = None
        self._load_background()

        # 当前视图状态: 'main' (主菜单) 或 'difficulty' (难度选择)
        self.current_view = 'main'

        # 按钮通用配置
        self.btn_width = 260
        self.btn_height = 60
        # 将菜单放在屏幕右侧 75% 的位置
        self.menu_x = int(WINDOW_WIDTH * 0.75) - (self.btn_width // 2)
        self.start_y = 350 # 按钮起始高度
        self.spacing = 80  # 按钮间距

        # --- 初始化两组按钮 ---
        self.main_menu_buttons = self._create_main_menu_buttons()
        self.difficulty_buttons = self._create_difficulty_buttons()

        # 播放菜单音乐
        self._play_menu_music()

    def _play_menu_music(self):
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
                self.background = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except Exception as e:
            self.background = None

    def _create_main_menu_buttons(self):
        """创建主界面的按钮"""
        buttons = []
        # 主菜单选项：除了开始和退出，其他都是装饰
        options = [
            ("NEW GAME", self._to_difficulty_select),
            ("LEADERBOARD", self._placeholder_action),
            ("STORE", self._placeholder_action),     # 新增：商店入口占位
            ("SETTINGS", self._placeholder_action),
            ("QUIT GAME", self._quit_game)
        ]

        for i, (text, func) in enumerate(options):
            y = self.start_y + i * self.spacing
            btn = Button(self.menu_x, y, self.btn_width, self.btn_height, text, func)

            # 将未开发的功能按钮设为灰色，避免误点
            if text in ["LEADERBOARD", "STORE", "SETTINGS"]:
                self._disable_button(btn)

            buttons.append(btn)

        return buttons

    def _create_difficulty_buttons(self):
        """创建难度选择界面的按钮"""
        buttons = []

        # 难度选项
        diff_keys = ['chill', 'relax', 'normal', 'mayhem']
        for i, diff in enumerate(diff_keys):
            y = self.start_y + i * self.spacing
            name = DIFFICULTY_SETTINGS[diff]['name'].upper()

            if diff == 'normal':
                # ✅ 只有 NORMAL 模式是可用的
                btn = Button(
                    self.menu_x, y, self.btn_width, self.btn_height,
                    name,
                    self._start_game,
                    diff
                )
            else:
                # 🚫 其他模式暂时锁定 (变灰，点击无效)
                btn = Button(
                    self.menu_x, y, self.btn_width, self.btn_height,
                    name,
                    self._placeholder_action
                )
                self._disable_button(btn)

            buttons.append(btn)

        # 添加一个返回按钮在最后
        back_y = self.start_y + len(diff_keys) * self.spacing + 20
        back_btn = Button(self.menu_x, back_y, self.btn_width, self.btn_height, "BACK", self._to_main_menu)
        buttons.append(back_btn)

        return buttons

    def _disable_button(self, btn):
        """辅助函数：将按钮设为禁用样式"""
        disabled_color = (60, 60, 60) # 深灰色背景
        disabled_text = (150, 150, 150) # 暗灰色文字

        btn.color_normal = disabled_color
        btn.color_hover = disabled_color # 悬停不变色
        btn.color_pressed = disabled_color
        btn.text_color = disabled_text

    # --- 回调函数 ---

    def _to_difficulty_select(self):
        """切换到难度选择视图"""
        self.current_view = 'difficulty'

    def _to_main_menu(self):
        """切换回主菜单视图"""
        self.current_view = 'main'

    def _start_game(self, difficulty):
        """开始游戏"""
        from game.game_manager import GameState
        self.game_manager.change_state(
            GameState.GAMEPLAY,
            difficulty=difficulty
        )

    def _quit_game(self):
        """退出游戏"""
        pygame.quit()
        sys.exit()

    def _placeholder_action(self):
        """占位符，点击没反应"""
        pass

    # --- 状态机标准方法 ---

    def enter(self, **kwargs):
        pass

    def exit(self):
        pygame.mixer.music.stop()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            target_buttons = self.main_menu_buttons if self.current_view == 'main' else self.difficulty_buttons

            for button in target_buttons:
                button.handle_click(mouse_pos)

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()

        target_buttons = self.main_menu_buttons if self.current_view == 'main' else self.difficulty_buttons

        for button in target_buttons:
            button.update(mouse_pos)

    def render(self, screen):
        # 1. 绘制背景
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(COLOR_DARK_GRAY)

        # 2. 绘制标题
        center_x = self.menu_x + self.btn_width // 2

        title_surf = self.font_title.render("Lost But Found", True, COLOR_WHITE)
        title_shadow = self.font_title.render("Lost But Found", True, COLOR_BLACK)

        title_surf = pygame.transform.rotate(title_surf, 2)
        title_shadow = pygame.transform.rotate(title_shadow, 2)

        title_rect = title_surf.get_rect(center=(center_x, 150))
        shadow_rect = title_shadow.get_rect(center=(center_x + 4, 150 + 4))

        screen.blit(title_shadow, shadow_rect)
        screen.blit(title_surf, title_rect)

        # 3. 绘制提示
        if self.current_view == 'difficulty':
            prompt = self.font_subtitle.render("- Select Difficulty -", True, COLOR_YELLOW)
        else:
            prompt = self.font_subtitle.render("v1.0.3-dev", True, (200, 200, 200))

        prompt_rect = prompt.get_rect(center=(center_x, 220))
        screen.blit(prompt, prompt_rect)

        # 4. 绘制按钮
        target_buttons = self.main_menu_buttons if self.current_view == 'main' else self.difficulty_buttons
        for button in target_buttons:
            button.render(screen)