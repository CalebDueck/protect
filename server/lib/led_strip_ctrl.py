from rpi_ws281x import *
from color_helpers import c
import time
import RPi.GPIO as GPIO



class LEDSegment:
    def __init__(self, strip, start_index, end_index):
        self.strip = strip
        self.start_index = start_index
        self.end_index = end_index

    def set_color(self, color, off_vs_on=0):
        for i in range(self.start_index, self.end_index + 1):
            #ie if off_vs_on == 1 want to have every other LED off, so if i%2 == 0 then on else off
            if i % (off_vs_on+1) == 0:
                self.strip.setPixelColor(i, color)
            else:
                self.strip.setPixelColor(i, c.no_light)
        time.sleep(0.01)

        self.strip.show()



# pin = pinnumber for data pin
# segment_border_num_array = array containing start index of each segment
# num_leds = total number of LEDs
# isbutton= boolean to determine if it should be configured as a button
# if isbutton==True then num_leds and segment_border_num_array doesn't matter and will be set to button presets

class LEDStripController:
    def __init__(self, pin, isbutton=False, segment_border_num_array=None, num_leds=None):
        # Initialize WS281x LED strip settings
        if isbutton:
            self.LED_COUNT = 25
        else:
            self.LED_COUNT = num_leds
        self.LED_PIN = pin
        self.LED_FREQ_HZ = 800000 #maybe change
        self.LED_DMA = 10
        self.LED_BRIGHTNESS = 30 #max is 255
        self.LED_INVERT = False

        #fix sync issues
        if pin==13:
            self.LED_CHANNEL = 1
        else:
            self.LED_CHANNEL=0
            
        # GPIO.setmode(GPIO.BCM)

        # GPIO.setup(pin, GPIO.OUT)

        # pwm_instance = GPIO.PWM(pin, self.LED_CHANNEL)
        # pwm_instance.start(0)

        # Create LED strip
        self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ,
                                       self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS, self.LED_CHANNEL)
        self.strip.begin()


        self.segments = []
        # Define segments for the strip
        if isbutton:
            segment1 = LEDSegment(self.strip, 0, 15)
            segment2 = LEDSegment(self.strip, 16, 23)
            segment3 = LEDSegment(self.strip, 24, self.LED_COUNT - 1)
            self.segments.extend([segment1, segment2, segment3])
        else:
            for i in range(len(segment_border_num_array)-1):
                if segment_border_num_array[i+1]>num_leds:
                    print("ERROR: segment index %d is out of range", i+1)
                else:
                    seg_i = LEDSegment(self.strip, segment_border_num_array[i], segment_border_num_array[i+1])
                    self.segments.append(seg_i)


    def set_segment_color(self, segment_index, color, off_vs_on = 0):
        if segment_index>=len(self.segments):
            print("ERROR: Tried setting nonexistent segment")
        else:
            self.segments[segment_index].set_color(color, off_vs_on)

    def set_strip_color(self, color):
        for i in range(len(self.segments)):
            self.segments[i].set_color(color)

    def turn_off_leds(self):
        self.set_strip_color(c.no_light)
