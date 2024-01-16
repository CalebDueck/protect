import pygame
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 680
GRID_SIZE = 10
RECT_SIZE = WIDTH // GRID_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Grid Clicker")

# Create a 2D array to represent the grid
grid = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

def draw_grid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            color = WHITE if not grid[row][col] else RED
            pygame.draw.rect(screen, color, (col * RECT_SIZE, row * RECT_SIZE, RECT_SIZE, RECT_SIZE))

# Main game loop
running = True
active_fingers = set()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.FINGERDOWN:
            x, y = event.x * WIDTH, event.y * HEIGHT
            col = int(x // RECT_SIZE)
            row = int(y // RECT_SIZE)
            grid[row][col] = not grid[row][col]

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
