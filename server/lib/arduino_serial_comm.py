import serial 
import time 

class ArduinoSerial: 
    def __init__(self, com_port, baud_rate): 
        self.comm = serial.Serial(port=com_port, baudrate=baud_rate)

    def write_read(self, message):
        self.comm.write(bytes(message, 'utf-8'))
        time.sleep(0.05)
        return self.comm.readline()
