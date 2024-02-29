import pygame
import sys
from serverCommunication import *
import queue
import enum
import json
import time 
from serverGame import *

class BackWallMainApp(BaseServerGame):
    def __init__(self, width, height, host, port):
        super().__init__(width, height, host, port)

        # set up rectangles for back wall
        self.rectangles = []
        self.GRIDS_WIDTH = 10
        self.RECT_WIDTH = self.WIDTH // self.GRIDS_WIDTH

        self.GRIDS_HEIGHT = 6
        self.RECT_HEIGHT = self.HEIGHT // self.GRIDS_HEIGHT
        for y in range(0, self.HEIGHT, self.RECT_HEIGHT):
            for x in range(0, self.WIDTH, self.RECT_WIDTH):            
                rect = pygame.Rect(x, y, self.RECT_WIDTH, self.RECT_HEIGHT)
                self.rectangles.append([rect, False, self.WHITE, 0, False]) # rectangle, clicked, colour, points when clicked, successfully completed

        self.impreciseHitBoxes = []

    def reset_game(self):
        for rect in self.rectangles:
            rect[1] = False
            rect[2] = self.WHITE
            rect[3] = 0
            rect[4] = False
        self.start_game = False

    def is_inside_rect(self, pos, rect):
        return rect.collidepoint(pos)

    # Function to draw the grid of rectangles
    def draw_grid(self):
        for rect in self.rectangles:
            pygame.draw.rect(self.screen, rect[2], rect[0])

    def run(self):
        self.start_game = False

        # Main game loop
        while True:
            for event in pygame.event.get():
                
                if self.commonEvents(event):
                    continue
                elif event.type == pygame.FINGERDOWN:
                    if self.start_game != True:
                        continue
                    # Check if the mouse click is inside any rectangle
                    for rect in self.rectangles:
                        if self.is_inside_rect((event.x * self.WIDTH,event.y * self.HEIGHT), rect[0]):                          

                            if (rect[3] > 0 and rect[4] == False):
                                rect[4] = True
                                self.points = rect[3]
                                rect[3] = 0
                                rect[2] = self.GREEN
                            elif (rect[3] < 0 and rect[4] == False):
                                rect[4] = True
                                self.lives = -1
                                rect[3] = 0
                                rect[2] = self.ORANGE
                            else:
                                if rect[2] != self.GREEN:
                                    matching_entry = next((entry for entry in self.impreciseHitBoxes if entry[1] == 0), None)
                                    if matching_entry is not None:
                                        self.lives = -1
                                        matching_entry[1] = 1

                            
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
        with open('backWallClickGame.json', 'r') as file:
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

                elif not 'completed' in command:
                    if matching_entry is None:
                        self.impreciseHitBoxes.append([command_id,0])
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
                    elif matching_entry[4] == False and matching_entry[3] < 0:
                        self.points = abs(matching_entry[3])
                        self.server.point_update(self.points,self.lives)
                        self.points = 0
                        matching_entry[1] = False
                        matching_entry[2] = self.WHITE
                        matching_entry[3] = 0
                        matching_entry[4] = False
                    else:
                        # reset the rectangle
                        if matching_entry[4] == True:
                            matching_entry[1] = False
                            matching_entry[2] = self.WHITE
                            matching_entry[3] = 0
                            matching_entry[4] = False
                    
                    command['completed'] = True
        
                elif not 'completed' in command:
                    if matching_entry[4] != True:
                        if (matching_entry[3] > 0):
                            matching_entry[2] = self.RED
                        elif matching_entry[3] < 0:
                            matching_entry[2] = self.BLUE

                        matching_entry[3] = points 
            # Last Command       
            if command == commands[-1]:
                if time_since_start > time_end + 5:
                    self.server.send_end()
                    self.reset_game()

           

if __name__ == "__main__":
    backWallMainApp = BackWallMainApp(2560,1440,'activateMotor.local',12345)
    backWallMainApp.connect_client()
    backWallMainApp.run()