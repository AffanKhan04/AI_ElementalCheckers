import pygame
from .constants import WHITE, SQUARE_SIZE, GREY, CROWN, FIRE, WATER, AIR, EARTH

class Piece:
    PADDING = 15
    OUTLINE = 2

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        
        # Elemental power tracking
        self.element_power = None
        self.power_used = False
        
        self.calc_pos()

    def move(self, row, col):
        """Updates the piece's position"""
        self.row = row
        self.col = col
        self.calc_pos()

    def calc_pos(self):
        """Calculates the pixel position based on row and column"""
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def make_king(self):
        """Promotes piece to king"""
        self.king = True
        self.power_used = True

    def draw(self, win):
        """Draws the piece on the window"""
        radius = SQUARE_SIZE // 2 - self.PADDING
        pygame.draw.circle(win, GREY, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        
        # Draw king crown if applicable
        if self.king:
            win.blit(CROWN, (self.x - CROWN.get_width() // 2, self.y - CROWN.get_height() // 2))
        
        # Draw elemental icon if applicable
        if self.element_power and not self.power_used:
            icon = None
            if self.element_power == 'fire':
                icon = FIRE
            elif self.element_power == 'water':
                icon = WATER
            elif self.element_power == 'air':
                icon = AIR
            elif self.element_power == 'earth':
                icon = EARTH
            
            if icon:
                # Position the icon in the bottom right of the piece
                icon_pos = (self.x + radius//2, self.y + radius//2)
                win.blit(icon, (icon_pos[0] - icon.get_width()//2, icon_pos[1] - icon.get_height()//2))

    def set_element(self, element):
        """Set the elemental power for this piece"""
        self.element_power = element
        
    def use_power(self):
        """Mark the power as used"""
        self.power_used = True
        
    def can_use_power(self):
        """Check if the power can be used"""
        return self.element_power is not None and not self.power_used
        
    def __repr__(self):
        """String representation of the piece"""
        return str(self.color)