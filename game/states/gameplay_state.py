"""
游戏玩法状态 - 核心游戏逻辑
"""

import pygame
import random
from config.settings import *
from game.entities.item import Item
from game.entities.customer import Customer
from game.managers.inventory_manager import InventoryManager
from game.ui.hud import HUD

class GameplayState:
    """游戏玩法状态"""

    def __init__(self, game_manager, difficulty='normal'):
        self.game_manager = game_manager
        self.difficulty = difficulty
        self.settings = DIFFICULTY_SETTINGS[difficulty]

        # 游戏数据
        self.money = 1176
        self.day = 3
        self.shift_time = 0
        self.shift_duration = 480

        # 管理器
        self.inventory_manager = InventoryManager()

        # 实体列表
        self.current_customer = None
        self.customer_timer = 0

        # 传送带物品
        self.conveyor_items = []
        self.item_spawn_timer = 0
        self.item_spawn_interval = ITEM_SPAWN_INTERVAL
        self.current_batch_id = 0
        self.batch_pause_states = {}

        # UI
        self.hud = HUD()
        from game.ui.button import Button
        self.no_item_button = Button(
            CUSTOMER_DELIVERY_AREA['x'] + CUSTOMER_DELIVERY_AREA['width']//2 - 75,
            CUSTOMER_DELIVERY_AREA['y'] + CUSTOMER_DELIVERY_AREA['height'] + 10,
            150, 40,
            "Don't Have",
            self._tell_customer_no_item
        )

        # 拖拽相关
        self.dragging_item = None
        self.drag_offset = (0, 0)
        self.hovered_item = None

        # 字体
        self.font = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # 背景
        self.background = None
        self._load_background()

        # 初始化
        self._init_game()

    def _load_background(self):
        """加载背景"""
        try:
            bg_path = ASSETS.get('bg_main')
            if bg_path:
                self.background = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
                print(f"✅ 背景加载成功")
        except:
            self.background = None

    def _init_game(self):
        """初始化游戏"""
        # 立即生成第一批物品
        self._spawn_item_on_conveyor()

        # 生成第一个顾客
        self._spawn_customer()

        # 播放背景音乐
        self._play_music()


    def _play_music(self):
        """播放背景音乐"""
        try:
            pygame.mixer.music.load('assets/sounds/bgm_gameplay.mp3')
            pygame.mixer.music.set_volume(0.5)  # 音量 0.0-1.0
            pygame.mixer.music.play(-1)  # -1 表示循环播放
            print("🎵 背景音乐开始播放")
        except Exception as e:
            print(f"❌ 音乐加载失败: {e}")



    def _spawn_item_on_conveyor(self):
        """生成一批物品"""
        print(f"\n========== 生成批次 {self.current_batch_id} ==========")

        self.batch_pause_states[self.current_batch_id] = {
            'paused': False,
            'timer': 0,
            'triggered': False
        }

        for i in range(ITEMS_PER_BATCH):
            item_type = random.choice(list(ITEM_DESCRIPTIONS.keys()))
            item = Item(item_type)

            item.on_conveyor = True
            item.conveyor_progress = 0
            item.item_index = i
            item.batch_id = self.current_batch_id

            # 间距设置
            start_pos = CONVEYOR_PATH[0]
            horizontal_offset = i * 80  # 水平间距（从65改成80，更分散）
            vertical_offset = [35, 0, -35][i]  # 垂直间距（从25改成35，更分散）

            item.conveyor_start_offset = horizontal_offset
            item.conveyor_vertical_offset = vertical_offset

            item.set_position(
                start_pos[0] - horizontal_offset - item.width // 2,
                start_pos[1] - item.height // 2
            )

            self.conveyor_items.append(item)
            print(f"📦 物品{i+1}: {item_type} (水平:{horizontal_offset}, 垂直:{vertical_offset})")

        self.current_batch_id += 1

    def _spawn_customer(self):
        """生成顾客"""
        if self.current_customer is None:
            desk_items = self.inventory_manager.get_all_items()
            if desk_items:
                target_item = random.choice(desk_items)
                sought_item_type = target_item.item_type
            else:
                sought_item_type = random.choice(list(ITEM_DESCRIPTIONS.keys()))

            self.current_customer = Customer(sought_item_type)
            print(f"✅ 顾客到达，寻找: {sought_item_type}")

    def _check_item_return(self, item):
        """检查返还物品"""
        if self.current_customer and item:
            if self.current_customer.check_item_match(item):
                self.money += REWARD_CORRECT
                if item in self.conveyor_items:
                    self.conveyor_items.remove(item)
                else:
                    self.inventory_manager.remove_item(item)
                self.current_customer = None
                print(f"✅ 正确！+${REWARD_CORRECT}")
                return True
            else:
                self.money += PENALTY_WRONG
                print(f"❌ 错误！{PENALTY_WRONG}")
                return False
        return False

    def _tell_customer_no_item(self):
        """告诉顾客没有"""
        if self.current_customer:
            sought_type = self.current_customer.sought_item_type
            all_items = self.conveyor_items + self.inventory_manager.get_all_items()
            has_item = any(item.item_type == sought_type for item in all_items)

            if has_item:
                self.money += PENALTY_WRONG * 2
                print(f"❌ 撒谎！{PENALTY_WRONG * 2}")
            else:
                self.money += -10
                print(f"⚠️ 没有物品 -$10")

            self.current_customer = None

    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if event.button == 1:
                if self.current_customer and self.no_item_button.handle_click(mouse_pos):
                    return

                clicked_item = None
                for item in self.conveyor_items:
                    if item.contains_point(mouse_pos):
                        clicked_item = item
                        item.on_conveyor = False
                        break

                if not clicked_item:
                    clicked_item = self.inventory_manager.get_item_at_position(mouse_pos)

                if clicked_item:
                    self.dragging_item = clicked_item
                    item_pos = clicked_item.get_position()
                    self.drag_offset = (mouse_pos[0] - item_pos[0], mouse_pos[1] - item_pos[1])

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging_item:
                mouse_pos = pygame.mouse.get_pos()

                if self.current_customer and self._is_in_customer_area(mouse_pos):
                    self._check_item_return(self.dragging_item)
                else:
                    new_x = mouse_pos[0] - self.drag_offset[0]
                    new_y = mouse_pos[1] - self.drag_offset[1]
                    self.dragging_item.set_position(new_x, new_y)

                    if self.dragging_item in self.conveyor_items:
                        if self.inventory_manager.is_position_in_desk((new_x, new_y)):
                            self.conveyor_items.remove(self.dragging_item)
                            self.inventory_manager.add_item_to_desk(self.dragging_item)
                            print(f"✅ 移到工作台")

                self.dragging_item = None

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_item:
                mouse_pos = pygame.mouse.get_pos()
                new_x = mouse_pos[0] - self.drag_offset[0]
                new_y = mouse_pos[1] - self.drag_offset[1]
                self.dragging_item.set_position(new_x, new_y)

    def _is_in_customer_area(self, pos):
        """检查是否在顾客区域"""
        x, y = pos
        return (CUSTOMER_DELIVERY_AREA['x'] <= x <= CUSTOMER_DELIVERY_AREA['x'] + CUSTOMER_DELIVERY_AREA['width'] and
                CUSTOMER_DELIVERY_AREA['y'] <= y <= CUSTOMER_DELIVERY_AREA['y'] + CUSTOMER_DELIVERY_AREA['height'])

    def _render_item_tooltip(self, screen):
        """渲染提示框"""
        if not self.hovered_item:
            return

        mouse_pos = pygame.mouse.get_pos()
        item_name = self.hovered_item.name
        item_category = self.hovered_item.category.upper()

        padding = 10
        name_surface = self.font_small.render(item_name, True, COLOR_WHITE)
        category_surface = self.font_small.render(f"[{item_category}]", True, COLOR_YELLOW)

        tooltip_width = max(name_surface.get_width(), category_surface.get_width()) + padding * 2
        tooltip_height = name_surface.get_height() + category_surface.get_height() + padding * 3

        tooltip_x = mouse_pos[0] + 15
        tooltip_y = mouse_pos[1] + 15

        if tooltip_x + tooltip_width > WINDOW_WIDTH:
            tooltip_x = mouse_pos[0] - tooltip_width - 15
        if tooltip_y + tooltip_height > WINDOW_HEIGHT:
            tooltip_y = mouse_pos[1] - tooltip_height - 15

        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(screen, (40, 40, 40), tooltip_rect, border_radius=5)
        pygame.draw.rect(screen, COLOR_WHITE, tooltip_rect, 2, border_radius=5)

        name_rect = name_surface.get_rect(centerx=tooltip_x + tooltip_width // 2, top=tooltip_y + padding)
        screen.blit(name_surface, name_rect)

        category_rect = category_surface.get_rect(centerx=tooltip_x + tooltip_width // 2, top=name_rect.bottom + 5)
        screen.blit(category_surface, category_rect)

    def update(self, dt):
        """更新游戏"""
        self.shift_time += dt

        # 鼠标悬停
        mouse_pos = pygame.mouse.get_pos()
        if not self.dragging_item:
            self.hovered_item = None
            for item in self.conveyor_items:
                if item.contains_point(mouse_pos):
                    self.hovered_item = item
                    break
            if not self.hovered_item:
                self.hovered_item = self.inventory_manager.get_item_at_position(mouse_pos)
        else:
            self.hovered_item = None

        # 下班检查
        if self.shift_time >= self.shift_duration:
            self._end_shift()
            return

        # 物品生成
        self.item_spawn_timer += dt
        if self.item_spawn_timer >= self.item_spawn_interval:
            self.item_spawn_timer = 0
            self._spawn_item_on_conveyor()

        # 批次暂停控制
        trigger_y = 420
        pause_duration = 3.0

        batch_items = {}
        for item in self.conveyor_items:
            if item.batch_id not in batch_items:
                batch_items[item.batch_id] = []
            batch_items[item.batch_id].append(item)

        for batch_id, items in batch_items.items():
            if batch_id in self.batch_pause_states:
                pause_state = self.batch_pause_states[batch_id]
                item3 = next((item for item in items if item.item_index == 2), None)

                if item3 and not pause_state['triggered']:
                    if item3.y >= trigger_y:
                        pause_state['paused'] = True
                        pause_state['triggered'] = True
                        print(f"🛑 批次{batch_id}停留")

                if pause_state['paused']:
                    pause_state['timer'] += dt
                    if pause_state['timer'] >= pause_duration:
                        pause_state['paused'] = False
                        print(f"✅ 批次{batch_id}继续")

        # 更新物品移动
        items_to_remove = []
        for item in self.conveyor_items[:]:
            if item.on_conveyor:
                pause_flag = self.batch_pause_states.get(item.batch_id, {'paused': False})
                finished = item.update_conveyor_movement(dt, CONVEYOR_SPEED, CONVEYOR_PATH, pause_flag)
                if finished:
                    items_to_remove.append(item)

        for item in items_to_remove:
            if item in self.conveyor_items:
                self.conveyor_items.remove(item)

        # 顾客更新
        self.customer_timer += dt
        if self.customer_timer >= self.settings['customer_interval']:
            self.customer_timer = 0
            self._spawn_customer()

        if self.current_customer:
            self.current_customer.update(dt)
            if self.current_customer.is_timeout():
                self.money += PENALTY_TIMEOUT
                self.current_customer = None

        # 更新按钮
        if self.current_customer:
            self.no_item_button.update(mouse_pos)

    def _end_shift(self):
        """结束班次"""
        from game.game_manager import GameState
        self.game_manager.change_state(GameState.GAME_OVER, money=self.money, day=self.day)

    def render(self, screen):
        """渲染"""
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(COLOR_GRAY)

        # 调试：显示路径（可以设为False关闭）
        if True:  # 改为False关闭路径显示
            for i in range(len(CONVEYOR_PATH) - 1):
                pygame.draw.line(screen, (255, 0, 0), CONVEYOR_PATH[i], CONVEYOR_PATH[i+1], 2)
                pygame.draw.circle(screen, (0, 255, 0), CONVEYOR_PATH[i], 5)
            font = pygame.font.Font(None, 20)
            for i, point in enumerate(CONVEYOR_PATH):
                text = font.render(str(i), True, (255, 255, 0))
                screen.blit(text, (point[0] + 10, point[1] - 10))

        # 不再绘制区域矩形，使用背景图
        # （工作台、传送带、储物柜的视觉效果由背景图提供）

        # 传送带物品
        for item in self.conveyor_items:
            item.render(screen)

        # 工作台物品
        self.inventory_manager.render(screen)

        # 顾客和交付区域
        if self.current_customer:
            # 只绘制边框，不填充
            pygame.draw.rect(screen, COLOR_GREEN,
                             (CUSTOMER_DELIVERY_AREA['x'], CUSTOMER_DELIVERY_AREA['y'],
                              CUSTOMER_DELIVERY_AREA['width'], CUSTOMER_DELIVERY_AREA['height']),
                             3)  # 3是边框宽度

            # 绘制顾客
            self.current_customer.render(screen)

            # 绘制按钮
            self.no_item_button.render(screen)

        # HUD
        self.hud.render(screen, self.money, self.day, self.shift_time, self.shift_duration)

        # 拖拽物品
        if self.dragging_item:
            self.dragging_item.render(screen, alpha=180)

        # 悬停提示
        if self.hovered_item and not self.dragging_item:
            self._render_item_tooltip(screen)

