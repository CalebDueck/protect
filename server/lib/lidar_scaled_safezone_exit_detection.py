import os
from math import cos, sin, pi, floor
import numpy as np
import pygame
from adafruit_rplidar import RPLidar


# Set up pygame and the display
pygame.init()
pygame.display.set_caption('LIDAR Data')
window_size = (1920, 1080)
lcd = pygame.display.set_mode(window_size)
pygame.mouse.set_visible(False)
lcd.fill((0, 0, 0))
pygame.display.update()

# Setup the RPLidar
PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(None, PORT_NAME, timeout=3)

# used to scale data to fit on the screen
max_distance = 4000

# Modify these values based on your requirements
MIN_ANGLE = 0
MAX_ANGLE = 180
DISTANCE_THRESHOLD = 1000  # Adjust this based on your specific use case

SAFEZONE_WIDTH = 3000
SAFEZONE_HEIGHT = 1500
SAFEZONE_TL = [-1500,2500] #top left of safe zone
PLAY_AREA_WIDTH =3000
PLAY_AREA_HEIGHT = 3500
PLAY_AREA_TL = [-1500,800]




def safe_zone_occupied(xy_data, min_points = 3):
    points_detected = 0
    for point in xy_data:
        if is_point_in_safezone(point):
            points_detected = points_detected + 1
            if points_detected > min_points:
                return True
    return False

def is_point_in_rect(point, rect_top_left, rect_width, rect_height):
    if rect_top_left[0]<=point[0]<=rect_top_left[0]+rect_width:
        if rect_top_left[1]<=point[1]<=rect_top_left[1]+rect_height:
            return True
    return False

def is_point_in_safezone(point):
    return is_point_in_rect(point, SAFEZONE_TL, SAFEZONE_WIDTH, SAFEZONE_HEIGHT)

def is_point_in_playarea(point):
    return is_point_in_rect(point, PLAY_AREA_TL, PLAY_AREA_WIDTH, PLAY_AREA_HEIGHT)

def lidar_to_xy(data):
    point_cloud = list()
    for angle in range(1080):
        distance = data[angle]
        if distance > 0:  # ignore initially ungathered data points
            radians = angle * pi / 180.0
            x = distance * cos(radians)
            y = distance * sin(radians)
            point_cloud.append([x,y])
    return point_cloud
        

def plot_point(point, color=(255,0,0)):
    x = point[0]
    y = point[1]
    scaledpoint = (
        int(transform_x(x)),
        int(transform_y(y)),
    )
    pygame.draw.circle(lcd, color, scaledpoint, 3)

def plot_points_xy(data, color=(255,0,0)):
    global max_distance
    for point in data:
        plot_point(point, color)
        

            
def scale_x(x):
    return x / 2000 * (window_size[0] / 2 - 1)
def scale_y(y):
    return y / 6000 * (window_size[1])

def transform_x(x):
    return window_size[0] / 2 + scale_x(x)
def transform_y(y):
    return scale_y(y)

def find_average_line_of_best_fit(xy):
    # Convert the 2D array to a numpy array for easier manipulation
    xy_np = np.array(xy)

    # Calculate the average of x and y coordinates
    avg_x = np.mean(xy_np[:, 0])  # Assuming x-coordinates are in column 0
    avg_y = np.mean(xy_np[:, 1])  # Assuming y-coordinates are in column 1
    std_dev_x = np.std(xy_np[:, 0])

    # Calculate the slope (m) and y-intercept (b) for the line of best fit
    # Using numpy's polyfit to perform linear regression
    m, b = np.polyfit(xy_np[:, 0], xy_np[:, 1], 1)

    # Extend the line from the average point by 10 units in both directions
    x_values = np.array([avg_x - std_dev_x, avg_x + std_dev_x])
    y_values = m * x_values + b

    return (avg_x, avg_y), (x_values, y_values)


def filter_points_in_play_area(xy_data):
    filtered_data = list()
    for point in xy_data:
        if is_point_in_playarea(point):
            filtered_data.append(point)

    return filtered_data


# pylint: disable=redefined-outer-name,global-statement
def process_data(data):
    lcd.fill((0, 0, 0))
    xy_pointcloud = lidar_to_xy(data)
    xy_in_frame = filter_points_in_play_area(xy_pointcloud)
    #plot_points_xy(xy_pointcloud)
    plot_points_xy(xy_in_frame, (0,255,0))

    if len(xy_in_frame)>3:
        centrepoint, linexy = find_average_line_of_best_fit(xy_in_frame)
        # Draw the average point
        pygame.draw.circle(lcd, (255, 255, 255), (transform_x(int(centrepoint[0])), transform_y(int(centrepoint[1]))), 10)
        # Draw the line of best fit
        pygame.draw.line(lcd, (0, 255, 255), 
                        (transform_x(linexy[0][0]), transform_y(linexy[1][0])), 
                        (transform_x(linexy[0][1]), transform_y(linexy[1][1])), 4)



    # Calculate the scaled position for the safe zone
    scaled_safezone = (
        int(transform_x(SAFEZONE_TL[0])),
        int(transform_y(SAFEZONE_TL[1])),
        int(scale_x(SAFEZONE_WIDTH)),
        int(scale_y(SAFEZONE_HEIGHT)),
    )


    scaled_playarea = (
        int(transform_x(PLAY_AREA_TL[0])),
        int(transform_y(PLAY_AREA_TL[1])),
        int(scale_x(PLAY_AREA_WIDTH)),
        int(scale_y(PLAY_AREA_HEIGHT)),
    )


    if safe_zone_occupied(xy_pointcloud):
        pygame.draw.rect(lcd, pygame.Color('green'), scaled_safezone, 2)
    else:
        pygame.draw.rect(lcd, pygame.Color('red'), scaled_safezone, 2)

    pygame.draw.rect(lcd, pygame.Color('blue'), scaled_playarea, 2)

    pygame.display.flip()





def main():
    lidar = RPLidar(None, '/dev/ttyUSB0', timeout=3)

    #static_points = filter_static_points(lidar)
    #print("Static Points:", static_points)
    #static_xy=lidar_to_xy(static_points)
    #print("Static xy", static_xy)



    try:
        print(lidar.info)
        scan_data = [0] * 1080 #zero out scan data each time
        
        for scan in lidar.iter_scans():
            
            for i in range(360):
                scan_data[720+i] = scan_data[360+i]
                scan_data[360+i] = scan_data[i] 
                scan_data[i] = 0 #zero out first scan data each time
            for (_, angle, distance) in scan:
                scan_data[min([359, floor(angle)])] = distance


            process_data(scan_data)


            
    except KeyboardInterrupt:
        print('Stopping...')
    finally:
        lidar.stop()
        lidar.disconnect()

if __name__ == '__main__':
    main()
