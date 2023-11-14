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
scan_data = [0] * 360

# Setup the RPLidar
PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(None, PORT_NAME, timeout=3)

# used to scale data to fit on the screen
max_distance = 0

# Modify these values based on your requirements
MIN_ANGLE = 0
MAX_ANGLE = 180
DISTANCE_THRESHOLD = 1000  # Adjust this based on your specific use case

SAFEZONE_WIDTH = 2000
SAFEZONE_HEIGHT = 500
SAFEZONE_TL = [-1000,1000]

def safe_zone_occupied(xy_data, min_points = 5):
    points_detected = 0
    for point in xy_data:
        if is_point_in_zone(point):
            points_detected = points_detected + 1
            if points_detected > min_points:
                return True
    return False

def is_point_in_zone(point):
    if SAFEZONE_TL[0]<=point[0]<=SAFEZONE_TL[0]+SAFEZONE_WIDTH:
        if SAFEZONE_TL[1]<=point[1]<=SAFEZONE_TL[1]+SAFEZONE_HEIGHT:
            return True
    return False

def lidar_to_xy(data):
    point_cloud = list()
    for angle in range(360):
        distance = data[angle]
        if distance > 0:  # ignore initially ungathered data points
            radians = angle * pi / 180.0
            x = distance * cos(radians)
            y = distance * sin(radians)
            point_cloud.append([x,y])
    return point_cloud
        
#WIP
def find_static_points(lidar, num_scans=10, distance_threshold=10):
    print("Calibrating static points")
    # Dictionary to store the observed points across scans
    static_points = {}

    for _ in range(num_scans):
        for scan in lidar.iter_scans():
            for (_, angle, distance) in scan:
                # Store the distance for each angle
                static_points.setdefault(min([359, floor(angle)]), []).append(distance)

        # Pause briefly to allow for a new scan to start
        print("Pausing")
        lidar.pause_scan()

    # Resume scanning after collecting static points
    lidar.resume_scan()

    print("filtering")
    # Filter static points based on the distance threshold
    # ie if they move more than the specified distance then they are not static
    static_points_filtered = {angle: sum(distances) / len(distances)
                              for angle, distances in static_points.items()
                              if all(abs(distance - distances[0]) < distance_threshold for distance in distances)}

    return static_points_filtered



def plot_points(data):
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



# pylint: disable=redefined-outer-name,global-statement
def process_data(data):
    xy_pointcloud = lidar_to_xy(data)
    plot_points(data)

    # Calculate the scaled position for the safe zone
    scaled_rect = (
        int(window_size[0] / 2 + SAFEZONE_TL[0] / max_distance * (window_size[0] / 2 - 1)),
        int(window_size[1] / 2 + SAFEZONE_TL[1] / max_distance * (window_size[1] / 2 - 1)),
        int(SAFEZONE_WIDTH / max_distance * (window_size[0] / 2 - 1)),
        int(SAFEZONE_HEIGHT / max_distance * (window_size[1] / 2 - 1)),
    )

    if safe_zone_occupied(xy_pointcloud):
        pygame.draw.rect(lcd, pygame.Color('green'), scaled_rect, 2)
    else:
        pygame.draw.rect(lcd, pygame.Color('red'), scaled_rect, 2)

    pygame.display.flip()





def main():
    lidar = RPLidar(None, '/dev/ttyUSB0', timeout=3)
    #static_points = find_static_points(lidar)
    #print("Static Points:", static_points)
    #static_xy=lidar_to_xy(static_points)
    #print("Static xy", static_xy)



    try:
        print(lidar.info)
        for scan in lidar.iter_scans():
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
