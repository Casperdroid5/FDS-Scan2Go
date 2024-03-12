from machine import Pin, PWM
from servo import ServoMotor
from rgbled import RGBLed
from sh1106 import SH1106_I2C

class rgb(RGBLed):
    def __init__(self, pin_blue, pin_green, pin_red):
        self.pin_red = PWM(Pin(pin_red, Pin.OUT))
        self.pin_green = PWM(Pin(pin_green, Pin.OUT))
        self.pin_blue = PWM(Pin(pin_blue, Pin.OUT))
        
        # Set PWM frequency to 1 kHz
        self.pin_red.freq(1000)
        self.pin_green.freq(1000)
        self.pin_blue.freq(1000)

    def On(self):
        self.pin_red.duty_u16(65535)
        self.pin_green.duty_u16(65535)
        self.pin_blue.duty_u16(65535)

    def Off(self):
        self.pin_red.duty_u16(0)
        self.pin_green.duty_u16(0)
        self.pin_blue.duty_u16(0)

    def Setcolor(self, color):
        colors = {
            "red": (65535, 0, 0),
            "green": (0, 65535, 0),
            "blue": (0, 0, 65535),
            "yellow": (65535, 65535, 0),
            "cyan": (0, 65535, 65535),
            "magenta": (65535, 0, 65535),
            "white": (65535, 65535, 65535),
            "off": (0, 0, 0)
        }
        
        if color.lower() in colors:
            red, green, blue = colors[color.lower()]
            self.pin_red.duty_u16(red)
            self.pin_green.duty_u16(green)
            self.pin_blue.duty_u16(blue)
        else:
            raise ValueError("Invalid color")


class Door(ServoMotor):
    def __init__(self, pin_number, angle_closed, angle_open):
        self.servo = ServoMotor(Pin(pin_number)) 
        self.pin_number = pin_number 
        self.angle_open = angle_open # maximum opening angle
        self.angle_closed = angle_closed # maximum closing angle

    def Open(self): # Open the door
        self.servo.set_angle(self.angle_open)   # 0 is the angle to open the door

    def Close(self): # Close the door
        self.servo.set_angle(self.angle_closed)  # 90 is the angle to close the door

