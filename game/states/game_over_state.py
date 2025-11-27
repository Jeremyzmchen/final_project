"""
游戏结束状态 - 显示结算界面
"""

import pygame
from config.settings import *
from game.ui.button import Button

class GameOverState:
    """游戏结束状态 - 显示当天工作总结"""

    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.money = 0
        self.day = 0

        # 字体
        self.font_title = pygame.font.Font(None, 64)
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)

        # 按钮
        self.continue_button = Button(
            WINDOW_WIDTH // 2 - 150, 500, 300, 70,
            "Next Day",
            self._continue_game
        )

        self.menu_button = Button(
            WINDOW_WIDTH // 2 - 150, 600, 300, 70,
            "Main Menu",
            self._return_to_menu
        )

    def _continue_game(self):
        """继续游戏（进入下一天）"""
        # 这里可以增加天数，重新开始游戏
        new_day = self.day + 1
        self.game_manager.change_state(
            self.game_manager.GameState.GAMEPLAY,
            difficulty=self.game_manager.get_game_data('difficulty', 'normal'),
            day=new_day,
            money=self.money
        )

    def _return_to_menu(self):
        """返回主菜单"""
        self.game_manager.change_state(self.game_manager.GameState.MENU)

    def enter(self, **kwargs):
        """进入游戏结束状态"""
        self.money = kwargs.get('money', 0)
        self.day = kwargs.get('day', 1)

    def exit(self):
        """退出游戏结束状态"""
        pass

    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            self.continue_button.handle_click(mouse_pos)
            self.menu_button.handle_click(mouse_pos)

    def update(self, dt):
        """更新状态"""
        mouse_pos = pygame.mouse.get_pos()
        self.continue_button.update(mouse_pos)
        self.menu_button.update(mouse_pos)

    def render(self, screen):
        """渲染结束界面"""
        # 背景
        screen.fill(COLOR_DARK_GRAY)

        # 标题
        title_text = self.font_title.render("Shift Complete!", True, COLOR_WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 100))
        screen.blit(title_text, title_rect)

        # 天数
        day_text = self.font_large.render(f"Day {self.day}", True, COLOR_YELLOW)
        day_rect = day_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
        screen.blit(day_text, day_rect)

        # 金钱
        money_label = self.font_medium.render("Today's Earnings:", True, COLOR_WHITE)
        money_label_rect = money_label.get_rect(center=(WINDOW_WIDTH // 2, 280))
        screen.blit(money_label, money_label_rect)

        money_color = COLOR_GREEN if self.money > 0 else COLOR_RED
        money_text = self.font_large.render(f"${self.money}", True, money_color)
        money_rect = money_text.get_rect(center=(WINDOW_WIDTH // 2, 340))
        screen.blit(money_text, money_rect)

        # 评价
        if self.money > 500:
            evaluation = "Excellent!"
            eval_color = COLOR_GREEN
        elif self.money > 200:
            evaluation = "Good Job!"
            eval_color = COLOR_YELLOW
        elif self.money > 0:
            evaluation = "Keep Trying"
            eval_color = COLOR_ORANGE
        else:
            evaluation = "Need Improvement..."
            eval_color = COLOR_RED

        eval_text = self.font_medium.render(evaluation, True, eval_color)
        eval_rect = eval_text.get_rect(center=(WINDOW_WIDTH // 2, 410))
        screen.blit(eval_text, eval_rect)

        # 按钮
        self.continue_button.render(screen)
        self.menu_button.render(screen)