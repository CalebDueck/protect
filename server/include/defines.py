import enum
import pygame

class NetworkEvents(enum.IntEnum):
    EVENT_START = pygame.USEREVENT + 1
    EVENT_INITIALIZE_GAME = pygame.USEREVENT + 2
    EVENT_POINT_UPDATE = pygame.USEREVENT + 3
    EVENT_LIFE_UPDATE = pygame.USEREVENT + 4
    EVENT_END_GAME = pygame.USEREVENT + 5
    EVENT_ACK = pygame.USEREVENT + 6
    
class ActionEvents(enum.IntEnum):
    BUTTON_CLICK_SIDEWALL = pygame.USEREVENT + 7

# class NetworkEvents(enum.IntEnum):
#     EVENT_START = 1
#     EVENT_INITIALIZE_GAME = 2
#     EVENT_POINT_UPDATE = 3
#     EVENT_LIFE_UPDATE = 4
#     EVENT_END_GAME = 5
#     EVENT_ACK = 6