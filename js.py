"""
工具：生成无缝传送带纹理 (generate_texture.py)
运行此脚本，它会在 assets/images/ 下生成 belt_tile.png
"""
import pygame
import os
import sys

# 确保路径存在
if not os.path.exists('assets/images'):
    os.makedirs('assets/images')


def generate():
    pygame.init()

    # 1. 尺寸定义 (单元格大小)
    TILE_SIZE = 100

    # 2. 颜色定义 (提取自你的截图)
    COLOR_BODY = (60, 64, 68)  # 传送带原本的深灰色
    COLOR_LINE = (30, 32, 34)  # 接缝线的黑色
    COLOR_HIGHLIGHT = (80, 84, 88)  # 边缘高光

    # 3. 创建画布
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    surf.fill(COLOR_BODY)

    # 4. 绘制纹理细节
    # A. 绘制面板的立体边缘 (上下)
    # 上边缘高光
    pygame.draw.line(surf, COLOR_HIGHLIGHT, (0, 0), (TILE_SIZE, 0), 2)
    # 下边缘阴影
    pygame.draw.line(surf, COLOR_LINE, (0, TILE_SIZE - 2), (TILE_SIZE, TILE_SIZE - 2), 2)

    # B. 绘制中间的接缝 (模拟板与板的连接)
    # 我们画一条垂直线或者水平线，取决于你想要它是横着排还是竖着排
    # 既然我们要让它沿着路径流动，我们画一条 "竖线" 代表接缝，
    # 这样当纹理水平平铺时，看起来就是一节一节的板子。
    seam_x = TILE_SIZE - 4
    pygame.draw.rect(surf, COLOR_LINE, (seam_x, 0, 4, TILE_SIZE))
    pygame.draw.line(surf, COLOR_HIGHLIGHT, (seam_x - 1, 0), (seam_x - 1, TILE_SIZE), 1)

    # C. 增加一点杂色/质感 (可选)
    # for i in range(20):
    #     x = random.randint(0, TILE_SIZE)
    #     y = random.randint(0, TILE_SIZE)
    #     c = random.choice([COLOR_HIGHLIGHT, COLOR_LINE])
    #     surf.set_at((x, y), c)

    # 5. 保存
    save_path = 'assets/images/belt_tile.png'
    pygame.image.save(surf, save_path)
    print(f"✅ 成功生成纹理: {save_path}")
    print("现在运行游戏，传送带就会有丝滑的滚动效果了！")


if __name__ == "__main__":
    generate()