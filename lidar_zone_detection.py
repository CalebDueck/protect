import time
from rplidar import RPLidar

# Modify these values based on your requirements
MIN_ANGLE = 45
MAX_ANGLE = 135
DISTANCE_THRESHOLD = 1000  # Adjust this based on your specific use case

def is_object_in_zone(scan_data):
    for scan in scan_data:
        angle = scan[1]
        distance = scan[2]
        if MIN_ANGLE <= angle <= MAX_ANGLE and distance < DISTANCE_THRESHOLD:
            return True, angle, distance
    return False, 0, 0

def main():
    lidar = RPLidar(None, '/dev/ttyUSB0', timeout=3)
    
    try:
        print("Waiting for lidar to stabilize...")
        time.sleep(2)

        for scan_data in lidar.iter_scans():
            object_detected, angle, dist = is_object_in_zone(scan_data)
            if object_detected:
                print("Object detected in the predetermined zone! Angle", angle, "dist",dist)
                # Add your code here to take action when an object is detected

    except KeyboardInterrupt:
        print('Stopping...')
    finally:
        lidar.stop()
        lidar.disconnect()

if __name__ == '__main__':
    main()
