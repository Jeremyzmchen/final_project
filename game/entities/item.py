"""
物品实体 - 代表失物招领处的各种物品 (沉重手感版)
"""

import pygame
import random
from config.settings import ITEM_SIZE, ITEM_DESCRIPTIONS, ASSETS, COLOR_WHITE

class Item:
    """物品类"""

    def __init__(self, item_type):
        # property of each item
        ### in this part, mainly get the information of the input and seperate them into different variables
        # input itemtype
        self.item_type = item_type
        self.data = ITEM_DESCRIPTIONS.get(item_type, {})

        # according to the item type(input), get the information of that item in description
        self.name = self.data.get('name', 'Unknown Item')
        self.keywords = self.data.get('keywords', [])
        self.category = self.data.get('category', 'unknown')
        target_size = self.data.get('size', ITEM_SIZE)
        # get the size of the item
        self.width = target_size[0]
        self.height = target_size[1]
        # original position
        self.x = 0
        self.y = 0

        # angular velocity, rotation part
        self.angle = random.uniform(-5, 5) # original rotation degree
        # initial velocity on x and y axis
        # vx, vy are only about the friction, collision
        self.vx = 0.0
        self.vy = 0.0
        # angular velocity for rotation
        self.va = 0.0

        # friction: make sure that the object will stop after collision
        self.friction = 0.6
        self.mass = 1.0

        # set up space for image, original image, and rect object in pygame
        self.image = None
        self.original_image = None
        self.rect = None

        self._load_image()
        # load image function: load the correlated image according to the item type

        # item status
        self.is_selected = False
        self.in_storage = False

        # conveyor status(connect or not connect with conveyor)
        self.on_conveyor = False
        self.conveyor_progress = 0
        self.conveyor_start_offset = 0
        self.conveyor_vertical_offset = 0
        self.item_index = 0
        self.batch_id = 0

        self.rotate(0)

    def _load_image(self):
        try:
            image_key = f'item_{self.item_type}'
            # if image_key in assets, then use the image
            # else raise not found
            if image_key in ASSETS:
                image_path = ASSETS[image_key]
                self.original_image = pygame.image.load(image_path)
                # transform the input image's size, following the size of width and height
                self.original_image = pygame.transform.scale(self.original_image, (self.width, self.height))
            else:
                raise Exception("Image key not found")
        except Exception as e:
            # if previous progress not working, then create a label for that
            self.original_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.original_image.fill((100, 100, 200))
            font = pygame.font.Font(None, 16)
            text = font.render(self.item_type[:8], True, COLOR_WHITE)
            text_rect = text.get_rect(center=(self.width//2, self.height//2))
            self.original_image.blit(text, text_rect)

        self.image = self.original_image.copy()
        # rect: rectangle object
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def set_position(self, x, y):
        # set the position on top-left for rect
        self.x = x
        self.y = y
        if self.rect:
            self.rect.topleft = (int(x), int(y))

    def get_position(self):
        # get the position
        return (self.x, self.y)

    def get_rect(self):
        if self.rect:
            return self.rect
        # telling pygame the size of the rectangle, position(x, y), width and height
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def rotate(self, angle_change=0):
        # change the angle based on existed angle
        self.angle = (self.angle + angle_change) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)

        if self.rect:
            # change the value of rect
            old_center = self.rect.center
            # center not in get_rect function but as long as it is rect it has rect
            self.rect = self.image.get_rect(center=old_center)
            self.x = self.rect.x
            self.y = self.rect.y
            self.width = self.rect.width
            self.height = self.rect.height
        else:
            self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def update_physics(self, dt):
        # update the physics status
        if self.is_selected or self.on_conveyor or self.in_storage:
            # selected: vx, vy, va should be 0 because player control the item
            # 
            self.vx = 0
            self.vy = 0
            self.va = 0
            return

        # prevent subtle movement (move only when velocity is larger than certain value)
        if abs(self.vx) > 0.1 or abs(self.vy) > 0.1:
            self.x += self.vx * dt * 60
            self.y += self.vy * dt * 60
            self.rect.topleft = (int(self.x), int(self.y))

            # decrease the velocity caused by the friction
            self.vx *= self.friction
            self.vy *= self.friction
        else:
            # not moving
            self.vx = 0
            self.vy = 0

        # decrease angular velocity (friction)
        if abs(self.va) > 0.1:
            self.rotate(self.va * dt * 60)
            self.va *= self.friction
        else:
            self.va = 0

    '''
    pause_flag meaning?
    pause means conveyor movement stops
    True: not connect with conveyor
    False: still on conveyor
    '''
    def update_conveyor_movement(self, dt, speed, pause_flag=None):
        # conveyor will move from up to down
        # this function will return True if the item not affected by conveyor False otherwise
        if not self.on_conveyor: return True  # item is picked, return True
        # pause_flag means when conveyor paused
        if pause_flag and pause_flag.get('paused', False): return False

        # movement on y direction
        self.y += speed * dt

        # update the rect position
        if self.rect:
            self.rect.topleft = (int(self.x), int(self.y))

        # return True if the item is out of screen, return True
        if self.y > 950:
            return True

        return False

    def contains_point(self, point):
        # whether the point is in size of rectangle
        if self.rect:
            # function in rect in pygame will return True if point inside else False
            return self.rect.collidepoint(point)
        return self.get_rect().collidepoint(point)

    '''
    keywords from where?
    '''
    def matches_keywords(self, keywords):
        # the percentage of matching
        if not keywords: return 0
        matches = sum(1 for kw in keywords if kw in self.keywords)
        return matches / len(keywords)


    def render(self, screen):
        if self.image:
            render_rect = self.rect if self.rect else pygame.Rect(self.x, self.y, self.width, self.height)
            
            screen.blit(self.image, render_rect)

        if self.is_selected:
            sel_rect = self.rect if self.rect else pygame.Rect(self.x, self.y, self.width, self.height)
            pygame.draw.rect(screen, (255, 255, 0), sel_rect, 3)

    def __repr__(self):
        return f"Item({self.item_type})"