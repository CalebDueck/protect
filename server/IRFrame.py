import pygame
import sys
from serverCommunication import *
import queue
import enum
import json
import time 
from serverGame import *
# from lib.backwall import LEDBackwall
from lib.backwall_single_strip import LEDBackwall_single
from lib.color_helpers import c

class BackWallMainApp(BaseServerGame):
    def __init__(self, width, height, host, port, dummy_server=False):
        super().__init__(width, height, host, port, dummy_server=dummy_server)

        # set up rectangles for back wall
        self.rectangles = []
        self.GRIDS_WIDTH = 10
        self.RECT_WIDTH = self.WIDTH // self.GRIDS_WIDTH

        self.GRIDS_HEIGHT = 6
        self.RECT_HEIGHT = self.HEIGHT // self.GRIDS_HEIGHT
        for y in range(0, self.HEIGHT, self.RECT_HEIGHT):
            for x in range(0, self.WIDTH, self.RECT_WIDTH):            
                rect = pygame.Rect(x, y, self.RECT_WIDTH, self.RECT_HEIGHT)
                self.rectangles.append([rect, False, self.WHITE, 0, False, True, 0, 0, 0]) # rectangle, clicked, colour, points when clicked, successfully completed, update colour, prev update color, start_time, end_time

        self.impreciseHitBoxes = []

        self.LED_control = LEDBackwall_single(13)

        self.debouncing = 0

    def reset_game(self):
        for rect in self.rectangles:
            rect[1] = False
            rect[2] = self.WHITE
            rect[3] = 0
            rect[4] = False
            rect[5] = True
            rect[6] = 0
            rect[7] = 0
            rect[8] = 0
        self.start_game = False

    def in_quadrant(self, index):
        if  index >= 0 and index <= 4 or index >= 10 and index <= 14 or index >= 20 and index <= 24:
            return 1
        elif index >= 5 and index <= 9 or index >= 15 and index <= 29 or index >= 25 and index <= 30:
            return 2
        elif index >= 30 and index <= 34 or index >= 40 and index <= 34 or index >= 50 and index <= 54:
            return 3
        else:
            return 4


    def is_inside_rect(self, pos, rect):
        return rect.collidepoint(pos)

    # Function to draw the grid of rectangles
    def draw_grid(self):
        update = False
        #self.LED_control.turn_off_all()
        for index, rect in enumerate(self.rectangles):
            pygame.draw.rect(self.screen, rect[2], rect[0])
            if rect[5]:
                led_color = self.convert_color_to_LED_color(rect[2])
                if led_color:  
                    update = True
                    if led_color == c.white:
                        self.LED_control.turn_off_segment(index)
                    else:
                        self.LED_control.set_color(index, led_color, 0)
                print("Setting Color of " + str(index) + "to " + str(rect[2]))
                rect[5] = False
        if update:
            self.LED_control.show()

    def run(self):
        self.start_game = False

        # Main game loop
        while True:
            for event in pygame.event.get():
                
                if self.commonEvents(event):
                    continue
                elif event.type == pygame.FINGERDOWN or event.type == pygame.FINGERMOTION:
                    if self.start_game != True:
                        continue
                    # Check if the mouse click is inside any rectangle
                    for index, rect in enumerate(self.rectangles):
                        if self.is_inside_rect((event.x * self.WIDTH,event.y * self.HEIGHT), rect[0]) and time.time() - rect[6] > self.debouncing:                           

                            if (rect[3] > 0 and rect[4] == False):
                                rect[4] = True
                                self.points = int(round(rect[3] * ( 1 + abs(( rect[8] - (time.time()-self.start_time) )/ (rect[8] - rect[7])))))
                                rect[3] = 0
                                rect[2] = self.GREEN
                                rect[5] = True
                                rect[6] = time.time()
                            elif (rect[3] < 0 and rect[4] == False):
                                rect[4] = True
                                self.lives = -1
                                rect[3] = 0
                                rect[2] = self.RED
                                rect[5] = True
                                rect[6] = time.time()
                            else:
                                if rect[2] != self.GREEN:                                    
                                    matching_entry = next((entry for entry in self.impreciseHitBoxes if entry[1] == 0), None)
                                    if matching_entry is not None:
                                        if matching_entry[3] is None or self.in_quadrant(index) == matching_entry[3]:
                                            self.lives = -1
                                            matching_entry[1] = 1
                                            rect[2] = self.RED
                                            rect[5] = True
                                            rect[6] = time.time()
                                            matching_entry[2] = rect

                            
                            self.server.point_update(points=self.points,lives=self.lives)
                            self.points = 0
                            self.lives = 0
                            print("Sending Client Update")
                            break


                

            self.extractCustomEvents()

            # Clear the screen
            self.screen.fill(self.WHITE)
            
            # update rectangle information
            self.update_rects()
            # Draw the grid
            self.draw_grid()

            # Update the display
            pygame.display.flip()

            # Control the frames per second
            pygame.time.Clock().tick(30)

    def read_game_file(self):
        with open('cdueck_backWallClickGame.json', 'r') as file:
            self.game_data = json.load(file)   

    def update_rects(self):
        if self.game_data == None:
            return
        
        if self.start_game == False:
            return
        
        levels = self.game_data.get("levels", [])
        target_level = next((level for level in levels if level["level_id"] == self.level), None)
        commands = target_level['commands']
        time_since_start = time.time() - self.start_time

        for command in commands:
            time_start = command['time_start']

            if time_since_start < time_start:
                 continue          
            command_id = command['command_id']
            command_name = command['command_name']
            location_x = command['location_x']
            location_y = command['location_y']
            time_end = command['time_end']
            points = command['points']
            
            if command_name == "Imprecise Hit Box":
                matching_entry = next((entry for entry in self.impreciseHitBoxes if entry[0] == command_id), None)
                if time_since_start > time_end and not 'completed' in command:                  

                    if matching_entry is not None:                      
                        if matching_entry[1] == 0:
                            self.points = points
                            self.server.point_update(self.points,self.lives)

                            updated_list = [entry for entry in self.impreciseHitBoxes if entry[0] != command_id]
                            self.impreciseHitBoxes = updated_list
                        command['completed'] = True
                        if not matching_entry[2] is None:
                            matching_entry[2][2] = self.WHITE
                            matching_entry[2][5] = True

                elif not 'completed' in command:
                    if matching_entry is None:
                        quadrant = command.get('quadrant')
                        self.impreciseHitBoxes.append([command_id,0, None, quadrant])
                        print("Command ID: " + str(command_id) + " ball has been shot")
                    
            else:
                # Use list comprehension to find the entry that matches the specified location_x and location_y
                matching_entry = next((rect for rect in self.rectangles if rect[0].left == location_x*self.RECT_WIDTH and rect[0].top == location_y*self.RECT_HEIGHT), None)
                if matching_entry == None:
                    print("Cant find rectangle")
                    return
                if time_since_start > time_end and not 'completed' in command:
                    # wasn't clicked in time
                    if matching_entry[4] == False and matching_entry[3] > 0:
                        self.lives = -1
                        self.server.point_update(self.points,self.lives)
                        self.lives = 0
                        matching_entry[1] = False
                        matching_entry[2] = self.WHITE
                        matching_entry[3] = 0
                        matching_entry[4] = False
                        matching_entry[5] = True
                    elif matching_entry[4] == False and matching_entry[3] < 0:
                        self.points = abs(matching_entry[3])
                        self.server.point_update(self.points,self.lives)
                        self.points = 0
                        matching_entry[1] = False
                        matching_entry[2] = self.WHITE
                        matching_entry[3] = 0
                        matching_entry[4] = False
                        matching_entry[5] = True
                    else:
                        # reset the rectangle
                        if matching_entry[4] == True:
                            matching_entry[1] = False
                            matching_entry[2] = self.WHITE
                            matching_entry[3] = 0
                            matching_entry[4] = False
                            matching_entry[5] = True
                    
                    command['completed'] = True
        
                elif not 'completed' in command:
                    if matching_entry[4] != True:
                        if (matching_entry[3] > 0):
                            matching_entry[5] = matching_entry[2] != self.BLUE
                            matching_entry[2] = self.BLUE
                        elif matching_entry[3] < 0:
                            matching_entry[5] = matching_entry[2] != self.RED
                            matching_entry[2] = self.RED

                        matching_entry[3] = points
                        matching_entry[7] = time_start
                        matching_entry[8] = time_end
                    # make flashing red 
                    if matching_entry[4] == True and matching_entry[3] < 0:
                        matching_entry[2] = self.WHITE if matching_entry[2] == self.RED else self.RED
                        matching_entry[5] = True
            # Last Command       
            if command == commands[-1]:
                if time_since_start > time_end + 5:
                    self.server.send_end()
                    self.reset_game()


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
        elif color == self.YELLOW:
            led_color = c.yellow
        return led_color


           

if __name__ == "__main__":
    backWallMainApp = BackWallMainApp(1920,1080,'192.168.1.141',12345, True)
    backWallMainApp.connect_client()
    backWallMainApp.run()