"""
Responsible for managing all the core logic
    1. Game Loop, eg: time, money, batch spawning, game state
    2. Entity Lifecycle, eg: app / disapp of npcs and items
    3. Story Plot: interaction with police
"""
import pygame, random, math, os
from config.settings import *
from game.entities.item import Item
from game.entities.customer import Customer
from game.managers.inventory_manager import InventoryManager
from game.ui.hud import HUD
from game.ui.popup import FloatingText
from game.ui.button import Button
from game.entities.sticky_note import StickyNote
from game.entities.police import Police

class GameplayState:
    def __init__(self, game_manager):
        """
        Args:
            game_manager: manage game status and data
        """
        # 1. Initialize base data
        self.game_manager = game_manager
        self.money = 0
        self.shift_time = 0
        self.shift_duration = 5
        # TODO: an extension for next update
        #if 'money' in game_manager.game_data:
        #    self.money = game_manager.game_data['money']

        # 2. Initialize core game system
        self.inventory_manager = InventoryManager()
        self.customers = []
        self.customer_slots = [None] * len(CUSTOMER_SLOTS)
        self.customer_timer = 0
        self.customer_interval = CUSTOMER_INTERVAL  # interval of generation
        self.conveyor_items = []
        self.item_spawn_timer = 0
        self.item_spawn_interval = ITEM_SPAWN_INTERVAL

        # 3. Initialize batch management
        self.current_batch_id = 0
        self.batch_pause_states = {}    # eg, key:5, value:{'paused': True, 'timer': 1.2, 'triggered': True}

        # 4. Initialize ui
        self.conveyor_texture = None
        self.scroll_offset = 0
        self.scroll_speed = CONVEYOR_SPEED
        self.belt_width = 160   # to put items in the middle
        self.hud = HUD()
        self.popups = []
        self._load_background()
        self._load_conveyor_texture()
        self.label_image = None
        try:
            self.label_image = pygame.image.load('assets/images/icons/label.png')
        except Exception as e:
            print(f"Failed to load the conveyor belt image: {e}")
        self.dragging_item = None
        self.drag_offset = (0, 0)  # prevent items from drifting
        self.hovered_item = None  # for tooltip
        self.font_small = pygame.font.Font(FONT_PATH, 24)
        self.call_police_btn = Button(1430, 570, 130, 70,
                                      "Call Police", None, style='danger', font_size=27)
        # 5. Calling private method and music
        self._init_game()

    def _init_game(self):
        """
        Generate the first batch of items and customer
        """
        self._spawn_item_on_conveyor()
        self._spawn_customer()
        try:
            pygame.mixer.music.load('assets/sounds/bgm_gameplay.mp3')
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Failed to load the music: {e}")

    def _load_background(self):
        """
        load background image
        """
        self.background = pygame.transform.scale(
            pygame.image.load(ASSETS['bg_main']),
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )

    def _load_conveyor_texture(self):
        """
        load conveyor_texture image
        """
        try:
            self.conveyor_texture = pygame.image.load('assets/images/conveyor_belt.png')
            self.belt_width = self.conveyor_texture.get_width()
        except Exception as e:
            print(f"Failed to load the conveyor belt image: {e}")

    def _end_shift(self):
        """
        state shift, game over
        """
        from game.game_manager import GameState
        self.game_manager.change_state(GameState.GAME_OVER, money=self.money)

    def handle_event(self, event):
        """
        Handles player input events (Mouse clicks, dragging, and releasing).
        """
        mouse = pygame.mouse.get_pos()
        self.call_police_btn.update(mouse)  # for hover
        # Calculate the offset to prevent drift
        if event.type == pygame.MOUSEMOTION and self.dragging_item:
            self.dragging_item.set_position(mouse[0] - self.drag_offset[0], mouse[1] - self.drag_offset[1])
            return

        # 1. Click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # -1.1. First handle: click 'call police' button
            if self.call_police_btn.handle_click(mouse):
                # Determine whether there is a police
                has_police = any(isinstance(c, Police) for c in self.customers)
                self._spawn_popup(mouse[0], mouse[1], "Police is here!",
                                  COLOR_BLACK) if has_police else self._spawn_police()
                return

            # -1.2. Then handle: player click on 'don't have' button
            clicked_customer = next((c for c in self.customers if c.is_arrived
                                     and c.reject_button.handle_click(mouse)), None)
            if clicked_customer:
                self._handle_rejection(clicked_customer)
                return

            # -1.3. Then handle: player select items
            item = next((i for i in reversed(self.conveyor_items) if i.contains_point(mouse)), None)
            # -1.3.1. Check item in conveyor belt first, then desk
            if item:
                item.on_conveyor = False
                self.conveyor_items.remove(item)
            else:
                item = self.inventory_manager.get_item_at_position(mouse)
                if item: self.inventory_manager.remove_item(item)

            # -1.4. Finally handle dragging
            if item:
                self.dragging_item = item
                self.dragging_item.is_selected = True
                self.drag_offset = (mouse[0] - item.x, mouse[1] - item.y)

        # 2. Release
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.dragging_item:
            self.dragging_item.is_selected = False

            # -2.1. Check whether there is a npc receiving the item
            target_customer = next(
                (c for c in self.customers if c.is_arrived and c.get_delivery_rect().collidepoint(mouse)), None)

            # -2.2. Check delivery process
            if not (target_customer and self._handle_delivery(target_customer, self.dragging_item)):
                self.dragging_item.set_position(mouse[0] - self.drag_offset[0], mouse[1] - self.drag_offset[1])
                self.inventory_manager.add_item_to_desk(self.dragging_item)
            self.dragging_item = None

    def update(self, dt):
        """update game status"""
        # 1.Check time
        self.shift_time += dt
        if self.shift_time >= self.shift_duration: self._end_shift(); return

        # 2.Update spawn_item state
        self.item_spawn_timer += dt
        if self.item_spawn_timer >= self.item_spawn_interval: self.item_spawn_timer = 0; self._spawn_item_on_conveyor()

        # 3.Items on conveyor(batch, pause)
        # -3.1. Whether trigger pause or not
        for item in self.conveyor_items:
            if getattr(item, 'is_pause_trigger', False) and item.on_conveyor:
                state = self.batch_pause_states.get(item.batch_id)
                if state and not state['triggered'] and item.y >= CONVEYOR_PAUSE_TRIGGER_Y:
                    state['paused'] = True
                    state['triggered'] = True
        # -3.2. Update pause state
        for state in self.batch_pause_states.values():
            if state['paused']:
                state['timer'] += dt
                if state['timer'] >= 5.0:
                    state['paused'] = False

        # 4.Items on conveyor(move, remove)
        removes = []
        for i in self.conveyor_items[:]:
            if i.on_conveyor:   # check whether item is not being dragged
                paused = self.batch_pause_states.get(i.batch_id, {'paused': False})
                # calling 'item' module method, checking items is in screen or not
                if i.update_conveyor_movement(dt, CONVEYOR_SPEED, paused):
                    removes.append(i)
        for r in removes: self.conveyor_items.remove(r)

        # 5.Update spawn_customer state
        self.customer_timer += dt
        if self.customer_timer >= self.customer_interval:
            if None in self.customer_slots: self._spawn_customer(); self.customer_timer = 0
            else: self.customer_timer -= 2    # delay 2seconds and check again
        for c in self.customers[:]:
            c.update(dt)
            if c.is_timeout(): self.money += PENALTY_TIMEOUT; self._remove_customer(c)

        # 6.UI update
        # -6.1. Check popup state
        for p in self.popups[:]:
            if not p.update(dt): self.popups.remove(p)

        # -6.2. Check status for hover(tooltip)
        mouse = pygame.mouse.get_pos()
        if not self.dragging_item:
            self.hovered_item = None
            # Check conveyor first, then desk
            for i in reversed(self.conveyor_items):
                if i.contains_point(mouse): self.hovered_item = i; break
            if not self.hovered_item:
                self.hovered_item = self.inventory_manager.get_item_at_position(mouse)
        else: self.hovered_item = None

        # -6.3. Determine whether conveyor belt scroll
        should_scroll = False
        if self.conveyor_items:
            for item in self.conveyor_items:
                if not self.batch_pause_states.get(item.batch_id, {'paused': False})['paused']:
                    should_scroll = True; break
        if should_scroll: self.scroll_offset += CONVEYOR_SPEED * dt

        # -6.4. Update status of items on desk(collision,physics)
        self.inventory_manager.update(dt)

    def render(self, screen):
        # 1. Render background and belt texture
        if self.background: screen.blit(self.background, (0,0))
        else: screen.fill(COLOR_GRAY)
        self._render_conveyor_belt(screen)

        # 2. Render items
        for i in self.conveyor_items:
            self._draw_item_shadow(screen, i);
            i.render(screen)
        for i in self.inventory_manager.desk_items:
            self._draw_item_shadow(screen, i)
        self.inventory_manager.render(screen)

        # 3. Render npc
        for c in self.customers: c.render(screen)

        # 4. Render UI
        self.call_police_btn.render(screen)     # call_police
        for p in self.popups: p.render(screen)  # popups info
        self.hud.render(screen, self.money, self.shift_time, self.shift_duration)   # hud
        # -4.1. If dragging, scale img of items
        if self.dragging_item:
            scale_rate = 1.2
            self._draw_item_shadow(screen, self.dragging_item, (20,20), scale_rate)
            scale_image = pygame.transform.rotozoom(self.dragging_item.image, 0, scale_rate)
            screen.blit(scale_image, scale_image.get_rect(center=self.dragging_item.get_rect().center))
        # -4.2. If not, show the label
        if self.hovered_item and not self.dragging_item: self._render_item_tooltip(screen)


    # private_Methods
    def _spawn_item_on_conveyor(self):
        """
        Item Batch Spawning System
        Each batch of items shares a batch_id, which is used for paused status
        """
        self.batch_pause_states[self.current_batch_id] = {'paused': False, 'timer': 0, 'triggered': False}

        # 1. Generate items in a batch
        for i in range(ITEMS_PER_BATCH):
            # -1.1. Randomly choose an item
            item_type = random.choice(list(ITEM_DESCRIPTIONS.keys()))

            # -1.2. Instantiation
            item = Item(item_type)

            # -1.3 Set item attributes
            item.on_conveyor = True
            item.item_index = i
            item.batch_id = self.current_batch_id
            if i == CONVEYOR_PAUSE_AT_INDEX:
                item.is_pause_trigger = True
            target_x = CONVEYOR_CENTER_X
            target_y = -150 - (i * 180)
            item.set_position(target_x, target_y)

            # -1.4. Append to list
            self.conveyor_items.append(item)

        # 2. Set batch id
        self.current_batch_id += 1

    def _spawn_customer(self):
        """
        Customer Spawning System and Match demand
        Responsible for generating new customers when the counter is idle
        Dynamically adjusts the items based on the current desktop status
        """
        # 1. Check whether there is empty slot
        empty = [i for i, c in enumerate(self.customer_slots) if c is None]
        if not empty: return
        idx = random.choice(empty)

        # 2. Intelligently assign item request to npc
        desk_items = self.inventory_manager.get_all_items()
        # -2.1. Remove the sticky notes
        valid_items = [i for i in desk_items if i.item_type != 'sticky_note']
        type = random.choice(valid_items).item_type if valid_items and random.random() < 0.7 else random.choice(list(ITEM_DESCRIPTIONS.keys()))

        c = Customer(type, CUSTOMER_SLOTS[idx])
        self.customer_slots[idx] = c; self.customers.append(c)

    def _spawn_police(self):
        empty_indices = [i for i, slot in enumerate(self.customer_slots) if slot is None]
        if not empty_indices:
            self._spawn_popup(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, "No Space!", COLOR_RED)
            return
        idx = empty_indices[0]
        p = Police(CUSTOMER_SLOTS[idx])
        self.customer_slots[idx] = p
        self.customers.append(p)
        self._spawn_popup(p.x, p.y-80, "Police Arrived!", COLOR_BLUE)

    def _spawn_popup(self, x, y, text, c=COLOR_WHITE):
        self.popups.append(FloatingText(x, y, text, c))

    def _remove_customer(self, c):
        if c in self.customers: self.customers.remove(c)
        if c in self.customer_slots: self.customer_slots[self.customer_slots.index(c)] = None

    # 警察
    def _handle_delivery(self, c, item):
        if isinstance(c, Police):
            if c.police_state == 'waiting_for_note':
                if isinstance(item, StickyNote):
                    c.receive_note(item)
                    self._spawn_popup(c.x, c.y-50, "File Accepted", COLOR_YELLOW)
                    return True
                else:
                    self._spawn_popup(c.x, c.y-50, "Need Case Note!", COLOR_RED)
                    return False
            elif c.police_state == 'waiting_for_evidence':
                if isinstance(item, StickyNote):
                    self._spawn_popup(c.x, c.y-50, "I have the file.", COLOR_YELLOW)
                    return False
                if item.item_type == c.target_item_type:
                    self.money += REWARD_CORRECT * 1.5
                    self._spawn_popup(c.x, c.y-50, "Case Solved!", COLOR_GREEN)
                    self._remove_customer(c)
                    return True
                else:
                    self.money += PENALTY_WRONG
                    self._spawn_popup(c.x, c.y-50, "Wrong Evidence!", COLOR_RED)
                    self._remove_customer(c)
                    return False
            return False

        if c.check_item_match(item):
            self.money += REWARD_CORRECT; self._spawn_popup(c.x, c.y-50, f"+${REWARD_CORRECT}", COLOR_GREEN)
            self._remove_customer(c); return True
        else:
            self.money += PENALTY_WRONG; self._spawn_popup(c.x, c.y-50, "WRONG!", COLOR_RED); return False

    def _handle_rejection(self, c):
        if isinstance(c, Police): return
        note = StickyNote(c.x, 350, c.sought_item_type)
        self.inventory_manager.add_item_to_desk(note)
        self._spawn_popup(c.x, c.y-50, "Filed Case", COLOR_YELLOW)
        self._remove_customer(c)

    def _render_conveyor_belt(self, screen):
        if not self.conveyor_texture: return

        # 获取纹理高度
        tex_h = self.conveyor_texture.get_height()

        # 计算垂直滚动的偏移量 (取模运算实现无限循环)
        y_offset = int(self.scroll_offset) % tex_h

        # 确定绘制的 X 坐标 (左上角)
        draw_x = CONVEYOR_CENTER_X - self.belt_width // 2

        # [修改] 垂直平铺绘制
        # 从 -tex_h 开始画，确保屏幕顶部没有空隙
        for y in range(-tex_h, WINDOW_HEIGHT + tex_h, tex_h):
            screen.blit(self.conveyor_texture, (draw_x, y + y_offset))

    def _draw_item_shadow(self, screen, item, off=(5,5), sc=1.0):
        if not item.image: return
        img = item.image
        if sc != 1.0: img = pygame.transform.scale(img, (int(img.get_width()*sc), int(img.get_height()*sc)))
        try:
            mask = pygame.mask.from_surface(img)
            shad = mask.to_surface(setcolor=(0,0,0,100), unsetcolor=None)
            if sc != 1.0:
                r = shad.get_rect(center=item.get_rect().center); r.x+=off[0]; r.y+=off[1]; screen.blit(shad, r)
            else: screen.blit(shad, (item.x+off[0], item.y+off[1]))
        except: pass

    def _render_item_tooltip(self, screen):
        if not self.hovered_item: return
        mouse_pos = pygame.mouse.get_pos()
        item_name = self.hovered_item.name
        name_surf = self.font_small.render(item_name, True, COLOR_WHITE)
        padding_x = 10; padding_y = 8
        width = name_surf.get_width() + padding_x * 2; height = name_surf.get_height() + padding_y * 2
        x = mouse_pos[0] + 20; y = mouse_pos[1] + 20
        if x + width > WINDOW_WIDTH: x = mouse_pos[0] - width - 10
        if y + height > WINDOW_HEIGHT: y = mouse_pos[1] - height - 10
        if self.label_image:
            bg = pygame.transform.scale(self.label_image, (width, height))
            screen.blit(bg, (x, y))
            text_x = x + (width - name_surf.get_width()) // 2
            text_y = y + (height - name_surf.get_height()) // 2
            screen.blit(name_surf, (text_x, text_y))
