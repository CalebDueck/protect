import matplotlib.pyplot as plt
import csv
import numpy as np

left_count = []
left_time = []
right_count = []
right_time = []
left_speed = []
right_speed = []

with open('speeds.csv','r') as csvfile: 
    lines = csv.reader(csvfile, delimiter=',') 
    for row in lines:
        if float(row[0])==-1 or float(row[1]) == -1:
            continue
        left_speed.append(float(row[0]))
        left_time.append(float(row[2]))
        right_speed.append(float(row[1]))
        right_time.append(float(row[3]))

plt.scatter(left_time, left_speed, color = 'g', 
         marker = 'o',label = "left speed")
plt.scatter(right_time, right_speed, color = 'r', 
         marker = 'o',label = "right speed") 
major_ticks = np.arange(0, 5000, 500)
plt.yticks(major_ticks)
plt.grid() 
plt.legend() 
plt.show() 