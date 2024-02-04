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
        self.pwm = [0,0]
        self.kp = (0.01, 0.01)
        self.ki = (0,0)
        self.kd = (0.01, 0.01)
        
        # setup arrays for storing speed
        self.R_timestamps = [-1] * 10_000
        self.L_timestamps = [-1] * 10_000
        self.L_speeds = [-1] * 10_000
        self.R_speeds = [-1] * 10_000
        
        self.R_timestamps[0] = time.perf_counter()
        self.L_timestamps[0] = time.perf_counter()
        self.L_speeds[0] = 0
        self.R_speeds[0] = 0
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
            wr.writerows(zip(self.L_speeds, self.R_speeds, self.L_timestamps, self.R_timestamps))
        print('\r\nSIGINT or CTRL-C detected. Exiting gracefully')
        self.motorThread.join()
        exit(0)


    def run_launcher(self, rpm: int):
        # start pwm channels at 0%
        self.pwm0.start(0)
        self.pwm1.start(0)
        
        # read initial HAL sensors values
        old_value = [GPIO.input(self.left_HAL),GPIO.input(self.right_HAL)]
        
        # read initial time for speed calcs
        old_time = [time.perf_counter(), time.perf_counter()] # .0 = left, .1 = right
        pid_time = time.perf_counter()
        
        # setup count variables for HAL sensor
        count = [0,0] # count.0 = left count, count.1 = right count
        i = [0, 0]
        
        # setup error buffer for pid calcs
        error_buf = [[0,0]] * 5 #(.0 = left error, .1 = right error)
        buf_index = 0
        
        while 1:
            # increment left count on rising edge
            if GPIO.input(self.left_HAL) != old_value[0]:
                if old_value[0] == 0:
                    count[0] += 1
                old_value[0] = not old_value[0]
            # increment right count on rising edge
            if GPIO.input(self.right_HAL) != old_value[1]:
                if old_value[1] == 0:
                    count[1] += 1
                old_value[1] = not old_value[1]
            # every 100ms or every 10 counts (whichever is faster), record the new wheelspeed
            if time.perf_counter() - old_time[0] > 0.1 or count[0] > 40:
                i[0] += 1
                self.L_timestamps[i[0]] = time.perf_counter()
                self.L_speeds[i[0]] = count[0]/(12*(self.L_timestamps[i[0]]-self.L_timestamps[i[0]-1]))*60;
                old_time[0] = time.perf_counter();
                count[0] = 0
            if time.perf_counter() - old_time[1] > 0.1 or count[1] > 40:
                i[1] += 1
                self.R_timestamps[i[1]] = time.perf_counter()
                self.R_speeds[i[1]] = count[1]/(12*(self.R_timestamps[i[1]]-self.R_timestamps[i[1]-1]))*60;
                old_time[1] = time.perf_counter();
                count[1] = 0
            # every 10ms, run the pid calculations
            if time.perf_counter() - pid_time > 0.1 and i[0] >= 0 and i[1] >= 0:
                # calculate e, edot, eint
                error_buf[buf_index] = [self.desired_speed - self.L_speeds[i[0]],
                                        self.desired_speed - self.R_speeds[i[1]]]               
                Ledot = 0
                Leint = 0
                Redot = 0
                Reint = 0
                if i[0] > 4 and i[1] > 4:
                    for ind in range(5):
                        temp_i = buf_index - ind
                        prev_i = buf_index - ind - 1
                        if temp_i < 0:
                            temp_i = 5 - ind
                        if prev_i < 0 :
                            prev_i = 5 - ind -1
                        L_dt = self.L_timestamps[i[0]-ind]-self.L_timestamps[i[0]-ind-1]
                        R_dt = self.R_timestamps[i[1]-ind]-self.R_timestamps[i[1]-ind-1]
                        Ledot += (error_buf[temp_i][0] - error_buf[prev_i][0])/L_dt
                        Leint += (error_buf[temp_i][0] - error_buf[prev_i][0])*L_dt
                        Redot += (error_buf[temp_i][1] - error_buf[prev_i][1])/R_dt
                        Reint += (error_buf[temp_i][1] - error_buf[prev_i][1])*R_dt
                Ledot /= 5
                Leint /= 5
                Redot /= 5
                Reint /= 5
                # find and set new speed using kp, ki, kd values
                new_pwm_l = np.clip(self.pwm[0] + self.kp[0]*error_buf[buf_index][0] + self.ki[0]*Leint + self.kd[0]*Ledot, 0, 60)
                new_pwm_r = np.clip(self.pwm[1] + self.kp[1]*error_buf[buf_index][1] + self.ki[1]*Reint + self.kd[1]*Redot, 0, 60)
                if(abs(new_pwm_l - self.pwm[0]) > 0):
                    self.pwm0.change_duty_cycle(new_pwm_l)
                    self.pwm[0] = new_pwm_l
                if(abs(new_pwm_r - self.pwm[1]) > 0):
                    self.pwm1.change_duty_cycle(new_pwm_r)
                    self.pwm[1] = new_pwm_r
                # update indices, reset time
                buf_index += 1
                if buf_index == 4:
                    buf_index = 0
                pid_time = time.perf_counter()
            if self.running == 0:
                break
        
    def update_speed(self, rpm: int):
        print("Speed Update", rpm)
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



