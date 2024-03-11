from machine import *
from servo import ServoMotor
from rgbled import RGBLED
from sh1106 import SH1106_I2C

class rgb(RGBLED):
    
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
    def __init__(self, pin_number):
        self.pin_number = pin_number

    
    def Open(self): # Open the door
        self.servo = ServoMotor(Pin)
        self.servo.set_angle(0)   
        
    def Close(self):
        self.servo = ServoMotor(Pin)
        self.servo.set_angle(90)


class Display(SH1106_I2C):

    def __init__(self, width, height, i2c, reset, addr, contrast):
        self.display = SH1106_I2C(width, height, i2c, reset, addr, contrast)
        self.display_brightness_level = 100

    def DisplayStateInfo(self, state_info):
        self.display.fill(0)
        self.display.text(state_info, 0, 0, 1)
        self.display.show()

