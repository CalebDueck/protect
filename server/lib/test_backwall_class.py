from backwall_single_strip import *
import time

top_half_pin = 18
bot_half_pin = 13


count = 1

def main():
    backwall = LEDBackwall_single(bot_half_pin)
    print("inited and starting test")
    try:
        while(True):
            global count
            
            # if count%60 == 0:
            # backwall.set_color_all(c.white)
            backwall.turn_off_all()
            
            print(count)
            # backwall.top_strip.set_segment_color(count%30, c.blue)
            # time.sleep(1)
            # backwall.top_strip.set_segment_color(count%30, c.no_light)

            #backwall.set_color(count%60, c.no_light)
            backwall.set_color((count+1)%60, c.blue)

            backwall.show()
            count+=1
            time.sleep(0.5)


    except KeyboardInterrupt:
        backwall.turn_off_all()
        backwall.show()
        time.sleep(0.1)


if __name__ == '__main__':
    main()