import matplotlib.pyplot as plt
import csv
import numpy as np

left_count = []
left_time = []
right_count = []
right_time = []
left_speed = []
right_speed = []
left_pwm = []
right_pwm = []
time_between = []

with open('speeds.csv','r') as csvfile: 
    lines = csv.reader(csvfile, delimiter=',') 
    for row in lines:
        if float(row[0])==-1 or float(row[1]) == -1:
            continue
        left_speed.append(float(row[0]))
        left_time.append(float(row[2]))
        right_speed.append(float(row[1]))
        left_pwm.append(float(row[3]))
        right_pwm.append(float(row[4]))

# for i in range(len(left_time)):
#     if i == 0:
#         continue
#     time_between.append(left_time[i] - left_time[i-1])    

fig, ax = plt.subplots()
# ax.scatter(range(0, len(time_between)),time_between)
ax.scatter(left_time, left_speed, color = 'g', 
         marker = 'o',label = "left speed")

ax.scatter(left_time, right_speed, color = 'r', 
         marker = 'o',label = "right speed")
# ax1 = ax.twinx()
# ax1.scatter(left_time, left_pwm, color = 'b', 
#          marker = 'o',label = "left speed")
# ax1.scatter(left_time, right_pwm, color = 'k', 
#          marker = 'o',label = "right speed") 
#major_ticks = np.arange(0, 5000, 500)
# ax.set_ylim([0, 0.15])
# ax.set_xlim([30,70])
ax.grid() 
ax.legend() 

plt.show() 