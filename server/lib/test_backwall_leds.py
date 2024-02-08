from led_strip_ctrl import *
import time

led_pin = 18 
segment_def_arr = [0, 10, 20, 30, 40, 50, 55, 60]

count = 1
backwall_strip = LEDStripController(num_leds=60, pin=led_pin, isbutton=False, segment_border_num_array=segment_def_arr)



def main():
    #see test_button for how to get arguments

    try:
        #nothing
        print("Starting button test")
        while(True):
            global count
            for i in range(len(segment_def_arr)-1):
                backwall_strip.set_segment_color(segment_index=i, color=c.color_list[(count+i)%len(c.color_list)], off_vs_on=0) 


            count+=1
            time.sleep(1)

    except KeyboardInterrupt:
        backwall_strip.turn_off_leds()


if __name__ == '__main__':
    main()