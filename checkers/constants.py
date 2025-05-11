import pygame

WIDTH = 620
BOARD_HEIGHT = 620
INFO_HEIGHT = 80
HEIGHT = BOARD_HEIGHT + INFO_HEIGHT

ROWS, COLS = 8, 8
SQUARE_SIZE = BOARD_HEIGHT//COLS

# rgb
CREAM = (220, 206, 160)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREY = (128,128,128)
LIGHT_GREY = (220, 220, 220)

FIRE_COLOR = (255, 69, 0)
WATER_COLOR = (0, 119, 190)
AIR_COLOR = (135, 206, 235)
EARTH_COLOR = (34, 139, 34)

CROWN = pygame.transform.scale(pygame.image.load('assets/crown.png'), (44, 25))
FIRE = pygame.transform.scale(pygame.image.load('assets/fire.png'), (44, 25))
WATER = pygame.transform.scale(pygame.image.load('assets/water.png'), (44, 25))
AIR = pygame.transform.scale(pygame.image.load('assets/air.png'), (44, 25))
EARTH = pygame.transform.scale(pygame.image.load('assets/earth.png'), (44, 25))

ELEMENTS = ['fire', 'water', 'air', 'earth']
