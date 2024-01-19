import pygame
import sys
from serverCommunication import *
import queue
import enum
import json
import time 
from serverGame import *

class MotorControllerMainApp(BaseServerGame):
    def __init__(self, width, height, host, port):
        super().__init__(width, height, host, port)

        self.impreciseHitBoxes = []

    def reset_game(self):
        pass

    def run(self):
        self.start_game = False

        # Main game loop
        while True:
            for event in pygame.event.get():
                
                if self.commonEvents(event):
                    continue                

            self.extractCustomEvents()
            
            # information
            self.update_information()


            # Update the display
            pygame.display.flip()

            # Control the frames per second
            pygame.time.Clock().tick(30)

    def read_game_file(self):
        with open('server/motorController.json', 'r') as file:
            self.game_data = json.load(file)   

    def update_information(self):
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
            points = command['points']
            speed = command['speed']
            if not 'completed' in command: 
                # pass speed to motor here
                print("Shot ball for command_id", command_id, "at speed", speed)
                command['completed'] = True

if __name__ == "__main__":
    motor_controller_main_app = MotorControllerMainApp(800,600,'activateMotor.local',12345)
    motor_controller_main_app.connect_client()
    motor_controller_main_app.run()