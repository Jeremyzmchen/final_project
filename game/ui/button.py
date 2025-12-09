"""
UI Button Component
Supports styles: primary (blue), grey, danger (red), transparent
"""

import pygame
from config.settings import COLOR_WHITE, COLOR_BLACK, COLOR_BLUE, COLOR_RED

class Button:
    """Clickable button with customizable styles and callbacks"""

    def __init__(self, x, y, width, height, text, callback,  
                callback_arg=None, style='primary', font_size=36, image_path=None):
        """
        Initialize a button
        
        Args:
            x, y (int): Top-left position
            width, height (int): Button size
            text (str): Button text
            callback (function): Function called on click (can be None)
            callback_arg (optional): Argument for callback
            style (str): 'primary'/'grey'/'danger'/'transparent'
            font_size (int): Text size
        
        Returns:
            None
        """
        # Position and size
        self.rect = pygame.Rect(x, y, width, height)
        
        # Text and callback
        self.text = text
        self.callback = callback
        self.callback_arg = callback_arg
        
        # Interaction state
        self.is_hovered = False  # True when mouse is over button
        
        # Load font
        try:
            from config.settings import FONT_PATH
            self.font = pygame.font.Font(FONT_PATH, font_size)
        except:
            # If custom font fails, use system default font
            self.font = pygame.font.Font(None, font_size)
        
        # Apply visual style (sets colors and border width)
        self.apply_style(style)

        # load_img
        self.image = None
        if image_path:
            try:
                raw_img = pygame.image.load(image_path)
                self.image = pygame.transform.scale(raw_img, (width, height))
            except Exception as e:
                print(f"Failed to load button image: {image_path}, error: {e}")
    
    
    def apply_style(self, style):
        """
        Sets button colors for different states (normal, hover)
        and border width based on the selected style.
        
        Args:
            style (str): Style name
            ('primary', 'grey', 'danger', 'transparent')
        
        Returns:
            None
        """
        # Default border width
        self.border_width = 2
        
        if style == 'transparent':
            # Transparent style (e.g., menu buttons)
            self.color_normal = (0, 0, 0, 0) # Fully transparent
            self.color_hover = (255, 255, 255, 30)
            self.text_color = COLOR_WHITE
            self.border_width = 0  # No border
        
        elif style == 'grey':
            # Grey style (e.g., reject/cancel buttons)
            self.color_normal = (60, 60, 60)
            self.color_hover = (180, 180, 180)
            self.text_color = COLOR_WHITE
            self.border_width = 0  # No border
        
        elif style == 'danger':
            # Danger style (e.g., delete, call police)
            self.color_normal = COLOR_RED
            self.color_hover = (230, 80, 80)
            self.text_color = COLOR_WHITE
            # Keeps default border_width = 2
        
        else:
            # Primary style (default) (e.g., start game, confirm)
            self.color_normal = COLOR_BLUE
            self.color_hover = (120, 170, 255)
            self.text_color = COLOR_WHITE
            # Keeps default border_width = 2
    
    
    def handle_click(self, mouse_pos):
        """   
        Check if click position is on button and execute callback
        Note: Caller should verify click event occurred before calling this.
        
        Args:
            mouse_pos (tuple): Click position (x, y)
        
        Returns:
            bool: True if position on button, False otherwise
        """
        # Check if mouse position is inside button area
        if self.rect.collidepoint(mouse_pos):
            
            # Execute callback if one was provided
            if self.callback:
                if self.callback_arg is not None:
                    # Call with argument
                    self.callback(self.callback_arg)
                else:
                    # Call without argument
                    self.callback()
            
            return True  # Button was clicked
        
        return False  # Click was outside button
    
    
    def update(self, mouse_pos):
        """
        Update hover state based on mouse position
        
        Args:
            mouse_pos (tuple): Current mouse position (x, y)
        
        Returns:
            None
        """
        # Update hover state: True if mouse is over button, False otherwise
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    
    def render(self, screen):
        """
        Draw button to screen
        
        Args:
            screen (pygame.Surface): Screen to draw on
        
        Returns:
            None
        """
        if self.image:
            screen.blit(self.image, self.rect)
            return

        # Step 1: Determine color based on state
        if self.is_hovered:
            color = self.color_hover
        else:
            color = self.color_normal

        # Step 2: Draw background
        # TODO 把变量 s 改成了 temp_surface
        if len(color) == 4:
            # RGBA: use temp surface for transparency
            temp_surface = pygame.Surface(
                (self.rect.width, self.rect.height), 
                pygame.SRCALPHA
            )
            pygame.draw.rect(
                temp_surface, 
                color, 
                temp_surface.get_rect(), 
                border_radius=8
            )
            screen.blit(temp_surface, self.rect.topleft)
        else:
            # RGB: draw directly
            pygame.draw.rect(screen, color, self.rect, border_radius=8)

        # Step 3: Draw border
        if self.border_width > 0:
            pygame.draw.rect(
                screen, 
                COLOR_WHITE, 
                self.rect, 
                self.border_width, 
                border_radius=8
            )

        # Step 4: Draw text (centered)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
