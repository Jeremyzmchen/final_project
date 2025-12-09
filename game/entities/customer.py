"""
Game Entity - Customer (NPC)
A customer walks in, shows a request dialog, waits with decreasing patience,
and accepts delivery or a "Don't Have" rejection.
"""

import pygame
import random
from config.settings import *
from game.ui.button import Button


class Customer:
    """Customer NPC who requests a specific item type and waits at the counter."""

    def __init__(self, sought_item_type, target_x=WINDOW_WIDTH//2):
        """
        Initialize a customer who is looking for a specific item type.

        Args:
            sought_item_type (str): Item type key (must match ITEM_DESCRIPTIONS keys)
            target_x (int): X position of the customer slot (counter position)
        """
        # Requested item type (matching uses: item.item_type == sought_item_type)
        self.sought_item_type = sought_item_type
        # Config dict for this item type (name/keywords/etc.)
        self.item_data = ITEM_DESCRIPTIONS.get(sought_item_type, {})

        # UI hint text only (not used for matching)
        self.description = self._generate_description()

        # Waiting / patience (seconds)
        self.max_wait_time = CUSTOMER_WAIT_TIME
        self.wait_time = 0
        self.patience = 1.0  # 1.0 -> 0.0

        # Position & movement
        self.x = target_x
        self.y = -100  # spawn above the screen
        self.target_y = CUSTOMER_Y
        self.speed = 400  # px/s

        # Simple state machine: walking_in -> waiting
        self.state = 'walking_in'

        # Assets
        self.image = None
        self.bubble_image = None
        self._load_resources()

        # Dialog is shown after arrival
        self.dialog_visible = False

        # Fonts
        self.font = pygame.font.Font(FONT_PATH, 24)
        self.font_small = pygame.font.Font(FONT_PATH, 20)

        # "Don't Have" button (click handling is done in GameplayState)
        # The position is updated dynamically in update().
        self.reject_button = Button(
            0, 0, 150, 35,
            "Don't Have",
            None,
            style='grey',
            font_size=24
        )

    def is_arrived(self):
        """True if the customer has reached the counter and is waiting."""
        return self.state == 'waiting'

    def get_delivery_rect(self):
        """
        Delivery / drop zone for this customer.

        GameplayState checks whether the mouse release position is inside this rect
        to decide which customer receives the dragged item.
        """
        return pygame.Rect(self.x - 100, self.y - 100, 200, 250)

    def _generate_description(self):
        """
        Generate a short randomized hint sentence based on item keywords.

        Note: This is only for UI. The real matching is done by item_type equality.
        """
        # TODO 12.07 REVISE
        item_name = self.item_data.get('name', 'Item')
        descriptions = [
            f"I lost my {item_name}",
            f"I am looking for {item_name}",
            f"Seen my {item_name}?",
            f"My {item_name} missing",
        ]
        return random.choice(descriptions)

    def _load_resources(self):
        """Load customer sprite and bubble frame. Draw placeholders if loading fails."""

        # 1) Load NPC sprite (random). If anything fails, draw a simple placeholder.
        customer_images = [
            'npc_1', 'npc_2', 'npc_3', 'npc_4',
            'npc_5', 'npc_6', 'npc_7', 'npc_8',
            'npc_9', 'npc_10', 'npc_11', 'npc_12'
        ]
        image_key = random.choice(customer_images)

        try:
            path = ASSETS.get(image_key)
            if not path:
                raise KeyError(f"Missing ASSETS key: {image_key}")  # force fallback

            img = pygame.image.load(path)
            self.image = pygame.transform.scale(img, (375, 470))
        except Exception:
            self.image = pygame.Surface((100, 100))
            self.image.fill((150, 150, 200))
            pygame.draw.circle(self.image, (255, 200, 150), (50, 50), 40)

        # 2) Load bubble frame; if it fails, render() will draw a basic bubble
        try:
            self.bubble_image = pygame.image.load('assets/images/icons/bubble_box.png')
        except Exception:
            self.bubble_image = None

    def update(self, dt):
        """
        Update customer movement, waiting timer/patience, and button hover state.

        Args:
            dt (float): Delta time in seconds since last frame.
        """
        # State 1: walk into the scene
        if self.state == 'walking_in':
            self.y += self.speed * dt
            if self.y >= self.target_y:
                self.y = self.target_y
                self.state = 'waiting'
                self.dialog_visible = True

        # State 2: waiting at counter
        elif self.state == 'waiting':
            self.wait_time += dt
            self.patience = max(
                0,
                1.0 - (self.wait_time / self.max_wait_time)
            )

            # Anchor the button under the dialog bubble
            dialog_height = 120
            bubble_bottom_y = 200 + dialog_height

            # Center button under the bubble
            btn_x = self.x - self.reject_button.rect.width // 2
            btn_y = bubble_bottom_y + 5

            self.reject_button.rect.topleft = (btn_x, btn_y)
            self.reject_button.update(pygame.mouse.get_pos())

    def is_timeout(self):
        """Return True if the customer has waited too long."""
        return self.wait_time >= self.max_wait_time

    def check_item_match(self, item):
        """Return True if delivered item matches the requested item type."""
        return item.item_type == self.sought_item_type

    def get_patience_color(self):
        """Return a color based on remaining patience (blue -> orange -> red)."""
        if self.patience > 0.6:
            return COLOR_BLUE
        elif self.patience > 0.3:
            return COLOR_ORANGE
        else:
            return COLOR_RED

    def render(self, screen):
        """
        Render the customer sprite, dialog bubble, text, patience bar, and button.

        Args:
            screen (pygame.Surface): The game screen surface to draw on.
        """
        # 1) Draw customer sprite
        if self.image:
            image_rect = self.image.get_rect(center=(self.x, self.y))
            screen.blit(self.image, image_rect)

        # 2) Draw dialog UI (if active)
        if self.dialog_visible:
            dialog_width = 268
            dialog_height = 135
            dialog_x = self.x - dialog_width // 2
            dialog_y = 205

            # Bubble background (image preferred, rectangle fallback)
            # - If bubble image exists, blit it.
            # - Otherwise, fallback to a simple rounded rectangle
            if self.bubble_image:
                bubble_scaled = pygame.transform.scale(
                    self.bubble_image,
                    (dialog_width, dialog_height)
                )
                screen.blit(bubble_scaled, (dialog_x, dialog_y))
            else:
                pygame.draw.rect(
                    screen, COLOR_WHITE,
                    (dialog_x, dialog_y, dialog_width, dialog_height),
                    border_radius=10
                )
                pygame.draw.rect(
                    screen, COLOR_BLACK,
                    (dialog_x, dialog_y, dialog_width, dialog_height),
                    2,
                    border_radius=10
                )

            # Render wrapped dialog text (centered)
            lines = self._wrap_text(
                self.description,
                self.font,
                dialog_width - 30
            )
            line_height = 25
            total_text_height = len(lines) * line_height
            content_area_height = dialog_height - 30
            text_start_y = (
                dialog_y
                + (content_area_height - total_text_height) // 2
                + 5
            )

            for i, line in enumerate(lines):
                text = self.font.render(line, True, COLOR_BLACK)
                text_rect = text.get_rect(
                    centerx=dialog_x + dialog_width // 2,
                    top=text_start_y + i * line_height
                )
                screen.blit(text, text_rect)

            # Patience bar (background + fill)
            bar_w = dialog_width - 100
            bar_x = dialog_x + 45
            bar_y = dialog_y + dialog_height - 35

            pygame.draw.rect(
                screen,
                COLOR_DARK_GRAY,
                (bar_x, bar_y, bar_w, 10),
                border_radius=4
            )
            fill = int(bar_w * self.patience)
            if fill > 0:
                pygame.draw.rect(
                    screen,
                    self.get_patience_color(),
                    (bar_x, bar_y, fill, 10),
                    border_radius=4
                )

            # "Don't Have" button
            self.reject_button.render(screen)

    def _wrap_text(self, text, font, max_width):
        """Wrap text into multiple lines so each line fits within max_width."""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines if lines else [text]