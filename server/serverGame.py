import pygame
import queue 
from serverCommunication import *
import sys
from abc import ABC, abstractmethod
import time
import os

class BaseServerGame(ABC):
    def __init__(self, width, height, host, port, dummy_server=False, flags=None):
        os.putenv('SDL_FBDEV','/dev/fb0')
        pygame.init()
        self.host = host
        self.port = port
        self.dummy_server = dummy_server
        # Constants
        self.WIDTH, self.HEIGHT = width, height

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.ORANGE = (255, 165, 0)
        self.YELLOW = (255, 255, 0)

        # Create the screen
        if flags is not None:
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), flags)
        else:
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
       
        # event queue for custom events
        self.event_queue = queue.Queue()
        
        # level information
        self.level = 0

        # points information
        self.points = 0

        self.lives = 0

        # store start time for json data
        self.start_time = 0

        # store json data
        self.game_data = None

    def connect_client(self):

        self.server = ServerThread(host=self.host, port=self.port, app=self, dummy_server=self.dummy_server)

        self.server.start()
        if self.dummy_server:
            self.event_queue.put({"type": NetworkEvents.EVENT_INITIALIZE_GAME, "message": {"address": '', "message": 'Client,INITIALIZE_GAME,20'}})
            self.event_queue.put({"type": NetworkEvents.EVENT_START, "message": {"address":'', "message": 'Client,START_GAME\n'}})

    def commonEvents(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif event.type == NetworkEvents.EVENT_START:
            self.start_game = True
            # set level etc. 
            print("Game is started")
            self.start_time = time.time()
        elif event.type == NetworkEvents.EVENT_INITIALIZE_GAME:
            # find game mode 
            print("Game is initializing")
            message = event.dict['message']['message']
            fullCommand = message.split(',')
            self.level = int(fullCommand[2])
            self.read_game_file()
            self.server.send_ack()
        elif event.type == NetworkEvents.EVENT_END_GAME:
            self.start_game = False
            print("Game has ended")
            self.reset_game()
        else:
            return False
        
        return True
    
    def extractCustomEvents(self):
        while not self.event_queue.empty():
            queued_event = self.event_queue.get()
            pygame.event.post(pygame.event.Event(queued_event['type'], message=queued_event['message']))

    @abstractmethod
    def read_game_file(self):
        pass

    @abstractmethod
    def reset_game(self):
        pass

    @abstractmethod
    def run(self):
        pass
