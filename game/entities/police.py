"""
Game Entity - Police (NPC)
A special customer that handles case reports. The player must first submit a case note,
then deliver the matching evidence item. Police cannot be dismissed.
"""

import pygame
from game.entities.customer import Customer
from config.settings import ASSETS, WINDOW_WIDTH


class Police(Customer):
    """Police NPC: a special customer with a two-step case flow."""

    def __init__(self, target_slot):
        """
        Create a police NPC at the given customer slot.

        Args:
            target_slot (int): X position of the slot (counter position)
        """
        # uses Customer base setup (movement/patience/dialog)
        super().__init__('unknown', target_slot)  

        self.wait_time = 0  # reset timer when police arrives / changes stage

        self.police_state = 'waiting_for_note'  # stage 1 -> stage 2
        self.target_item_type = None  # set after receiving a note
        self.case_id = None  # set after receiving a note

        self.description = "Officer on duty.\nAny cases to report?"  # UI text

        # hide "Don't Have" (police can't be rejected)
        self.reject_button.rect.topleft = (-1000, -1000) 

    def _load_resources(self):
        """Load police sprite and optional bubble image."""
        try:
            # fallback path if key missing
            path = ASSETS.get('police', 'assets/images/police.png')  
            img = pygame.image.load(path)
            self.image = pygame.transform.scale(img, (375, 470))
        except Exception:
            self.image = pygame.Surface((100, 100))  # placeholder sprite
            self.image.fill((100, 100, 100))
            pygame.draw.circle(self.image, (20, 50, 180), (50, 50), 40)

        # bubble image is optional; if it fails, 
        # Customer.render() will draw a basic bubble
        try:
            self.bubble_image = pygame.image.load('assets/images/icons/bubble_box.png')
        except Exception:
            self.bubble_image = None

    def receive_note(self, note_item):
        """Accept a case note and move to the evidence stage."""
        self.police_state = 'waiting_for_evidence'
        # evidence to look for
        self.target_item_type = note_item.sought_item_type  
        self.case_id = note_item.case_id
        # update dialog text
        self.description = f"Case #{self.case_id}...\nFind the missing item."  
        self.wait_time = 0  # reset patience timer when stage changes

    def update(self, dt):
        """Update movement/patience via parent, then keep reject button hidden."""
        super().update(dt)
        self.reject_button.rect.topleft = (-1000, -1000)  # keep hidden every frame
