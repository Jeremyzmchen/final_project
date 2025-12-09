import pygame
import sys
from game.states.menu_state import MenuState
from game.states.gameplay_state import GameplayState
from game.states.game_over_state import GameOverState
from config.settings import *

class GameState:
    MENU = 'menu'
    GAMEPLAY = 'gameplay'
    GAME_OVER = 'game_over'

class GameManager:
    def __init__(self):
        pygame.init()
        # [修改] 确保使用 settings 中的宽高
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # 1. 隐藏系统默认光标
        pygame.mouse.set_visible(False)
        self.cursor_img = None
        try:
            path = ASSETS['cursor']
            self.cursor_img = pygame.image.load(path)
            self.cursor_img = pygame.transform.scale(self.cursor_img, (45, 45))
        except Exception as e:
            print(f"Failed to load custom cursor: {e}")
            pygame.mouse.set_visible(True)

        self.states = {}
        self.current_state = None

        self.game_data = {}

        self._init_states()
        self.change_state(GameState.MENU)

    def _init_states(self):
        self.states[GameState.MENU] = MenuState(self)

    def change_state(self, state_name, **kwargs):
        """切换状态"""
        self.game_data.update(kwargs)

        if state_name == GameState.GAMEPLAY:
            # [修改] 移除 difficulty 参数，每次重新创建以重置游戏
            self.states[GameState.GAMEPLAY] = GameplayState(self)

        elif state_name == GameState.GAME_OVER:
            self.states[GameState.GAME_OVER] = GameOverState(self)

        elif state_name == GameState.MENU:
            if GameState.MENU not in self.states:
                self.states[GameState.MENU] = MenuState(self)
            # 切换回菜单时播放音乐
            try:
                pygame.mixer.music.load('assets/sounds/bgm_menu.mp3')
                pygame.mixer.music.play(-1)
            except: pass

        self.current_state = state_name

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._render()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            if self.current_state in self.states:
                self.states[self.current_state].handle_event(event)

    def _update(self, dt):
        if self.current_state in self.states:
            self.states[self.current_state].update(dt)

    def _render(self):
        if self.current_state in self.states:
            self.states[self.current_state].render(self.screen)

        if self.cursor_img:
            mx, my = pygame.mouse.get_pos()
            self.screen.blit(self.cursor_img, (mx, my))

        pygame.display.flip()