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
            self.buttons.append([button, False, c.no_light])
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
                    self.buttons[button_id][0].led.set_button_color(color=c.white)

                    print("set color to white")
                    break
                

            self.extractCustomEvents()


            # Update the display
            pygame.display.flip()

            # Control the frames per second
            pygame.time.Clock().tick(30)

    def read_game_file(self):
        with open('backWallClickGame.json', 'r') as file:
            self.game_data = json.load(file)   

               

if __name__ == "__main__":
    buttons = [(17,18)]
    sideWallMainApp = SideWallMainApp(800, 600, buttons,'activateMotor.local',12345)
    sideWallMainApp.connect_client()
    sideWallMainApp.run()
