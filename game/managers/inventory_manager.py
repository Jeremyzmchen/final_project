import pygame
import random
from config.settings import DESK_AREA

class InventoryManager:

    def __init__(self):
        # a list that record the desk item
        self.desk_items = []

    '''
    where is the storage?
    '''
    def add_item_to_desk(self, item):
        # move out from the storage
        item.in_storage = False
        self.desk_items.append(item)

    def remove_item(self, item):
        if item in self.desk_items:
            self.desk_items.remove(item)

    '''
    why need reverse there is not front and back
    '''
    def get_item_at_position(self, pos):
        # if pos on an item return item else None
        for item in reversed(self.desk_items):
            # reverse for the front item
            if item.contains_point(pos):
                return item
        return None

    '''
    this one is necessary
    '''
    def get_all_items(self):
        return self.desk_items

    def is_position_in_desk(self, pos):
        # determine whether in desk
        x, y = pos
        return (DESK_AREA['x'] <= x <= DESK_AREA['x'] + DESK_AREA['width'] and
                DESK_AREA['y'] <= y <= DESK_AREA['y'] + DESK_AREA['height'])


    def render(self, screen):
        # render the item
        for item in self.desk_items:
            item.render(screen)

    def update(self, dt):
        # update the item position, this function embedded in item class
        for item in self.desk_items:
            item.update_physics(dt)

            # limitation for the desk canvas
            desk_rect = pygame.Rect(DESK_AREA['x'], DESK_AREA['y'], DESK_AREA['width'], DESK_AREA['height'])
            if not desk_rect.contains(item.get_rect()): #determine whether item inside the desk, contain is the pygame embedded function
                if item.x < desk_rect.left: #left side
                    item.x = desk_rect.left; item.vx = 0
                elif item.x + item.width > desk_rect.right: #right side
                    item.x = desk_rect.right - item.width; item.vx = 0
                if item.y < desk_rect.top: #top side
                    item.y = desk_rect.top; item.vy = 0
                elif item.y + item.height > desk_rect.bottom: # bot side
                    item.y = desk_rect.bottom - item.height; item.vy = 0
                # update the position after reach the desk's side
                item.set_position(item.x, item.y)

        # collision
        push_strength = 0.3
        for i, item_a in enumerate(self.desk_items):
            for item_b in self.desk_items[i+1:]:
                if item_a.is_selected or item_b.is_selected: continue
                # if one of them is selected then continue
                # inflate: offset the size of the rect
                rect_a = item_a.get_rect().inflate(-5, -5)
                rect_b = item_b.get_rect().inflate(-5, -5)
                # prevent over conflict

                if rect_a.colliderect(rect_b):
                    # if a and b collide
                    center_a = pygame.math.Vector2(rect_a.center)
                    center_b = pygame.math.Vector2(rect_b.center)
                    diff = center_a - center_b
                    # built-in function in pygame, for measure the distance
                    dist = diff.length()
                    if dist == 0:
                        force = pygame.math.Vector2(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
                    else:
                        force = diff.normalize()

                    push_force = force * push_strength
                    item_a.vx += push_force.x; item_a.vy += push_force.y
                    item_b.vx -= push_force.x; item_b.vy -= push_force.y
                    spin = random.uniform(-0.05, 0.05)
                    # rotation
                    item_a.va += spin; item_b.va -= spin