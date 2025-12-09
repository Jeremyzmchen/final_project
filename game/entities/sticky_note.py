"""
Game Entity - Sticky Note (Item)
A simple case note that carries case info (clue).
Used by Police NPC: submit note first, then deliver the matching evidence item.
"""

import pygame
import random
from config.settings import *
from game.entities.item import Item
from config.settings import COLOR_BLACK, ITEM_DESCRIPTIONS  # TODO 12.07 REVISE


class StickyNote(Item):
    """Case note item: static paper that stores the case target info."""

    def __init__(self, x, y, sought_item_type):
        # Basic identity
        self.item_type = 'sticky_note'
        self.name = "Case Note"
        self.keywords = ['note', 'clue', 'paper']  # UI only

        # Core case data (Police reads these fields)
        # what item type the customer wanted
        self.sought_item_type = sought_item_type  
        self.clue_text = self._generate_clue_text(sought_item_type)     # TODO 12.07 REVISE
        self.case_id = random.randint(10, 99)

        # Size & position
        self.width = 55
        self.height = 70
        self.x = x
        self.y = y

        # TODO Physics disabled: keep note static
        self.friction = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.va = 0.0
        self.angle = 0.0

        # State flags kept for compatibility with the rest of the system
        self.is_selected = False
        self.in_storage = False
        self.on_conveyor = False
        self.batch_id = -1
        self.item_index = -1
        self.conveyor_start_offset = 0
        self.conveyor_vertical_offset = 0

        # Build image and rect
        self._generate_image()
        self.rect = self.image.get_rect(center=(x, y))

    # TODO 12.07 REVISE
    def _generate_clue_text(self, item_type):
        """Helper to pick a random keyword or category as the clue."""
        data = ITEM_DESCRIPTIONS.get(item_type, {})
        
        # Get all the keywords and categories of this item.
        keywords = data.get('keywords', [])
        category = data.get('category')
        
        # Build a candidate pool
        candidates = []
        if keywords:
            candidates.extend(keywords)
        if category:
            candidates.append(category)
            
        # Randomly select one feature as a clue.
        return random.choice(candidates)

    def _generate_image(self):
        """Generate a simple sticky note surface (no rotation)."""
        # final image surface
        self.image = pygame.Surface((self.width, self.height))  
        self.image.fill(COLOR_YELLOW)  # yellow paper background

        # Red "CASE" stamp label (top-left)
        font_small = pygame.font.SysFont(FONT_PATH, 16, bold=True)
        pygame.draw.rect(self.image, COLOR_RED, (5, 5, 40, 15))
        lbl = font_small.render("CASE", True, COLOR_WHITE)
        self.image.blit(lbl, (8, 6))

        # Case ID
        font_id = pygame.font.SysFont(FONT_PATH, 16, bold=True)
        id_text = font_id.render(f"ID: {self.case_id}", True, COLOR_BLACK)
        self.image.blit(id_text, (10, 25))

        font_clue = pygame.font.SysFont(FONT_PATH, 24)

        text = font_clue.render(self.clue_text, True, COLOR_BLACK)
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2 + 15))
        self.image.blit(text, text_rect)