# SPDX-FileCopyrightText: 2019 Dave Astels for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Consume LIDAR measurement file and create an image for display.

Adafruit invests time and resources providing this open source code.
Please support Adafruit and open source hardware by purchasing
products from Adafruit!

Written by Dave Astels for Adafruit Industries
Copyright (c) 2019 Adafruit Industries
Licensed under the MIT license.

All text above must be included in any redistribution.
"""

import os
from math import cos, sin, pi, floor
import pygame
from adafruit_rplidar import RPLidar

# Set up pygame and the display
pygame.init()
pygame.display.set_caption('LIDAR Data')
window_size = (640, 480)
lcd = pygame.display.set_mode(window_size)
pygame.mouse.set_visible(False)
lcd.fill((0, 0, 0))
pygame.display.update()

# Setup the RPLidar
PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(None, PORT_NAME, timeout=3)

# used to scale data to fit on the screen
max_distance = 0

# pylint: disable=redefined-outer-name,global-statement
def process_data(data):
    global max_distance
    lcd.fill((0, 0, 0))
    for angle in range(360):
        distance = data[angle]
        if distance > 0:  # ignore initially ungathered data points
            if angle > 270:
                color = (0, 255, 0)
            elif angle > 180:
                color = (0, 0, 255)
            elif angle > 90:
                color = (255, 0, 0)
            else:
                color = (255, 255, 255)
            
            max_distance = max([min([5000, distance]), max_distance])
            radians = angle * pi / 180.0
            x = distance * cos(radians)
            y = distance * sin(radians)
            point = (
                int(window_size[0] / 2 + x / max_distance * (window_size[0] / 2 - 1)),
                int(window_size[1] / 2 + y / max_distance * (window_size[1] / 2 - 1)),
            )
            pygame.draw.circle(lcd, color, point, 1)
    pygame.display.update()

scan_data = [0] * 360

try:
    print(lidar.info)
    for scan in lidar.iter_scans():
        for (_, angle, distance) in scan:
            scan_data[min([359, floor(angle)])] = distance
        process_data(scan_data)

except KeyboardInterrupt:
    print('Stopping.')

lidar.stop()
lidar.disconnect()
