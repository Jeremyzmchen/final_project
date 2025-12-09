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
from game.entities.thief import Thief

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
        self.shift_duration = 120

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
                                      "Call Police", None, style='danger', font_size=27
        )
        self.menu_btn = Button(1430, 835, 130, 50,
                               "BACK", None, style='transparent', font_size=42)
        self.spray_btn = Button(
            1470, 400, 50, 150,
            None, None, style='transparent', image_path=ASSETS.get('item_spray')
        )

        # 5. Initialize sound effect
        self.sfx_money = None
        self.sfx_deny = None
        try:
            self.sfx_money = pygame.mixer.Sound(SOUNDS['sfx_money'])
            self.sfx_deny = pygame.mixer.Sound(SOUNDS['sfx_deny'])
            self.sfx_click = pygame.mixer.Sound(SOUNDS['sfx_click'])
            self.sfx_pick = pygame.mixer.Sound(SOUNDS['sfx_pick'])
            self.sfx_drop = pygame.mixer.Sound(SOUNDS['sfx_drop'])
            self.sfx_spray = pygame.mixer.Sound(SOUNDS['sfx_spray'])
            
            self.sfx_click.set_volume(0.8)
            self.sfx_pick.set_volume(0.8)
            self.sfx_drop.set_volume(0.2)
            self.sfx_money.set_volume(1.0)
            self.sfx_deny.set_volume(0.6)
            self.sfx_spray.set_volume(1.0)
        except Exception as e:
            print(f"Failed to load the sfx: {e}")

        # 5. Calling private method and music
        self._init_game()

    def _init_game(self):
        """
        Generate the first batch of items and customer
        """
        self._spawn_item_on_conveyor()  # generate the first batch
        self._spawn_customer()  # generate the first customer
        # Play BGM
        try:
            pygame.mixer.music.load(SOUNDS['bgm_menu'])
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Failed to play BGM: {e}")

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
        self.call_police_btn.update(mouse)
        self.menu_btn.update(mouse)
        self.spray_btn.update(mouse)

        # Calculate the offset to prevent drift
        if event.type == pygame.MOUSEMOTION and self.dragging_item:
            self.dragging_item.set_position(mouse[0] - self.drag_offset[0],
                                            mouse[1] - self.drag_offset[1])
            return

        # 1. Click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if player wants to back to menu
            if self.menu_btn.handle_click(mouse):
                from game.game_manager import GameState
                self.game_manager.change_state(GameState.MENU)
                return

            # [新增] 处理喷雾按钮点击 (Spray Button Click)
            if self.spray_btn.handle_click(mouse):
                self._handle_spray_click()
                return

            # -1.1. First handle: click 'call police' button
            if self.call_police_btn.handle_click(mouse):
                self.sfx_click.play()
                # Determine whether there is a police
                has_police = any(isinstance(c, Police) for c in self.customers)
                self._spawn_popup(mouse[0], mouse[1] - 210, "Police is here!",
                                  COLOR_WHITE) if has_police else self._spawn_police()
                return

            # -1.2. Then handle: player click on 'don't have' button
            clicked_customer = next((c for c in self.customers if c.is_arrived()
                                     and c.reject_button.handle_click(mouse)), None)
            if clicked_customer:
                self.sfx_click.play()
                self._handle_rejection(clicked_customer)
                return

            # -1.3. Then handle: player select items
            item = next((i for i in reversed(self.conveyor_items) if i.contains_point(mouse)), None)
            self.sfx_pick.play()
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
            # dragging stop, release
            self.sfx_drop.play()
            self.dragging_item.is_selected = False
            # item rotate when put down
            if not isinstance(self.dragging_item, StickyNote):
                self.dragging_item.va = random.uniform(-5, 5)

            # -2.1. Check whether there is a npc receiving the item
            target_customer = next(
                (c for c in self.customers if c.is_arrived() and c.get_delivery_rect().collidepoint(mouse)), None)

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
        if self.item_spawn_timer >= self.item_spawn_interval:
            self.item_spawn_timer = 0; self._spawn_item_on_conveyor()

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
        self.spray_btn.render(screen)           # spray
        self.menu_btn.render(screen)            # back to menu
        for p in self.popups: p.render(screen)  # popups info
        self.hud.render(screen, self.money, self.shift_time, self.shift_duration)   # hud
        # Label: If dragging, scale img of items
        if self.dragging_item:
            scale_rate = 1.2
            self._draw_item_shadow(screen, self.dragging_item, (20,20), scale_rate)
            scale_image = pygame.transform.rotozoom(self.dragging_item.image, 0, scale_rate)
            screen.blit(scale_image, scale_image.get_rect(center=self.dragging_item.get_rect().center))
        # Label: If not, show the label
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
            target_x = CONVEYOR_CENTER_X - 60
            target_y = -150 - (i * 150)
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
        empty_cst_space = [i for i, c in enumerate(self.customer_slots) if c is None]
        if not empty_cst_space: return
        idx = random.choice(empty_cst_space)

        # [修改] 独立的小偷生成逻辑
        # 使用 THIEF_SPAWN_PROB (例如 0.25)
        if random.random() < THIEF_SPAWN_PROB:
            t = Thief(CUSTOMER_SLOTS[idx])
            self.customer_slots[idx] = t
            self.customers.append(t)
            return

        # 2. Intelligently assign item request to npc
        desk_items = self.inventory_manager.get_all_items()
        # -2.1. Remove the sticky notes
        valid_items = [i for i in desk_items if i.item_type != 'sticky_note']
        # -2.2. Randomly choose an item
        if valid_items and random.random() < 0.7:
            item_type = random.choice(valid_items).item_type
        else:
            item_type = random.choice(list(ITEM_DESCRIPTIONS.keys()))

        # 3. Assign item request to npc and add npc to customer list
        c = Customer(item_type, CUSTOMER_SLOTS[idx])
        self.customer_slots[idx] = c; self.customers.append(c)

    def _remove_customer(self, c):
        if c in self.customers: self.customers.remove(c)
        if c in self.customer_slots: self.customer_slots[self.customer_slots.index(c)] = None

    def _spawn_police(self):
        """
        Police Spawning System
        A special game plot, related to rejection button, call police, sticky notes
        """
        # 1. Check whether there is empty slot
        empty_plc_space = [i for i, slot in enumerate(self.customer_slots) if slot is None]
        if not empty_plc_space:
            self._spawn_popup(WINDOW_WIDTH - 100, WINDOW_HEIGHT - 480, "No SPACE!", COLOR_WHITE)
            return
        idx = empty_plc_space[0]

        # 2. Instantiation and Set attributes
        p = Police(CUSTOMER_SLOTS[idx])
        self.customer_slots[idx] = p
        self.customers.append(p)

    def _handle_spray_click(self):
        """
        玩家点击了喷雾按钮。
        逻辑：全屏索敌，找到小偷并扣血。
        """
        # 播放音效
        self.sfx_spray.play()

        # 1. 查找场上是否有小偷
        # (可能有多个，如果有多个就都喷，或者只喷第一个，这里逻辑是都喷)
        thieves = [c for c in self.customers if isinstance(c, Thief)]

        if not thieves:
            # 没小偷还乱按 -> 惩罚
            self.money += PENALTY_CLICK
            self._spawn_popup(1500, 410, "No Thief!", COLOR_WHITE)
            return

        # 2. 对小偷造成伤害
        for t in thieves:
            is_dead = t.take_damage()  # 扣1血

            if is_dead:
                # 血量归零，赶走
                self._spawn_popup(t.x, t.y + 50, "Begone!", COLOR_WHITE)
                self._remove_customer(t)
            else:
                # 还没死，飘字提示剩余次数
                self._spawn_popup(t.x, t.y + 50, "Hit!", COLOR_WHITE)

    def _handle_delivery(self, c, item):
        """Handle customer's delivery process"""
        # 1. Check if not customers
        if isinstance(c, Police):
            return self._handle_police_delivery(c, item)

        # 2. Check if item match
        if c.check_item_match(item):
            self.money += REWARD_CORRECT
            self._spawn_popup(c.x, c.y + 100, f"+${REWARD_CORRECT}", COLOR_WHITE)
            self.sfx_money.play()
            self._remove_customer(c)
            return True
        else:
            self.money += PENALTY_WRONG
            self._spawn_popup(c.x, c.y + 100, "Not this item!", COLOR_WHITE)
            self.sfx_deny.play()
            return False

    def _handle_police_delivery(self, police, item):
        """
        Handle police's delivery process
        Two stages: 1.wait for sticky_note, 2.wait for matched_item
        """
        # Stage one
        if police.police_state == 'waiting_for_note':
            if isinstance(item, StickyNote):
                police.receive_note(item)
                self._spawn_popup(police.x, police.y + 50, "File Accepted.", COLOR_WHITE)
                return True
            else:
                self._spawn_popup(police.x, police.y + 50, "Need Case Note!", COLOR_RED)
                self.sfx_deny.play()
                return False

        # Stage two
        elif police.police_state == 'waiting_for_evidence':
            # Check if player delivery the sticky_note again
            if isinstance(item, StickyNote):
                self._spawn_popup(police.x, police.y - 50, "I have the file.", COLOR_RED)
                return False

            # Check item match
            if item.item_type == police.target_item_type:
                self.money += REWARD_CORRECT
                self._spawn_popup(police.x, police.y + 50, "Case Solved!", COLOR_WHITE)
                self._remove_customer(police)
                return True
            else:
                self.money += PENALTY_WRONG
                self._spawn_popup(police.x, police.y - 50, "Wrong Item!", COLOR_RED)
                self.sfx_deny.play()
                self._remove_customer(police)
                return False

        return False

    def _handle_rejection(self, c):
        """player click the 'don't have' button"""
        note = StickyNote(c.x, 350, c.sought_item_type)
        self.inventory_manager.add_item_to_desk(note)
        self._remove_customer(c)

    def _spawn_popup(self, x, y, text, c=COLOR_WHITE):
        """
        UI, popup messages for player(warning, tips)
        param: x: posX, y: posY, text: content, c: color
        """
        self.popups.append(FloatingText(x, y, text, c))

    # TODO AI Calculate the position of the conveyor belt texture
    def _render_conveyor_belt(self, screen):
        """UI, popup messages for player(warning, tips)"""
        if not self.conveyor_texture: return

        tex_h = self.conveyor_texture.get_height()
        # Calculate the offset for vertical scrolling
        y_offset = int(self.scroll_offset) % tex_h
        draw_x = CONVEYOR_CENTER_X - self.belt_width // 2
        for y in range(-tex_h, WINDOW_HEIGHT + tex_h, tex_h):
            screen.blit(self.conveyor_texture, (draw_x, y + y_offset))

    # TODO AI Calculate the position of the conveyor belt texture
    def _draw_item_shadow(self, screen, item, off=(5,5), sc=1.0):
        """UI, Draw shadow for item"""
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

    # TODO AI Calculate the position of the conveyor belt texture
    def _render_item_tooltip(self, screen):
        """UI, Draw item tooltip"""
        if not self.hovered_item: return
        mouse_pos = pygame.mouse.get_pos()
        item_name = self.hovered_item.name
        name_surf = self.font_small.render(item_name, True, COLOR_WHITE)

        padding_x = 10; padding_y = 8
        width = name_surf.get_width() + padding_x * 2; height = name_surf.get_height() + padding_y * 2
        x = mouse_pos[0] + 20; y = mouse_pos[1] - 30
        if x + width > WINDOW_WIDTH: x = mouse_pos[0] - width - 10
        if y + height > WINDOW_HEIGHT: y = mouse_pos[1] - height - 10
        if self.label_image:
            bg = pygame.transform.scale(self.label_image, (width, height))
            screen.blit(bg, (x, y))
            text_x = x + (width - name_surf.get_width()) // 2
            text_y = y + (height - name_surf.get_height()) // 2
            screen.blit(name_surf, (text_x, text_y))
