import pygame
import sys
from backwall import LEDBackwall
from color_helpers import c

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1920, 1080
GRID_SIZE = 10
GRID_WIDTH = 10
GRID_HEIGHT = 6
RECT_SIZE = WIDTH // GRID_WIDTH
RECT_HEIGHT = HEIGHT // GRID_HEIGHT

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

led = LEDBackwall(13,18)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Grid Clicker")

# Create a 2D array to represent the grid
grid = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
grid_update = [[True for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
def convert_color_to_LED_color(self,color):
        led_color = None
        if color == self.WHITE:
            led_color = c.white
        elif color == self.RED:
            led_color = c.red
        elif color == self.BLUE:
            led_color = c.blue
        elif color == self.ORANGE:
            led_color = c.orange
        elif color == self.GREEN:
            led_color = c.green
        return led_color

def draw_grid():
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            color = WHITE if not grid[row][col] else RED
            if grid_update[row][col]:
                if color != WHITE:
                    led.set_color(row*GRID_WIDTH+col,c.red, 0)
                else:
                    led.turn_off_segment(row*GRID_WIDTH+col)
                grid_update[row][col] = False
            pygame.draw.rect(screen, color, (col * RECT_SIZE, row * RECT_HEIGHT, RECT_SIZE, RECT_HEIGHT))

# Main game loop
running = True
active_fingers = set()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos[0], event.pos[1]
            col = int(x // RECT_SIZE)
            row = int(y // RECT_HEIGHT)
            grid[row][col] = not grid[row][col]
            grid_update[row][col] = True
        elif event.type == pygame.FINGERDOWN:
            x, y = event.x, event.y
            col = int(x // RECT_SIZE)
            row = int(y // RECT_HEIGHT)
            grid[row][col] = not grid[row][col]
            grid_update[row][col] = True

    # Clear the screen
    screen.fill(BLACK)

    # Draw the grid
    draw_grid()

    # # Highlight cells for active touches
    # for finger_id in active_fingers:
    #     x, y = pygame.mouse.get_pos()
    #     col = x // RECT_SIZE
    #     row = y // RECT_SIZE
    #     pygame.draw.rect(screen, GREEN, (col * RECT_SIZE, row * RECT_SIZE, RECT_SIZE, RECT_SIZE), 3)

    # Update the display
    pygame.display.flip()

# Quit pygame
pygame.quit()
sys.exit()
