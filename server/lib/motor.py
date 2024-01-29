from rpi_hardware_pwm import HardwarePWM
import time
from signal import signal, SIGINT
import RPi.GPIO as GPIO
import csv
import threading
import queue
import numpy as np

class launcher_motors:
    def __init__(self, left_HAL_gpio, right_HAL_gpio):
        #setup a ctrl+c interrupt handler to exit gracefully
        signal(SIGINT, self.handler)
        
        # Hookup HAL sensors
        self.left_HAL = left_HAL_gpio
        self.right_HAL = right_HAL_gpio
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.left_HAL, GPIO.IN)
        GPIO.setup(self.right_HAL, GPIO.IN)
        
        # hookup left and right motors to GPIO 18 and GPIO 19 to control pwm
        self.pwm0 = HardwarePWM(pwm_channel=0, hz=25_000, chip=0) #left
        self.pwm1 = HardwarePWM(pwm_channel=1, hz=25_000, chip=0) #right
        
        # set speed control params
        self.desired_speed = 0
        self.pwm_l = 0
        self.pwm_r = 0
        self.kp = 0.01
        self.ki = 0
        self.kd = 0.01
        
        # setup arrays for storing speed
        self.timestamps = [-1] * 10_000
        self.L_speed = [-1] * 10_000
        self.R_speed = [-1] * 10_000
        self.timestamps[0] = time.perf_counter()
        self.L_speed[0] = 0
        self.R_speed[0] = 0
        self.motorThread = 0
        
        self.running = False
    
    def handler(self, signal, frame):
        # Handle any cleanup here
        self.running = False
        self.pwm0.stop()
        self.pwm1.stop()
        GPIO.cleanup()
        with open("speeds.csv", 'w', newline='') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerows(zip(self.L_speed, self.R_speed, self.timestamps))
        print('\r\nSIGINT or CTRL-C detected. Exiting gracefully')
        self.motorThread.join()
        exit(0)


    def run_launcher(self, rpm: int):
        # start pwm channels at 0%
        self.pwm0.start(0)
        self.pwm1.start(0)
        
        # read initial HAL sensors values
        old_value_L = GPIO.input(self.left_HAL)
        old_value_R = GPIO.input(self.right_HAL)
        
        # read initial time for speed calcs
        old_time = time.perf_counter()
        
        # setup count variables for HAL sensor
        count_L = 0
        count_R = 0
        
        i = 0
        
        Lerror_buf = [0,0,0,0,0]
        Rerror_buf = [0,0,0,0,0]
        buf_index = 0
        
        while 1:
            # increment left count on rising edge
            if GPIO.input(self.left_HAL) != old_value_L:
                if old_value_L == 0:
                    count_L+=1
                old_value_L = not old_value_L
            # increment right count on rising edge
            if GPIO.input(self.right_HAL) != old_value_R:
                if old_value_R == 0:
                    count_R+=1
                old_value_R = not old_value_R
            # every 100ms, record the time and # of counts
            if time.perf_counter() - old_time > 0.1:
                self.timestamps[i] = time.perf_counter()
                self.L_speed[i] = count_L/(12*(self.timestamps[i]-self.timestamps[i-1]))*60;
                self.R_speed[i] = count_R/(12*(self.timestamps[i]-self.timestamps[i-1]))*60;
                old_time = time.perf_counter();
                count_L = 0
                count_R = 0
                Lerror = self.desired_speed - self.L_speed[i]
                Rerror = self.desired_speed - self.R_speed[i]
                Lerror_buf[buf_index] = Lerror
                Rerror_buf[buf_index] = Rerror
                Ledot = 0
                Leint = 0
                Redot = 0
                Reint = 0
                if (i > 4):
                    for ind in range(5):
                        temp_i = buf_index - ind
                        prev_i = buf_index - ind - 1
                        if temp_i < 0:
                            temp_i = 5 - ind
                        if prev_i < 0 :
                            prev_i = 5 - ind -1
                        dt = self.timestamps[i-ind]-self.timestamps[i-ind-1]
                        Ledot += (Lerror_buf[temp_i] - Lerror_buf[prev_i])/dt
                        Leint += (Lerror_buf[temp_i] - Lerror_buf[prev_i])*dt
                        Redot += (Rerror_buf[temp_i] - Rerror_buf[prev_i])/dt
                        Reint += (Rerror_buf[temp_i] - Rerror_buf[prev_i])*dt
                Ledot /= 5
                Leint /= 5
                Redot /= 5
                Reint /=5
                #print(error, edot, eint)
                new_pwm_l = np.clip(self.pwm_l + self.kp*Lerror + self.ki*Leint + self.kd*Ledot, 0, 60)
                new_pwm_r = np.clip(self.pwm_r + self.kp*Rerror + self.ki*Reint + self.kd*Redot, 0, 60)
                if(abs(new_pwm_l - self.pwm_l) > 1):
                    self.pwm0.change_duty_cycle(new_pwm_l)
                    self.pwm_l = new_pwm_l
                if(abs(new_pwm_r - self.pwm_r) > 1):
                    self.pwm1.change_duty_cycle(new_pwm_r)
                    self.pwm_r = new_pwm_r
                i += 1
                buf_index += 1
                if buf_index == 4:
                    buf_index = 0
            if self.running == 0:
                break
        
    def update_speed(self, rpm: int):
        self.desired_speed = rpm
    
    def start_thread(self):
        self.running = True
        self.motorThread = threading.Thread(target=self.run_launcher, args = (0,))
        self.motorThread.start()

if __name__ == '__main__':
    launcher = launcher_motors(16, 26)
    launcher.start_thread()
    while (True):
        rpm = int(input('Enter New RPM: '))
        launcher.update_speed(rpm)



