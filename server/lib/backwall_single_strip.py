from .led_strip_ctrl import *
import time
import board


class LEDBackwall_single:
    def __init__(self, pin, brightness=255):
        num_segments_per_row = 10
        num_leds_per_row = 180
        num_rows_per_pin = 6
        
        segment_def_arr = list()
        for i in range(num_segments_per_row*num_rows_per_pin+1):
            segment_def_arr.append(int(i*num_leds_per_row/num_segments_per_row))

        self.strip = LEDStripController(num_leds=num_leds_per_row*num_rows_per_pin, pin=pin, brightness=brightness, isbutton=False, segment_border_num_array=segment_def_arr)

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
            self.strip.set_segment_color(strip_index+30, c.no_light) 
            self.strip.set_segment_color(strip_index+30, color, off_vs_on) 
        elif top_strip==False:
            self.strip.set_segment_color(strip_index, c.no_light) 
            self.strip.set_segment_color(strip_index, color, off_vs_on)

    def turn_off_segment(self, square_index):
        top_strip, strip_index = self.square_index_to_strip_index(square_index)
        if strip_index == -1:
            print("Invalid square_index received")
            return
        
        if top_strip==True:
            self.strip.set_segment_color(strip_index+30, c.no_light) 
        elif top_strip==False:
            self.strip.set_segment_color(strip_index, c.no_light)


    def set_color_all(self, color):
        self.strip.set_strip_color(color)
        
    def turn_off_all(self):
        self.strip.turn_off_leds()
        self.show()

    def show(self):
        self.strip.show()

        






