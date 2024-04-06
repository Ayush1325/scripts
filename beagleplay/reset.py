import gpiod
import time

def reset_gpio():
    reset_find = gpiod.find_line("CC1352P7_RSTN")
    return (reset_find.get_chip().name, int(reset_find.offset))

if __name__ == "__main__":
    gpio_pins = reset_gpio()

    reset_chip = gpiod.chip(gpio_pins[0], gpiod.chip.OPEN_BY_NAME)
    reset_line = reset_chip.get_line(gpio_pins[1])

    reset_cfg = gpiod.line_request()
    reset_cfg.consumer="cc1352-flasher"
    reset_cfg.request_type=gpiod.line_request.DIRECTION_OUTPUT
    reset_line.request(reset_cfg)

    reset_line.set_value(0)
    time.sleep(0.2)
    reset_line.set_value(1)
    time.sleep(0.2)
    reset_line.set_direction_input()
    reset_line.release()
