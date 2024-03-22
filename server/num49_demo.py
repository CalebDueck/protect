from lib.backwall_single_strip import *
import time
from lib.color_helpers import *

bot_half_pin = 13

num4_ind = [2,12,22,23,24,34,44,54,14,4]
num9_ind = [6,16,26,56,7,27,8,18,28,38,48,58,57]

count = 1
backwall = LEDBackwall_single(bot_half_pin,50)

def set_ind_colors(inds, col):
    for i in inds:
        backwall.set_color(i,col)


def main():
    print("inited and starting test")
    try:
        while(True):
            global count
            
            # if count%60 == 0:
            # backwall.set_color_all(c.white)
            backwall.turn_off_all()
            
            print(count)
            color = c.color_list[(count)%len(c.color_list)]
            set_ind_colors(num4_ind, color)
            set_ind_colors(num9_ind, color)

            backwall.show()
            count+=1
            time.sleep(5)


    except KeyboardInterrupt:
        backwall.turn_off_all()
        backwall.show()
        time.sleep(0.1)


if __name__ == '__main__':
    main()