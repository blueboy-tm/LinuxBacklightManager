import os


def state(turn: bool)-> None:
    os.popen(f'echo {1 if turn else 0} | tee /sys/devices/platform/tuxedo_keyboard/state').read()


def brightness(value: int)-> None:
    os.popen(f'echo {value} | tee /sys/devices/platform/tuxedo_keyboard/brightness').read()


def get_value(key: str)-> str:
    return os.popen(f'cat /sys/devices/platform/tuxedo_keyboard/{key}').read()


def set_color(key: str, color: str)-> None:
    os.popen(f'echo 0x{color[1:]} | tee /sys/devices/platform/tuxedo_keyboard/color_{key}').read()


