from client import *
from include.utilities import *
import pygame
import sys
import enum
from sshclient import run_powershell_script

class MainGameStates(enum.IntEnum):
    START_SCREEN = 0
    LEVEL_SELECT = 1
    LEVEL_1 = 2
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
        self.font = pygame.font.Font(None, 36)
        self.countdownFont = pygame.font.Font(None, 100)

        # Set up colors
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.green = (0,255,0)

        HEART_IMAGE_PATH = 'heart.png'
        self.heart_image = pygame.image.load(HEART_IMAGE_PATH)
        self.heart_size = (120,120)
        self.heart_image = pygame.transform.scale(self.heart_image, self.heart_size)  # Adjust the size if needed

        self.transition_timer = 0
        self.transition_time = 500
        # Set up buttons
        self.start_button = pygame.Rect(300, 200, 200, 50)
        self.level1_button = pygame.Rect(300, 300, 200, 50)
        self.level2_button = pygame.Rect(300, 400, 200, 50)
        self.ready_button = pygame.Rect(300, 500, 200, 50)
        self.play_again_button = pygame.Rect(300, 600, 200, 50)

        # Set up state
        self.state = MainGameStates.START_SCREEN

        # Set up game variables
        self.points = 0
        self.lives = 5


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
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check button clicks
                if self.start_button.collidepoint(event.pos):
                    self.state = MainGameStates.LEVEL_SELECT
                elif self.level1_button.collidepoint(event.pos):
                    print("Starting Level 1")
                    self.state = MainGameStates.LEVEL_1
                    self.sendMessageToAllServers("Client,INITIALIZE_GAME,1\n")
                    # Add your code to start level 1 here
                elif self.level2_button.collidepoint(event.pos):
                    print("Starting Level 2")
                    self.state = MainGameStates.LEVEL_2
                    self.sendMessageToAllServers("Client,INITIALIZE_GAME,2\n")
                    # Add your code to start level 2 here
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
                    self.state = MainGameStates.END_GAME      


        while not self.event_queue.empty():
            queued_event = self.event_queue.get()
            pygame.event.post(pygame.event.Event(queued_event['type'], message=queued_event['message']))

    def draw(self):
        self.screen.fill(self.white)

        if self.state == MainGameStates.START_SCREEN:
            pygame.draw.rect(self.screen, self.black, self.start_button)
            text = self.font.render("Start", True, self.white)
            self.screen.blit(text, (self.start_button.x + 70, self.start_button.y + 15))

        elif self.state == MainGameStates.LEVEL_SELECT:
            pygame.draw.rect(self.screen, self.black, self.level1_button)
            text = self.font.render("Level 1", True, self.white)
            self.screen.blit(text, (self.level1_button.x + 60, self.level1_button.y + 15))

            pygame.draw.rect(self.screen, self.black, self.level2_button)
            text = self.font.render("Level 2", True, self.white)
            self.screen.blit(text, (self.level2_button.x + 60, self.level2_button.y + 15))

            # Display points and lives
            points_text = self.font.render(f"Points: {self.points}", True, self.black)
            self.screen.blit(points_text, (10, 10))

            lives_text = self.font.render(f"Lives: {self.lives}", True, self.black)
            self.screen.blit(lives_text, (10, 50))

        elif self.state == MainGameStates.LEVEL_1 or self.state == MainGameStates.LEVEL_2 or self.state == MainGameStates.ACTIVE_GAME:
            # Display points and lives
            points_text = self.font.render(f"Points: {self.points}", True, self.black)
            text_rect = points_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(points_text, text_rect)

            lives_text = self.font.render(f"Lives: {self.lives}", True, self.black)
            text_rect = lives_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 30))
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
            self.screen.blit(text, (self.ready_button.x + 60, self.ready_button.y + 15))

        elif self.state == MainGameStates.END_GAME:
            # Display points
            points_text = self.font.render(f"Points: {self.points}", True, self.black)
            text_rect = points_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(points_text, text_rect)

            pygame.draw.rect(self.screen, self.black, self.play_again_button)
            text = self.font.render("Play Again?", True, self.white)
            self.screen.blit(text, (self.play_again_button.x + 40, self.play_again_button.y + 15))

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
        font = pygame.font.Font(None, 36)
        text = font.render("You lost a life!", True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 4))
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(transition_time)
        if self.lives == 0:
            self.state = MainGameStates.END_GAME

    def draw_hearts(self):
        heart_x = (self.screen_width - self.lives * self.heart_size[0]) // 2
        heart_y = 50  # Adjust the vertical position near the top
        for i in range(self.lives):
            self.screen.blit(self.heart_image, (heart_x + i * self.heart_size[0], heart_y))

if __name__ == "__main__":

    servers = [('activateMotor.local',12345)]
    for ipAddress, port in servers:
        run_powershell_script('activateMotor')
    start_screen = MainGame(800, 800, servers)
    start_screen.run()

