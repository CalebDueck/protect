import pygame
import sys
from backwall_single_strip import LEDBackwall_single
from color_helpers import c
import time

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

led = LEDBackwall_single(13)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Grid Clicker")

# Create a 2D array to represent the grid
grid = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
grid_update = [[True for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
prev_time = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def convert_color_to_LED_color(color):
        led_color = None
        if color == WHITE:
            led_color = c.white
        elif color == RED:
            led_color = c.red

        return led_color

def draw_grid():
    update = False
    #led.set_color_all(c.white)
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            color = WHITE if not grid[row][col] else RED
            if grid_update[row][col]:
                update = True
                if color != WHITE:
                    led.set_color(row*GRID_WIDTH+col,convert_color_to_LED_color(color), 0)
                else:
                    led.turn_off_segment(row*GRID_WIDTH+col)
                grid_update[row][col] = False
                print("Updating LED number: " + str(row*GRID_WIDTH+col))
            pygame.draw.rect(screen, color, (col * RECT_SIZE, row * RECT_HEIGHT, RECT_SIZE, RECT_HEIGHT))
    if update:
        led.show()

# Main game loop
running = True
active_fingers = set()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.FINGERDOWN:
            x, y = event.x*WIDTH, event.y*HEIGHT
            col = int(x // RECT_SIZE)
            row = int(y // RECT_HEIGHT)
            if time.time() - prev_time[row][col] > 0.25:
                grid[row][col] = not grid[row][col]
                grid_update[row][col] = True
                prev_time[row][col] = time.time()

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
