import RPi.GPIO as GPIO
import time

class Button:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.on_rising_edge, bouncetime=100)

    def on_rising_edge(self, channel):
        print("Rising edge detected on GPIO pin", self.pin)
        # Add your custom functionality here for the rising edge event
    
    '''
    #can have rising and falling edge by changing 
    GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self.on_edge, bouncetime=200)

    def on_edge(self, channel):
        if GPIO.input(channel):
            print("Rising edge detected on GPIO pin", self.pin)
        else:
            print("Falling edge detected on GPIO pin", self.pin)
    '''
    def cleanup(self):
        GPIO.remove_event_detect(self.pin)
        GPIO.cleanup(self.pin)

