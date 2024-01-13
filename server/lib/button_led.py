from rpi_ws281x import *
from color_helpers import c

class LEDSegment:
    def __init__(self, strip, start_index, end_index):
        self.strip = strip
        self.start_index = start_index
        self.end_index = end_index

    def set_color(self, color):
        for i in range(self.start_index, self.end_index + 1):
            self.strip.setPixelColor(i, color)
        self.strip.show()

class LEDStripController:
    def __init__(self, pin, num_leds=25):
        # Initialize WS281x LED strip settings
        self.LED_COUNT = num_leds
        self.LED_PIN = pin
        self.LED_FREQ_HZ = 800000
        self.LED_DMA = 10
        self.LED_BRIGHTNESS = 50 #max is 255
        self.LED_INVERT = False
        self.LED_CHANNEL = 0

        # Create LED strip
        self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ,
                                       self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS, self.LED_CHANNEL)
        self.strip.begin()

        # Define segments for the strip
        self.segments = []
        segment1 = LEDSegment(self.strip, 0, 15)
        segment2 = LEDSegment(self.strip, 16, 23)
        segment3 = LEDSegment(self.strip, 24, self.LED_COUNT - 1)
        self.segments.extend([segment1, segment2, segment3])

    def set_segment_color(self, segment_index, color):
        self.segments[segment_index].set_color(color)

    def set_button_color(self, color):
        for i in range(len(self.segments)):
            self.segments[i].set_color(color)

    def turn_off_leds(self):
        self.set_button_color(c.no_light)
