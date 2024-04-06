# protect
Repo for all code used in the Protect game room

Need to activate venv to install libraries.


To run code use:
sudo venv/bin/python3 test_button.py

For the LIDAR
1. Open a terminal on your Raspberry Pi.
2. Create a virtual environment in your project directory (replace **`your_project_directory`** with the actual path):
    
    ```bash
    cd /path/to/your_project_directory
    python3 -m venv venv
    ```
    
3. Activate the virtual environment:
    
    ```bash
    source venv/bin/activate
    
    ```
    
4. Now, with the virtual environment activated, you can install the **`rplidar`** library:
    
    ```bash
    pip install rplidar - note we are using the the adafruit library
    pip install adafruit-circuitpython-rplidar
    
    ```
    
5. After installing the library, you can run your Python script within this virtual environment.
6. When you're done working on your project, deactivate the virtual environment:
    
    ```bash
    deactivate
    
    ```
    

Remember to activate the virtual environment every time you want to work on your project, and deactivate it when you're done.

Ensure you add timeout=3 to RPLidar function call

```jsx
PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(None, PORT_NAME, timeout=3)
```

*References*

SLAM-tech: https://wiki.slamtec.com/display/SD/1.LIDAR

Can reference their official repos.

ROS Setup: https://medium.com/robotics-with-ros/installing-the-rplidar-lidar-sensor-on-the-raspberry-pi-32047cde9588

Adafruit Setup: https://learn.adafruit.com/slamtec-rplidar-on-pi/using-the-slamtec-rplidar

Adafruit Repo: https://github.com/zlite/Adafruit_CircuitPython_RPLIDAR/blob/94fcbf9a5b4103313192403820fa2adac08c610d/examples/lidar_test.py
