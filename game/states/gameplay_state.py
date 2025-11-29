"""
游戏玩法状态 - 核心游戏逻辑 (修复 resolve_overlap 报错版)
"""

import pygame
import random
import math
import os
from config.settings import *
from game.entities.item import Item
from game.entities.customer import Customer
from game.managers.inventory_manager import InventoryManager
from game.ui.hud import HUD
from game.ui.popup import FloatingText

class GameplayState:
    """游戏玩法状态"""

    def __init__(self, game_manager, difficulty='normal'):
        self.game_manager = game_manager
        self.difficulty = difficulty
        self.settings = DIFFICULTY_SETTINGS[difficulty]

        # 游戏数据
        self.money = 0
        self.day = 1
        self.shift_time = 0
        self.shift_duration = 180

        if 'money' in game_manager.game_data:
            self.money = game_manager.game_data['money']
        if 'day' in game_manager.game_data:
            self.day = game_manager.game_data['day']

        # 管理器
        self.inventory_manager = InventoryManager()

        # 实体
        self.current_customer = None
        self.customer_timer = 0

        # 传送带系统
        self.conveyor_items = []
        self.item_spawn_timer = 0
        self.item_spawn_interval = ITEM_SPAWN_INTERVAL
        self.current_batch_id = 0
        self.batch_pause_states = {}

        # 多顾客管理
        self.customers = []
        self.customer_slots = [None] * len(CUSTOMER_SLOTS)

        # --- 传送带滚动变量 ---
        self.conveyor_texture = None
        self.scroll_offset = 0
        self.scroll_speed = CONVEYOR_SPEED
        self.belt_width = 160

        # UI
        self.hud = HUD()
        from game.ui.button import Button
        # 移除旧按钮，逻辑由 Customer 自带按钮处理
        self.no_item_button = None

        self.popups = []
        self.sfx = {}
        self._load_sfx()

        self.dragging_item = None
        self.drag_offset = (0, 0)
        self.hovered_item = None

        self.font = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        self.background = None
        self._load_background()
        self._load_conveyor_texture()

        self._init_game()

    def _load_background(self):
        try:
            bg_path = ASSETS.get('bg_main')
            if bg_path:
                self.background = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except:
            self.background = None

    def _load_conveyor_texture(self):
        """加载生成的无缝纹理"""
        paths = ['assets/images/belt_tile.png', 'assets/images/conveyor_4.jpg', 'assets/images/conveyor_1.jpg']

        for p in paths:
            try:
                if os.path.exists(p):
                    raw_img = pygame.image.load(p)
                    size = self.belt_width
                    self.conveyor_texture = pygame.transform.scale(raw_img, (size, size))
                    return
            except Exception as e:
                pass

        # 备用纹理
        s = pygame.Surface((self.belt_width, self.belt_width))
        s.fill((60, 64, 68))
        pygame.draw.rect(s, (30, 30, 30), (self.belt_width-5, 0, 5, self.belt_width))
        self.conveyor_texture = s

    def _load_sfx(self):
        sfx_files = {
            'pickup': 'assets/sounds/sfx_item_pickup.wav',
            'place': 'assets/sounds/sfx_item_place.wav',
            'cash': 'assets/sounds/sfx_money.wav',
            'wrong': 'assets/sounds/sfx_wrong.wav'
        }
        for name, path in sfx_files.items():
            try:
                self.sfx[name] = pygame.mixer.Sound(path)
                self.sfx[name].set_volume(0.4)
            except:
                self.sfx[name] = None

    def _play_sfx(self, name):
        if self.sfx.get(name):
            self.sfx[name].play()

    def _spawn_popup(self, x, y, text, color=COLOR_WHITE):
        self.popups.append(FloatingText(x, y, text, color))

    def _init_game(self):
        self._spawn_item_on_conveyor()
        self._spawn_customer()
        self._play_music()

    def _play_music(self):
        try:
            pygame.mixer.music.load('assets/sounds/bgm_gameplay.mp3')
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except:
            pass

    def _spawn_item_on_conveyor(self):
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

            start_pos = CONVEYOR_PATH[0]
            horizontal_offset = i * 80
            vertical_offset = [35, 0, -35][i]

            item.conveyor_start_offset = horizontal_offset
            item.conveyor_vertical_offset = vertical_offset
            item.set_position(
                start_pos[0] - horizontal_offset - item.width // 2,
                start_pos[1] - item.height // 2
            )
            self.conveyor_items.append(item)

        self.current_batch_id += 1

    def _spawn_customer(self):
        available_indices = [i for i, c in enumerate(self.customer_slots) if c is None]
        if not available_indices: return

        slot_index = random.choice(available_indices)
        target_x = CUSTOMER_SLOTS[slot_index]

        desk_items = self.inventory_manager.get_all_items()
        if desk_items and random.random() < 0.7:
            target_item = random.choice(desk_items)
            sought_item_type = target_item.item_type
        else:
            sought_item_type = random.choice(list(ITEM_DESCRIPTIONS.keys()))

        new_customer = Customer(sought_item_type, self.difficulty, target_x)
        self.customer_slots[slot_index] = new_customer
        self.customers.append(new_customer)

    def _remove_customer(self, customer):
        if customer in self.customers:
            self.customers.remove(customer)
            if customer in self.customer_slots:
                idx = self.customer_slots.index(customer)
                self.customer_slots[idx] = None

    def _handle_delivery(self, customer, item):
        if customer.check_item_match(item):
            self.money += REWARD_CORRECT
            self._spawn_popup(customer.x, customer.y - 50, f"+${REWARD_CORRECT}", COLOR_GREEN)
            self._play_sfx('cash')

            # 物品已经在 handle_event 里从列表移除了，不需要再 remove

            self._remove_customer(customer)
            return True
        else:
            self.money += PENALTY_WRONG
            self._spawn_popup(customer.x, customer.y - 50, f"-${abs(PENALTY_WRONG)}", COLOR_RED)
            self._play_sfx('wrong')
            return False

    def _handle_rejection(self, customer):
        sought_type = customer.sought_item_type
        all_items = self.conveyor_items + self.inventory_manager.get_all_items()
        has_item = any(item.item_type == sought_type for item in all_items)

        if has_item:
            penalty = PENALTY_WRONG * 2
            self.money += penalty
            self._spawn_popup(customer.x, customer.y - 50, f"LIAR! ${penalty}", COLOR_RED)
            self._play_sfx('wrong')
        else:
            self.money += -10
            self._spawn_popup(customer.x, customer.y - 50, "-$10", COLOR_YELLOW)
        self._remove_customer(customer)

    def _tell_customer_no_item(self):
        # 已废弃，改用 _handle_rejection
        pass

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # 1. 检查所有顾客的按钮
                button_clicked = False
                for cust in self.customers:
                    if cust.is_arrived and cust.reject_button.handle_click(mouse_pos):
                        self._handle_rejection(cust)
                        button_clicked = True
                        break
                if button_clicked: return

                # 2. 抓取逻辑
                clicked_item = None
                # A. 传送带
                for item in reversed(self.conveyor_items):
                    if item.contains_point(mouse_pos):
                        clicked_item = item
                        item.on_conveyor = False
                        self.conveyor_items.remove(item)
                        # 抓起来后，它暂时不属于任何列表，只在 dragging_item 里
                        break

                # B. 库存
                if not clicked_item:
                    clicked_item = self.inventory_manager.get_item_at_position(mouse_pos)
                    if clicked_item:
                        self.inventory_manager.remove_item(clicked_item)

                if clicked_item:
                    self.dragging_item = clicked_item
                    self.dragging_item.is_selected = True
                    item_pos = clicked_item.get_position()
                    self.drag_offset = (mouse_pos[0] - item_pos[0], mouse_pos[1] - item_pos[1])
                    self._play_sfx('pickup')

            elif event.button == 3:
                target_item = None
                if self.dragging_item: target_item = self.dragging_item
                else:
                    for item in reversed(self.conveyor_items):
                        if item.contains_point(mouse_pos):
                            target_item = item
                            break
                    if not target_item:
                        target_item = self.inventory_manager.get_item_at_position(mouse_pos)
                if target_item:
                    target_item.rotate()
                    self._play_sfx('pickup')

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging_item:
                self.dragging_item.is_selected = False
                self._play_sfx('place')

                # 1. 尝试交付
                delivered = False
                for cust in self.customers:
                    if cust.is_arrived and cust.get_delivery_rect().collidepoint(mouse_pos):
                        if self._handle_delivery(cust, self.dragging_item):
                            self.dragging_item = None
                            delivered = True
                        else:
                            pass # 交付失败，继续放置流程
                        break

                # 2. 放置逻辑
                if not delivered and self.dragging_item:
                    new_x = mouse_pos[0] - self.drag_offset[0]
                    new_y = mouse_pos[1] - self.drag_offset[1]
                    self.dragging_item.set_position(new_x, new_y)

                    if self.dragging_item in self.conveyor_items:
                        # 理论上 dragging_item 已经被移出 conveyor_items 了，
                        # 但这里为了保险起见，如果逻辑有变动：
                        in_desk = self.inventory_manager.is_position_in_desk((new_x, new_y))
                        in_storage = self.inventory_manager.is_position_in_storage((new_x, new_y))

                        if in_desk or in_storage:
                            # 再次确保移除
                            if self.dragging_item in self.conveyor_items:
                                self.conveyor_items.remove(self.dragging_item)

                            if in_storage:
                                self.inventory_manager.add_item_to_storage(self.dragging_item)
                            else:
                                self.inventory_manager.add_item_to_desk(self.dragging_item)

                            self._spawn_popup(new_x, new_y - 20, "Saved!", COLOR_YELLOW)
                            # 物理系统会自动处理重叠
                    else:
                        if self.inventory_manager.is_position_in_storage((new_x, new_y)):
                            self.inventory_manager.move_to_storage(self.dragging_item)
                        else:
                            self.inventory_manager.add_item_to_desk(self.dragging_item)

                    self.dragging_item = None

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_item:
                mouse_pos = pygame.mouse.get_pos()
                new_x = mouse_pos[0] - self.drag_offset[0]
                new_y = mouse_pos[1] - self.drag_offset[1]
                self.dragging_item.set_position(new_x, new_y)

    def _is_in_customer_area(self, pos):
        x, y = pos
        return (CUSTOMER_DELIVERY_AREA['x'] <= x <= CUSTOMER_DELIVERY_AREA['x'] + CUSTOMER_DELIVERY_AREA['width'] and
                CUSTOMER_DELIVERY_AREA['y'] <= y <= CUSTOMER_DELIVERY_AREA['y'] + CUSTOMER_DELIVERY_AREA['height'])

    def _render_item_tooltip(self, screen):
        if not self.hovered_item: return
        mouse_pos = pygame.mouse.get_pos()
        item_name = self.hovered_item.name
        item_category = self.hovered_item.category.upper()
        padding = 10
        name_surface = self.font_small.render(item_name, True, COLOR_WHITE)
        category_surface = self.font_small.render(f"[{item_category}]", True, COLOR_YELLOW)
        w = max(name_surface.get_width(), category_surface.get_width()) + padding * 2
        h = name_surface.get_height() + category_surface.get_height() + padding * 3
        tx, ty = mouse_pos[0] + 15, mouse_pos[1] + 15
        if tx + w > WINDOW_WIDTH: tx = mouse_pos[0] - w - 15
        if ty + h > WINDOW_HEIGHT: ty = mouse_pos[1] - h - 15

        bg = pygame.Rect(tx, ty, w, h)
        pygame.draw.rect(screen, (40, 40, 40), bg, border_radius=5)
        pygame.draw.rect(screen, COLOR_WHITE, bg, 2, border_radius=5)
        screen.blit(name_surface, name_surface.get_rect(centerx=tx+w//2, top=ty+padding))
        screen.blit(category_surface, category_surface.get_rect(centerx=tx+w//2, top=ty+padding+name_surface.get_height()+5))

    def update(self, dt):
        self.shift_time += dt
        self.scroll_offset += CONVEYOR_SPEED * dt
        self.inventory_manager.update(dt)

        for popup in self.popups[:]:
            if not popup.update(dt): self.popups.remove(popup)

        mouse_pos = pygame.mouse.get_pos()
        if not self.dragging_item:
            self.hovered_item = None
            for item in reversed(self.conveyor_items):
                if item.contains_point(mouse_pos):
                    self.hovered_item = item
                    break
            if not self.hovered_item:
                self.hovered_item = self.inventory_manager.get_item_at_position(mouse_pos)
        else:
            self.hovered_item = None

        if self.shift_time >= self.shift_duration:
            self._end_shift()
            return

        self.item_spawn_timer += dt
        if self.item_spawn_timer >= self.item_spawn_interval:
            self.item_spawn_timer = 0
            self._spawn_item_on_conveyor()

        trigger_y = 420
        pause_duration = 3.0
        batch_items = {}
        for item in self.conveyor_items:
            if item.batch_id not in batch_items: batch_items[item.batch_id] = []
            batch_items[item.batch_id].append(item)

        for batch_id, items in batch_items.items():
            if batch_id in self.batch_pause_states:
                pause_state = self.batch_pause_states[batch_id]
                item3 = next((item for item in items if item.item_index == 2), None)
                if item3 and not pause_state['triggered']:
                    if item3.y >= trigger_y:
                        pause_state['paused'] = True
                        pause_state['triggered'] = True
                if pause_state['paused']:
                    pause_state['timer'] += dt
                    if pause_state['timer'] >= pause_duration:
                        pause_state['paused'] = False

        items_to_remove = []
        for item in self.conveyor_items[:]:
            if item.on_conveyor:
                pause_flag = self.batch_pause_states.get(item.batch_id, {'paused': False})
                finished = item.update_conveyor_movement(dt, CONVEYOR_SPEED, CONVEYOR_PATH, pause_flag)
                if finished: items_to_remove.append(item)
        for item in items_to_remove:
            if item in self.conveyor_items: self.conveyor_items.remove(item)

        self.customer_timer += dt
        if self.customer_timer >= self.settings['customer_interval']:
            if None in self.customer_slots:
                self._spawn_customer()
                self.customer_timer = 0
            else:
                self.customer_timer = self.settings['customer_interval'] - 2.0

        for cust in self.customers[:]:
            cust.update(dt)
            if cust.is_timeout():
                self.money += PENALTY_TIMEOUT
                self._spawn_popup(cust.x, cust.y - 50, "Angry!", COLOR_RED)
                self._remove_customer(cust)

    def _end_shift(self):
        from game.game_manager import GameState
        self.game_manager.change_state(GameState.GAME_OVER, money=self.money, day=self.day)

    def _render_conveyor_belt(self, screen):
        if not self.conveyor_texture: return
        path = CONVEYOR_PATH
        tex = self.conveyor_texture
        tex_w = tex.get_width()
        for i in range(len(path) - 1):
            start = path[i]
            end = path[i+1]
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            dist = math.hypot(dx, dy)
            if dist < 1: continue
            angle = math.degrees(math.atan2(-dy, dx))
            segment_surf = pygame.Surface((int(dist), self.belt_width), pygame.SRCALPHA)
            offset = int(self.scroll_offset) % tex_w
            x_pos = offset - tex_w
            while x_pos < dist:
                segment_surf.blit(tex, (x_pos, 0))
                x_pos += tex_w
            rotated_segment = pygame.transform.rotate(segment_surf, angle)
            segment_center = (start[0] + dx/2, start[1] + dy/2)
            segment_rect = rotated_segment.get_rect(center=segment_center)
            screen.blit(rotated_segment, segment_rect)

    def _draw_item_shadow(self, screen, item, offset=(5, 5), scale=1.0):
        if not item.image: return
        source_img = item.image
        if scale != 1.0:
            w = int(source_img.get_width() * scale)
            h = int(source_img.get_height() * scale)
            source_img = pygame.transform.scale(source_img, (w, h))
        try:
            mask = pygame.mask.from_surface(source_img)
            shadow_surf = mask.to_surface(setcolor=(0, 0, 0, 100), unsetcolor=None)
            if scale != 1.0:
                item_rect = item.get_rect()
                shadow_rect = shadow_surf.get_rect(center=item_rect.center)
                shadow_rect.x += offset[0]
                shadow_rect.y += offset[1]
                screen.blit(shadow_surf, shadow_rect)
            else:
                screen.blit(shadow_surf, (item.x + offset[0], item.y + offset[1]))
        except Exception: pass

    def render(self, screen):
        if self.background: screen.blit(self.background, (0, 0))
        else: screen.fill(COLOR_GRAY)

        self._render_conveyor_belt(screen)
        for item in self.conveyor_items:
            self._draw_item_shadow(screen, item, offset=(5, 5))
            item.render(screen)

        for item in self.inventory_manager.storage_items:
            self._draw_item_shadow(screen, item, offset=(5, 5))
        for item in self.inventory_manager.desk_items:
            self._draw_item_shadow(screen, item, offset=(5, 5))

        self.inventory_manager.render(screen)

        for cust in self.customers:
            if cust.is_arrived:
                rect = cust.get_delivery_rect()
                pygame.draw.rect(screen, COLOR_GREEN, rect, 3, border_radius=10)
            cust.render(screen)

        self.hud.render(screen, self.money, self.day, self.shift_time, self.shift_duration)

        if self.dragging_item:
            SCALE_FACTOR = 1.15
            self._draw_item_shadow(screen, self.dragging_item, offset=(20, 20), scale=SCALE_FACTOR)
            original_img = self.dragging_item.image
            scaled_img = pygame.transform.rotozoom(original_img, 0, SCALE_FACTOR)
            scaled_rect = scaled_img.get_rect(center=self.dragging_item.get_rect().center)
            screen.blit(scaled_img, scaled_rect)

        if self.hovered_item and not self.dragging_item:
            self._render_item_tooltip(screen)

        for popup in self.popups:
            popup.render(screen)