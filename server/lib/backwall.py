from led_strip_ctrl import *
import time
import board


class LEDBackwall:
    def __init__(self, top_half_pin, bottom_half_pin):
        num_segments_per_row = 10
        num_leds_per_row = 180
        num_rows_per_pin = 3
        
        segment_def_arr = list()
        for i in range(num_segments_per_row*num_rows_per_pin+1):
            segment_def_arr.append(int(i*num_leds_per_row/num_segments_per_row))

        self.top_strip = LEDStripController(num_leds=num_leds_per_row*num_rows_per_pin, pin=top_half_pin, isbutton=False, segment_border_num_array=segment_def_arr)
        self.bot_strip = LEDStripController(num_leds=num_leds_per_row*num_rows_per_pin, pin=bottom_half_pin, isbutton=False, segment_border_num_array=segment_def_arr)

    def square_index_to_strip_index(self, square_index):
        top_strip = False
        strip_index = -1
        if square_index < 30:
            top_strip = True
            if square_index>=0 and square_index<=9:
                strip_index = 20 + square_index
            elif square_index>=10 and square_index<=19:
                strip_index = 19 - (square_index%10)
            elif square_index>=20 and square_index<=29:
                strip_index = square_index%10
        else:
            if square_index>=30 and square_index<=39:
                strip_index = square_index%10
            elif square_index>=40 and square_index<=49:
                strip_index = 19 - (square_index%10)
            elif square_index>=50 and square_index<=59:
                strip_index = 20 + square_index%10

        return top_strip, strip_index

    def set_color(self, square_index, color, off_vs_on=0):
        top_strip, strip_index = self.square_index_to_strip_index(square_index)
        # print("Index",square_index)
        # print("Top strip",top_strip)
        # print("strip intx", strip_index)
        
        if strip_index == -1:
            # print("Invalid square_index received")
            return
        
        if top_strip==True:
            # self.top_strip.set_segment_color(strip_index, c.no_light) 
            self.top_strip.set_segment_color(strip_index, color, off_vs_on) 
        elif top_strip==False:
            # self.bot_strip.set_segment_color(strip_index, c.no_light) 
            self.bot_strip.set_segment_color(strip_index, color, off_vs_on) 

    def turn_off_segment(self, square_index):
        top_strip, strip_index = self.square_index_to_strip_index(square_index)
        if strip_index == -1:
            print("Invalid square_index received")
            return
        
        if top_strip==True:
            self.top_strip.set_segment_color(strip_index, c.no_light) 
        elif top_strip==False:
            self.bot_strip.set_segment_color(strip_index, c.no_light)

    def turn_off_all(self):
        self.top_strip.turn_off_leds()
        self.bot_strip.turn_off_leds()
        self.show()

    def show(self):
        self.top_strip.show()
        self.bot_strip.show()

        








count = 1

# backwall_strip1 = neopixel.NeoPixel(board.D18, num_leds_per_row*num_rows_per_pin, brightness=0.1)
# backwall_strip2 = neopixel.NeoPixel(board.D12, num_leds_per_row*num_rows_per_pin, brightness=0.1)



def main():
    #see test_button for how to get arguments

    try:
        #nothing
        print("Starting button test")
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
                #time.sleep(0.01)
                backwall_strip1.set_segment_color(segment_index=i, color=c.color_list[(count+i)%len(c.color_list)], off_vs_on=0) 
                
                #time.sleep(0.01)
                backwall_strip2.set_segment_color(segment_index=i, color=c.color_list[(count+i)%len(c.color_list)], off_vs_on=0)


            count = (count+1)%(num_segments_per_row*num_rows_per_pin)

    except KeyboardInterrupt:
        backwall_strip1.turn_off_leds()
        backwall_strip2.turn_off_leds()
        # backwall_strip1.fill((0, 0, 0))
        # backwall_strip2.fill((0, 0, 0))
        time.sleep(0.1)


if __name__ == '__main__':
    main()