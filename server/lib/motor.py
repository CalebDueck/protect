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
        self.kp = [0.001, 0.004]
        self.ki = [0,0]
        self.kd = [0.0001,0.0001]
        
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
        self.L_pwm = [-1] * 10_000
        self.R_pwm = [-1] * 10_000
        self.error_buf_len = 10
        self.speed_buf_len = 5

        
        self.running = False
    
    def handler(self, signal, frame):
        # Handle any cleanup here
        self.running = False
        self.pwm0.stop()
        self.pwm1.stop()
        GPIO.cleanup()
        with open("speeds.csv", 'w', newline='') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerows(zip(self.L_speed, self.R_speed, self.timestamps, self.L_pwm, self.R_pwm))

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
        
        Lerror_buf = [0] * self.error_buf_len
        Rerror_buf = [0] * self.error_buf_len
        Lspeed_buf = [0] * self.speed_buf_len
        Rspeed_buf = [0] * self.speed_buf_len
        err_buf_index = 0
        speed_buf_index = 0
        last_updated_l = time.perf_counter()
        last_updated_r = time.perf_counter()

        GPIO.setmode(GPIO.BCM)

        
        while 1:
            # increment left count on rising edge
            if GPIO.input(self.left_HAL) != old_value[0]:
                if old_value[0] == 0:
                    count[0] += 1
                old_value[0] = not old_value[0]
            # increment right count on rising edge

            if GPIO.input(self.right_HAL) != old_value_R:
                if old_value_R == 0:
                    count_R+=1
                old_value_R = not old_value_R
            # every 100ms, record the time and # of counts
            if count_L > 5 and count_R > 5 or time.perf_counter()-self.timestamps[i-1] > 0.1:
                self.timestamps[i] = time.perf_counter()
                Lspeed_buf[speed_buf_index] = count_L/(12*(self.timestamps[i]-self.timestamps[i-1]))*60;
                Rspeed_buf[speed_buf_index] = count_R/(12*(self.timestamps[i]-self.timestamps[i-1]))*60;
                avg_L_speed = 0
                avg_R_speed = 0
                for ind in range(self.speed_buf_len):
                    avg_L_speed += Lspeed_buf[ind]
                    avg_R_speed += Rspeed_buf[ind]
                self.L_speed[i] = avg_L_speed / self.speed_buf_len
                self.R_speed[i] = avg_R_speed / self.speed_buf_len
                count_L = 0
                count_R = 0
                i += 1
                speed_buf_index += 1
                if speed_buf_index >= (self.speed_buf_len):
                    speed_buf_index = 0
#             if time.perf_counter() - old_time > 0.05:
                old_time = time.perf_counter();
                Lerror = self.desired_speed - self.L_speed[i-1]
                Rerror = self.desired_speed - self.R_speed[i-1]
#                 print(Lerror)
                Lerror_buf[err_buf_index] = Lerror
                Rerror_buf[err_buf_index] = Rerror

                Ledot = 0
                Leint = 0
                Redot = 0
                Reint = 0

                if i > self.error_buf_len:
                    for ind in range(self.error_buf_len):
                        temp_i = err_buf_index - ind
                        prev_i = err_buf_index - ind - 1

                        if temp_i < 0:
                            temp_i = self.error_buf_len - ind
                        if prev_i < 0 :
                            prev_i = self.error_buf_len - ind -1
                        dt = self.timestamps[i-ind]-self.timestamps[i-ind-1]
                        Ledot += (Lerror_buf[temp_i] - Lerror_buf[prev_i])/dt
                        Leint += (Lerror_buf[temp_i] - Lerror_buf[prev_i])*dt
                        Redot += (Rerror_buf[temp_i] - Rerror_buf[prev_i])/dt
                        Reint += (Rerror_buf[temp_i] - Rerror_buf[prev_i])*dt
                Ledot /= self.error_buf_len
                Leint /= self.error_buf_len
                Redot /= self.error_buf_len
                Reint /= self.error_buf_len
                new_pwm_l = np.clip(self.pwm_l + self.kp[0]*Lerror + self.ki[0]*Leint + self.kd[0]*Ledot, 35, 60)
                new_pwm_r = np.clip(self.pwm_r + self.kp[1]*Rerror + self.ki[1]*Reint + self.kd[1]*Redot, 35, 60)
                print(new_pwm_l, new_pwm_r, Lerror, self.pwm_l, self.pwm_r)
                if(abs(new_pwm_l - self.pwm_l) > 1 and abs(Lerror) > 50 and time.perf_counter() - last_updated_l > 0.1):
                    self.pwm0.change_duty_cycle(new_pwm_l)
                    self.pwm_l = new_pwm_l
                    last_updated_l = time.perf_counter()
                if(abs(new_pwm_r - self.pwm_r) > 1 and abs(Rerror) > 50 and time.perf_counter() - last_updated_r > 0.1):
                    self.pwm1.change_duty_cycle(new_pwm_r)
                    self.pwm_r = new_pwm_r
                    last_updated_r = time.perf_counter()
                self.L_pwm[i] = self.pwm_l
                self.R_pwm[i] = self.pwm_r
                err_buf_index += 1
                if err_buf_index >= (self.error_buf_len):
                    err_buf_index = 0

            if self.running == 0:
                break
        
    def update_speed(self, rpm: int):
        num_steps = int((rpm - self.desired_speed) / 500)
        for step in range(num_steps):   
            self.desired_speed = self.desired_speed + 500
            print("setting speed to: ", self.desired_speed)
            time.sleep(0.2)
            
        self.desired_speed = rpm
        print("setting speed to: ", self.desired_speed)
#         self.pwm1.change_duty_cycle(rpm)
#         self.pwm0.change_duty_cycle(rpm)
    
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



