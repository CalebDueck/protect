# color helpers
from rpi_ws281x import Color


class Colors:
    red = Color(255, 0, 0)
    yellow = Color(255, 255, 0)
    green = Color(0, 255, 0)
    cyan = Color(0, 255, 255)
    blue = Color(0, 0, 255)
    magenta = Color(255, 0, 255)
    white = Color(255,255,255)
    orange = Color(255, 165, 0)
    violet = Color(138, 43, 226)
    indigo = Color(75, 0, 130)

    no_light = Color(0,0,0)
    color_list = [red, yellow, green, cyan, blue, magenta]
    rainbow = [red, orange, yellow, green, blue, indigo, violet]

c = Colors()