from backwall import *
import time

top_half_pin = 13
bot_half_pin = 18


count = 1

def main():
    backwall = LEDBackwall(top_half_pin, bot_half_pin)
    print("inited and starting test")
    try:
        while(True):
            global count
            
            print(count)
            # backwall.top_strip.set_segment_color(count%30, c.blue)
            # time.sleep(1)
            # backwall.top_strip.set_segment_color(count%30, c.no_light)

            backwall.set_color(count%60, c.blue)
            time.sleep(0.1)
            backwall.turn_off_segment(count%60)
            count+=1


    except KeyboardInterrupt:
        backwall.turn_off_all()
        time.sleep(0.1)


if __name__ == '__main__':
    main()