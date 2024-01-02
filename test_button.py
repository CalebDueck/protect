from button_press import Button 
from button_led import LEDStripController
from rpi_ws281x import *

import time

color_list = [Color(255, 0, 0), Color(255, 255, 0), Color(0, 255, 0),  Color(0, 255, 255), Color(0, 0, 255), Color(255, 0, 255),]

# Example usage:
button_pin = 17  # Replace with the GPIO pin number you're using
button = Button(button_pin)
try:
    count = 0
    while True:
        time.sleep(0.5)
        strip_controller = LEDStripController(num_leds=30, pin=18)
        strip_controller.set_segment_color(segment_index=0, color=color_list[count%len(color_list)])  # Set color for segment 0
        strip_controller.set_segment_color(segment_index=1, color=color_list[(count+1)%len(color_list)])  # Set color for segment 1
        strip_controller.set_segment_color(segment_index=2, color=color_list[(count+2)%len(color_list)])  # Set color for segment 2
        count+=1

except KeyboardInterrupt:
    button.cleanup()




# Example usage:
