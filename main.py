from client import *
from include.utilities import *
import pygame

import sys
import enum
from sshclient import run_powershell_script
import os as os
import json
class MainGameStates(enum.IntEnum):
    START_SCREEN = 0
    LEVEL_SELECT = 1
    LEVEL_SELECTED = 2
    LEVEL_2 = 3
    RESET_GAME = 4
    READY_WAIT = 5
    ACTIVE_GAME = 6
    END_GAME = 7


class MainGame:
    def __init__(self, screen_width, screen_height, serversAddresses):
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Pygame Start Screen")

        self.countdownFont = pygame.font.Font(None, 300)

        # Set up colors
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.green = (0,255,0)

        HEART_IMAGE_PATH = 'heart.png'
        self.heart_image = pygame.image.load(HEART_IMAGE_PATH)
        self.heart_size = (300,300)
        self.heart_image = pygame.transform.scale(self.heart_image, self.heart_size)  # Adjust the size if needed

        self.transition_timer = 0
        self.transition_time = 500
        # Set up buttons
        self.start_button = pygame.Rect(0, 0, 400, 100)
        self.start_button.center = (self.screen_width//2, 200)
        self.ready_button = pygame.Rect(0, 0, 400, 100)
        self.ready_button.center = (self.screen_width//2, 500)

        self.play_again_button = pygame.Rect(0, 0, 400, 100)
        self.play_again_button.center = (self.screen_width//2, 800)

        self.font_size = 80
        self.font = pygame.font.SysFont(None, self.font_size)

        # Set up state

        self.state = MainGameStates.START_SCREEN

        # Set up game variables
        self.points = 0
        self.lives = 5

        self.input_active = True
        self.name = ""

        self.level_input_active = False
        self.level = ""

        self.serversAddresses = serversAddresses
        self.servers = []
        self.serverACK = []
        self.end_game_ack = []

        self.event_queue = queue.Queue()

        self.connectServers()
    
    def connectServers(self):
        for address,port in self.serversAddresses:
            server = ClientThread(address, port, self)
            server.connect()
            print("Connecting to Server: " + address)
            self.servers.append(server)
            self.serverACK.append(False)      
            self.end_game_ack.append(False)           

    def sendMessageToAllServers(self, message):
        for server in self.servers:
            server.send_message(message)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if self.input_active:
                    if event.key == pygame.K_RETURN:
                        self.input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.name = self.name[:-1]
                    else:
                        self.name += event.unicode
                if self.level_input_active:
                    if event.key == pygame.K_RETURN:
                        try:
                            level_chosen = int(self.level)
                            if level_chosen > 0 and level_chosen <= 10:
                                self.state = MainGameStates.LEVEL_SELECTED
                                self.level_input_active = False
                                message = "Client,INITIALIZE_GAME," + str(level_chosen) + "\n"
                                print(message)
                                self.sendMessageToAllServers(message)
                            else:
                                self.level = ""
                        except ValueError:
                            self.level_input_active = True
                    elif event.key == pygame.K_BACKSPACE:
                        self.level = self.level[:-1]
                    else:
                        self.level += event.unicode if event.unicode.isnumeric() else ""
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check button clicks
                if self.start_button.collidepoint(event.pos):
                    self.state = MainGameStates.LEVEL_SELECT
                    self.level_input_active = True
                    self.level = ""
                elif self.ready_button.collidepoint(event.pos):
                    print("Game is Ready")
                    self.countdown(5)
                    self.display_go()
                    self.sendMessageToAllServers("Client,START_GAME\n")
                    self.state = MainGameStates.ACTIVE_GAME
                elif self.play_again_button.collidepoint(event.pos):
                    print("Restart Game")
                    self.state = MainGameStates.START_SCREEN
                    self.points = 0
                    self.lives = 5
                    self.name = ""
                    self.input_active = True
                
            elif event.type == NetworkEvents.EVENT_POINT_UPDATE:
                print("Received Point Update")
                message = event.dict['message']['message']
                fullCommand = message.split(',')
                self.points += int(fullCommand[2])
                self.lives += int(fullCommand[3])

                if self.lives == 0:
                    self.sendMessageToAllServers("Client,END_GAME\n")

                if int(fullCommand[3]) != 0:
                    self.transition_timer = pygame.time.get_ticks()

            elif event.type == NetworkEvents.EVENT_ACK:

                address = event.dict['message']['address']
                print("Received ACK from Server: " + address)
                serverIndex = find_index_by_entry0(self.serversAddresses, address)
                if not serverIndex is None:
                    self.serverACK[serverIndex] = True

                if all(self.serverACK):
                    print("Waiting for Ready Game")
                    self.state = MainGameStates.READY_WAIT      
            elif event.type == NetworkEvents.EVENT_END_GAME:
                address = event.dict['message']['address']
                print("Received End Game from Server: " + address)
                serverIndex = find_index_by_entry0(self.serversAddresses, address)
                if not serverIndex is None:
                    self.end_game_ack[serverIndex] = True

                if all(self.end_game_ack):
                    print("Ending Game")
                    self.end_game_tasks()


        while not self.event_queue.empty():
            queued_event = self.event_queue.get()
            pygame.event.post(pygame.event.Event(queued_event['type'], message=queued_event['message']))

    def draw(self):
        self.screen.fill(self.white)

        if self.state == MainGameStates.START_SCREEN:
            if not self.input_active:
                pygame.draw.rect(self.screen, self.black, self.start_button)
                text = self.font.render("Start", True, self.white)
                text_rect = text.get_rect()
                text_rect.center = self.start_button.center
                self.screen.blit(text, text_rect)

            # Display user input
            input_text = self.font.render("Enter your name: " + self.name, True, self.black)
            input_rect = input_text.get_rect(center=(self.screen_width // 2, self.screen_height // 1.5))
            self.screen.blit(input_text, input_rect)

            pygame.draw.rect(self.screen, self.black, (input_rect.left, input_rect.bottom, input_rect.width, 2))

        elif self.state == MainGameStates.LEVEL_SELECT:

            # Display user input
            input_level_text = self.font.render("Select Level (0-10): " + self.level, True, self.black)
            input_level_rect = input_level_text.get_rect(center=(self.screen_width // 2, self.screen_height // 1.5))
            self.screen.blit(input_level_text, input_level_rect)

            pygame.draw.rect(self.screen, self.black, (input_level_rect.left, input_level_rect.bottom, input_level_rect.width, 2))
            # Display points and lives
            points_text = self.font.render(f"Points: {self.points}", True, self.black)
            self.screen.blit(points_text, (10, 10))

            lives_text = self.font.render(f"Lives: {self.lives}", True, self.black)
            self.screen.blit(lives_text, (10, 100))

        elif self.state == MainGameStates.LEVEL_SELECTED or self.state == MainGameStates.LEVEL_2 or self.state == MainGameStates.ACTIVE_GAME:
            # Display points and lives
            points_text = self.font.render(f"Points: {self.points}", True, self.black)
            text_rect = points_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(points_text, text_rect)

            lives_text = self.font.render(f"Lives: {self.lives}", True, self.black)
            text_rect = lives_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 70))
            self.screen.blit(lives_text, text_rect)
            if self.transition_timer > 0:
                self.show_transition_screen(self.transition_time)
                if pygame.time.get_ticks() - self.transition_timer >= self.transition_time:
                    self.transition_timer = 0
            else:
                self.draw_hearts()

        elif self.state == MainGameStates.READY_WAIT:
            pygame.draw.rect(self.screen, self.black, self.ready_button)
            text = self.font.render("Ready?", True, self.white)
            text_rect = text.get_rect()
            text_rect.center = self.ready_button.center
            self.screen.blit(text, text_rect)

        elif self.state == MainGameStates.END_GAME:
            # Display points
            points_text = self.font.render(f"Points: {self.points}", True, self.black)
            text_rect = points_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(points_text, text_rect)

            pygame.draw.rect(self.screen, self.black, self.play_again_button)
            text = self.font.render("Play Again?", True, self.white)
            text_rect = text.get_rect()
            text_rect.center = self.play_again_button.center
            self.screen.blit(text, text_rect)

        pygame.display.flip()

    def run(self):
        self.running = True
        while self.running:
            self.handle_events()
            self.draw()

    def countdown(self, countdown):
        for i in range(countdown, 0, -1):
            self.screen.fill(self.black)
            text = self.countdownFont.render(str(i), True, self.white)
            text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(text, text_rect)
            pygame.display.flip()
            pygame.time.wait(1000)  # Wait for 1 second

    def display_go(self):
        self.screen.fill(self.green)
        text = self.countdownFont.render("GO", True, self.white)
        text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(1000)  # Wait for 2 seconds

    # Function to display transition screen
    def show_transition_screen(self, transition_time):

        text = self.font.render("You lost a life!", True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 4))
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(transition_time)
        if self.lives == 0:
            self.end_game_tasks()         

    def draw_hearts(self):
        heart_x = (self.screen_width - self.lives * self.heart_size[0]) // 2
        heart_y = 50  # Adjust the vertical position near the top
        for i in range(self.lives):
            self.screen.blit(self.heart_image, (heart_x + i * self.heart_size[0], heart_y))

    def end_game_tasks(self):
        self.state = MainGameStates.END_GAME
        for element in self.end_game_ack:
            element = False
            # Check if the file exists

        cwd = os.getcwd()

        # Create the full path by joining the current working directory with the relative path
        full_path = os.path.join(cwd, 'high_scores.json')

        if not os.path.exists(full_path):
            # If the file doesn't exist, create an empty dictionary
            data = {}
            print("File doesnt exist")
        else:
            # Load existing data from the file if it exists
            with open(full_path, 'r') as file:
                data = json.load(file)

        # Check if the name is already in the data
        if self.name in data:
            # Update the score only if the new score is higher
            if self.points > data[self.name]:
                data[self.name] = self.points
        else:
            # Add the name and score if it doesn't exist in the data
            data[self.name] = self.points

        # Save the updated data back to the file
        with open(full_path, 'w') as file:
            json.dump(data, file)

if __name__ == "__main__":

    servers = [('127.0.0.1',12345)]
    # for ipAddress, port in servers:
    #     run_powershell_script('activateMotor')
    start_screen = MainGame(1920, 1080, servers)
    start_screen.run()

