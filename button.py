import RPi.GPIO as GPIO
import time
from button_led import *

class Button:
    def __init__(self, presspin, ledpin, min_time_between_presses=0.5):
        self.pin = presspin
        self.last_pressed = 0
        self.filter_duration = min_time_between_presses  # Filter duration in seconds
        self.led = LEDStripController(num_leds=30, pin=ledpin)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.on_rising_edge, bouncetime=100)

    def on_rising_edge(self, channel):
        current_time = time.time()
        if current_time - self.last_pressed > self.filter_duration:
            self.last_pressed = current_time
            self.button_action()
    
    def button_action(self):
        if self.callback:
            self.callback()       
        

    def set_callback(self, callback):
        self.callback = callback
        
    def cleanup(self):
        GPIO.remove_event_detect(self.pin)
        self.led.turn_off_leds()
        GPIO.cleanup(self.pin)

