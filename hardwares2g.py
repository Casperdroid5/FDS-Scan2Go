from machine import Pin, PWM
from servo import ServoMotor

class RGB:
    def __init__(self, pin_blue, pin_green, pin_red):
        self.pin_red = PWM(Pin(pin_red, Pin.OUT))
        self.pin_green = PWM(Pin(pin_green, Pin.OUT))
        self.pin_blue = PWM(Pin(pin_blue, Pin.OUT))
        self.colors = {
            "red": (65535, 0, 0),
            "green": (0, 65535, 0),
            "blue": (0, 0, 65535),
            "yellow": (65535, 65535, 0),
            "cyan": (0, 65535, 65535),
            "magenta": (65535, 0, 65535),
            "white": (65535, 65535, 65535),
        }

    def set_color(self, color):
        if color.lower() in self.colors:
            red, green, blue = self.colors[color.lower()]
            self.pin_red.duty_u16(red)
            self.pin_green.duty_u16(green)
            self.pin_blue.duty_u16(blue)
        else:
            raise ValueError("Invalid color")

    def on(self):
        self.set_color("white")

    def off(self):
        self.pin_red.duty_u16(0)
        self.pin_green.duty_u16(0)
        self.pin_blue.duty_u16(0)


class Door:
    def __init__(self, pin_number, angle_closed, angle_open):
        self.servo = ServoMotor(Pin(pin_number))
        self.angle_open = angle_open
        self.angle_closed = angle_closed

    def open(self):
        self.servo.set_angle(self.angle_open)

    def close(self):
        self.servo.set_angle(self.angle_closed)
