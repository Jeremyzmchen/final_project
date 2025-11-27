"""
Lost & Found Office Game - 机场失物招领处管理游戏
Main Entry Point
"""

import pygame
import sys
from game.game_manager import GameManager
from config.settings import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, WINDOW_TITLE


def main():
    """游戏主入口"""
    # 初始化Pygame
    pygame.init()

    # 创建游戏窗口
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    # 创建时钟对象
    clock = pygame.time.Clock()

    # 创建游戏管理器
    game_manager = GameManager(screen)

    # 游戏主循环
    running = True
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game_manager.handle_event(event)

        # 更新游戏状态
        dt = clock.tick(FPS) / 1000.0  # 转换为秒
        game_manager.update(dt)

        # 渲染游戏
        game_manager.render()
        pygame.display.flip()

    # 退出游戏
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()