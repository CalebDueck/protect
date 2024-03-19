import pygame
import sys
import csv
import time
from datetime import datetime

from backwall_single_strip import LEDBackwall_single
from color_helpers import c
import time

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1920, 1080
flags = pygame.DOUBLEBUF

current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

led = LEDBackwall_single(13)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
pygame.display.set_caption("Grid Clicker")
led.turn_off_all()
led.show()

rectangles = []
GRIDS_WIDTH = 10
RECT_WIDTH = WIDTH // GRIDS_WIDTH

GRIDS_HEIGHT = 6
RECT_HEIGHT = HEIGHT // GRIDS_HEIGHT
for y in range(0, HEIGHT, RECT_HEIGHT):
    for x in range(0, WIDTH, RECT_WIDTH):            
        rect = pygame.Rect(x, y, RECT_WIDTH, RECT_HEIGHT)
        rectangles.append([rect, False, WHITE, True, 0]) # rect, clicked, color, update, last_time

# Function to write event data to a CSV file
def write_to_csv(x, y, led_num, on, timestamp):
    filename = f"accuracytest_{current_datetime}.csv"
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['x', 'y','led_num', 'on','timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writerow({'x': x, 'y': y, 'led_num':led_num, 'on':on,'timestamp': timestamp})

def convert_color_to_LED_color(color):
        led_color = None
        if color == WHITE:
            led_color = c.white
        elif color == RED:
            led_color = c.red

        return led_color

def is_inside_rect(pos, rect):
    return rect.collidepoint(pos)

def draw_grid():

    update = False
    for index, rect in enumerate(rectangles):
        # pygame.draw.rect(screen, rect[2], rect[0])
        if rect[3]:
            update = True
            if rect[2] != WHITE:
                led.set_color(index, convert_color_to_LED_color(rect[2]),0)
                # print("Setting Color of " + str(index) + "to " + str(rect[2]))
            else:
                led.turn_off_segment(index)
            
            rect[3] = False
    if update:
        led.show()

# Main game loop
running = True
active_fingers = set()
event_happened = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.FINGERDOWN:
            event_happened=True
            x, y = event.x*WIDTH, event.y*HEIGHT

            for index,rect in enumerate(rectangles):
                if is_inside_rect((event.x * WIDTH,event.y * HEIGHT), rect[0]) and time.time() - rect[4] > 0:                           
                    rect[1] = not rect[1]
                    rect[2] = RED if rect[1] else WHITE
                    rect[3] = True
                    rect[4] = time.time()
                    write_to_csv(x, y, index, rect[4], rect[1])

        # #     print(f"Finger down at {x} and {y}")
        # elif event.type == pygame.MOUSEMOTION:
        #     event_happened=True
        #     x, y = pygame.mouse.get_pos()

        #     for index,rect in enumerate(rectangles):
        #         if is_inside_rect((x,y), rect[0]) and time.time() - rect[4] > 0:                           
        #             rect[1] = not rect[1]
        #             rect[2] = RED if rect[1] else WHITE
        #             rect[3] = True
        #             rect[4] = time.time()
        #             write_to_csv(x, y, index, rect[4], rect[1])
        #     print(f"Mouse down at {x} and {y}")

    if event_happened:
        event_happened=False
        # Clear the screen
        screen.fill(BLACK)

        # Draw the grid
        draw_grid()


        pygame.display.flip()

# Quit pygame
pygame.quit()
sys.exit()
