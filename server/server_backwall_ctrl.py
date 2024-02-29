from backwall import *
import time

top_half_pin = 12
bot_half_pin = 18



def main():
    backwall = LEDBackwall(top_half_pin, bot_half_pin)

    try:
        while(True):
            #listen for message
            #parse message for segment_id and color
            parse_index = "1"
            index = int(parse_index)
            parse_color = "val"
            output_color = c.blue


            if parse_color == "off":
                backwall.turn_off_segment((count-1)%60)
            else:
                match parse_color:
                    case "blue":
                        output_color = c.blue
                    case "red":
                        output_color = c.red
                    case "green":
                        output_color = c.green
                    case "yellow":
                        output_color = c.yellow
                    case "white":
                        output_color = c.white
                    case "violet":
                        output_color = c.violet
                    case _:
                        print("Invalid Color")
                backwall.set_color(index, output_color)


            


    except KeyboardInterrupt:
        backwall.turn_off_all()
        time.sleep(0.1)


if __name__ == '__main__':
    main()