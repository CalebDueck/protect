from button import Button 
from color_helpers import c
import argparse

import time
count = 0
button_pin = 17  # Replace with the GPIO pin number you're using
led_pin = 18 
button = Button(button_pin, led_pin)
button2 = Button(20, 21) # only using the light

def shift_color():
    global count
    button.led.set_segment_color(segment_index=0, color=c.color_list[count%len(c.color_list)])  # Set color for segment 0
    button.led.set_segment_color(segment_index=1, color=c.color_list[(count+1)%len(c.color_list)])  # Set color for segment 1
    button.led.set_segment_color(segment_index=2, color=c.color_list[(count+2)%len(c.color_list)])  # Set color for segment 2
    count+=1
    print("button pressed ", count, "times")


def shift_rainbow_color():
    global count
    button.led.set_segment_color(segment_index=0, color=c.rainbow[count%len(c.rainbow)])  # Set color for segment 0
    button.led.set_segment_color(segment_index=1, color=c.rainbow[(count+1)%len(c.rainbow)])  # Set color for segment 1
    button.led.set_segment_color(segment_index=2, color=c.rainbow[(count+2)%len(c.rainbow)])  # Set color for segment 2
    count+=1
    print("button pressed ", count, "times")


def toggle_white():
    global count
    if(count==0):
        count=1
        button.led.set_button_color(color=c.white)
        button2.led.turn_off_leds()
    else:
        count=0
        button.led.turn_off_leds()
        button2.led.set_button_color(color=c.white)



def main():
    button.led.set_button_color(color=c.white)
    button2.led.set_button_color(color=c.white)

    # Access the value of the argument 
    button.set_callback(toggle_white)
    

    try:
        #nothing
        print("Starting button test")
        while(True):
            time.sleep(0.01)

    except KeyboardInterrupt:
        button.cleanup()


if __name__ == '__main__':
    main()
