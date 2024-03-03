import serial 
import time 

class ArduinoSerial: 
    def __init__(self, com_port, baud_rate): 
        self.comm = serial.Serial(port=com_port, baudrate=baud_rate)

    def write_read(self, message):
        self.comm.write(bytes(message, 'utf-8'))
        time.sleep(0.05)
        return self.comm.readline()
    
    def write(self, message):
        self.comm.write(bytes(message,'utf-8'))

if __name__ == "__main__":
    comm = ArduinoSerial("COM4", 9600)
    while(1):
        message = input("Enter Arduino Command to send")
        message += "\n"
        comm.write(message)