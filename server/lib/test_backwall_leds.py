from led_strip_ctrl import *
import time
import neopixel
import board

led_pins = [13, 18] 
num_segments_per_row = 1
num_leds_per_row = 30
num_rows_per_pin = 1

segment_def_arr = list()
for i in range(num_segments_per_row*num_rows_per_pin+1):
    segment_def_arr.append(int(i*num_leds_per_row/num_segments_per_row))

count = 1
backwall_strip1 = LEDStripController(num_leds=num_leds_per_row*num_rows_per_pin, pin=led_pins[0], isbutton=False, segment_border_num_array=segment_def_arr)

backwall_strip2 = LEDStripController(num_leds=num_leds_per_row*num_rows_per_pin, pin=led_pins[1], isbutton=False, segment_border_num_array=segment_def_arr)
# backwall_strip1 = neopixel.NeoPixel(board.D18, num_leds_per_row*num_rows_per_pin, brightness=0.1)
# backwall_strip2 = neopixel.NeoPixel(board.D12, num_leds_per_row*num_rows_per_pin, brightness=0.1)



def main():
    #see test_button for how to get arguments

    try:
        #nothing
        print("Starting led test")
        # time.sleep(0.5)
        # backwall_strip2.set_strip_color(color=c.green)
        # time.sleep(5)

        # backwall_strip1.set_strip_color(color=c.blue)
        # backwall_strip2.fill((255, 0, 0))
        # time.sleep(0.1)
        # backwall_strip1.fill((255, 0, 0))

        while(True):
            global count
            
            #set only one segment at a time            
            # time.sleep(0.05)

            # backwall_strip1.set_segment_color(segment_index=(29+count-1)%29, color=c.no_light, off_vs_on=2) 
            # backwall_strip2.set_segment_color(segment_index=(29+count-1)%29, color=c.no_light, off_vs_on=2)
            # time.sleep(0.05)

            # backwall_strip1.set_segment_color(segment_index=count%29, color=c.color_list[(count)%len(c.color_list)], off_vs_on=2) 
            # backwall_strip2.set_segment_color(segment_index=count%29, color=c.color_list[(count)%len(c.color_list)], off_vs_on=2)


            # rainbow segments
            for i in range(len(segment_def_arr)-1):
                print("Switch led test")
                time.sleep(0.5)
                if(count%12>6):
                    backwall_strip1.set_segment_color(segment_index=i, color=c.color_list[(count+i)%len(c.color_list)], off_vs_on=0) 
                
                else:
                    backwall_strip2.set_segment_color(segment_index=i, color=c.color_list[(count+i)%len(c.color_list)], off_vs_on=0)


            time.sleep(0.5)
            count = (count+1)

    except KeyboardInterrupt:
        backwall_strip1.turn_off_leds()
        backwall_strip2.turn_off_leds()
        # backwall_strip1.fill((0, 0, 0))
        # backwall_strip2.fill((0, 0, 0))
        time.sleep(0.1)


if __name__ == '__main__':
    main()