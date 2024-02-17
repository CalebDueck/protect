from led_strip_ctrl import *
import time
import neopixel
import board



count = 1
backwall_strip1 = LEDStripController(num_leds=30, pin=18, isbutton=False, segment_border_num_array=[0,10,20,30])



def main():
    #see test_button for how to get arguments

    try:
        #nothing
        print("Starting button test")

        while(True):
            global count
            
            #set only one segment at a time

            time.sleep(1)
            backwall_strip1.set_segment_color(segment_index=(3+count-1)%3, color=c.no_light, off_vs_on=0) 

            time.sleep(1)
            backwall_strip1.set_segment_color(segment_index=count%3, color=c.color_list[(count)%len(c.color_list)], off_vs_on=0) 


            count = (count+1)%(3)
            # time.sleep(1)

    except KeyboardInterrupt:
        backwall_strip1.turn_off_leds()
        time.sleep(0.1)


if __name__ == '__main__':
    main()