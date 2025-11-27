"""
游戏管理器 - 负责游戏状态切换和整体流程控制
"""

from enum import Enum
from game.states.menu_state import MenuState
from game.states.gameplay_state import GameplayState
from game.states.game_over_state import GameOverState


class GameState(Enum):
    """游戏状态枚举"""
    MENU = "menu"
    GAMEPLAY = "gameplay"
    PAUSE = "pause"
    GAME_OVER = "game_over"


class GameManager:
    """游戏管理器 - 管理游戏状态切换"""

    def __init__(self, screen):
        self.screen = screen
        self.current_state = GameState.MENU
        self.states = {}
        self.game_data = {}  # 用于在状态之间传递数据

        # 初始化各个游戏状态
        self._init_states()

    def _init_states(self):
        """初始化所有游戏状态"""
        self.states[GameState.MENU] = MenuState(self)
        # GameplayState 和 GameOverState 将在需要时创建

    def change_state(self, new_state, **kwargs):
        """
        切换游戏状态

        Args:
            new_state: 新的游戏状态
            **kwargs: 传递给新状态的参数
        """
        # 退出当前状态
        if self.current_state in self.states:
            current = self.states[self.current_state]
            if hasattr(current, 'exit'):
                current.exit()

        # 更新游戏数据
        self.game_data.update(kwargs)

        # 切换到新状态
        self.current_state = new_state

        # 如果新状态还未创建，则创建它
        if new_state not in self.states:
            if new_state == GameState.GAMEPLAY:
                difficulty = kwargs.get('difficulty', 'normal')
                self.states[new_state] = GameplayState(self, difficulty)
            elif new_state == GameState.GAME_OVER:
                self.states[new_state] = GameOverState(self)

        # 进入新状态
        if new_state in self.states:
            state = self.states[new_state]
            if hasattr(state, 'enter'):
                state.enter(**kwargs)

    def handle_event(self, event):
        """处理输入事件"""
        if self.current_state in self.states:
            self.states[self.current_state].handle_event(event)

    def update(self, dt):
        """更新当前游戏状态"""
        if self.current_state in self.states:
            self.states[self.current_state].update(dt)

    def render(self):
        """渲染当前游戏状态"""
        if self.current_state in self.states:
            self.states[self.current_state].render(self.screen)

    def get_game_data(self, key, default=None):
        """获取游戏数据"""
        return self.game_data.get(key, default)

    def set_game_data(self, key, value):
        """设置游戏数据"""
        self.game_data[key] = value