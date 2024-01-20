import pygame
import sys
from serverCommunication import *
import queue
import enum
import json
import time 
from serverGame import *
from lib.button import Button
from lib.color_helpers import c
from include.defines import ActionEvents

    
class SideWallMainApp(BaseServerGame):
    def __init__(self, width, height, buttons, host, port):
        super().__init__(width, height, host, port)
        
        def button_click_callback(button_id):
            self.event_queue.put({"type":ActionEvents.BUTTON_CLICK_SIDEWALL, "message":{"id":button_id}})
            print("button clicked")
        # setup side buttons
        self.buttons = []
        _id = 0
        for press_pin, led_pin in buttons:
            button = Button(_id, press_pin, led_pin)
            button.set_callback(button_click_callback)
            button.led.turn_off_leds()
            self.buttons.append([button, False, c.no_light, 0])
            _id += 1

      
    def reset_game(self):
        for button in self.buttons:
            button[0].led.turn_off_leds()
            button[1] = False
            button[2] = c.no_light
            
            
    def run(self):
        self.start_game = False

        # Main game loop
        while True:
            for event in pygame.event.get():
                
                if self.commonEvents(event):
                    continue
                elif event.type == ActionEvents.BUTTON_CLICK_SIDEWALL:
                    button_id = event.dict['message']['id']
                    button = self.buttons[button_id]
                    if (button[3] > 0 and button[1] == False):
                        button[1] = True
                        self.points = button[3]
                        button[3] = 0
                        button[2] = c.green
                        button[0].led.set_button_color(color=c.green)
                    self.server.point_update(points=self.points,lives=self.lives)
                    self.points = 0
                    self.lives = 0
                    print("Sending Client Update")
                

            self.extractCustomEvents()
            
            self.update_information()

            # Update the display
            pygame.display.flip()

            # Control the frames per second
            pygame.time.Clock().tick(30)

    def read_game_file(self):
        with open('side_wall_game.json', 'r') as file:
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
            button_id = command['button_id']
            points = command['points']
            time_end = command['time_end']
            button = self.buttons[button_id]
            colour = command['colour']
            if time_since_start > time_end and not 'completed' in command:
                
                if button[1] == False and button[3] > 0:
                    self.lives = -1
                    self.server.point_update(self.points,self.lives)
                    self.lives = 0
                    button[1] = False
                    button[2] = c.no_light
                    button[3] = 0
                    button[0].led.set_button_color(color=c.no_light)
                else:
                    if button[1] == True:
                        button[1] = False
                        button[2] = c.no_light
                        button[3] = 0
                        button[0].led.set_button_color(color=c.no_light)

                command['completed'] = True
                
            elif not 'completed' in command:
                if button[1] != True:
                    if colour == 'R' and button[3] == 0:
                        button[0].led.set_button_color(color=c.red)
                    elif colour == 'B' and button[3] == 0:
                        button[0].led.set_button_color(color=c.blue)
                    
                    button[3] = points


               

if __name__ == "__main__":
    buttons = [(17,12)]
    sideWallMainApp = SideWallMainApp(800, 600, buttons,'activateMotor.local',12345)
    sideWallMainApp.connect_client()
    sideWallMainApp.run()
