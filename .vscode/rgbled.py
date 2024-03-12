from machine import Pin, PWM

class RGBLed:
    def __init__(self, pin_blue, pin_green, pin_red):
        self.pin_red = PWM(Pin(pin_red, Pin.OUT))
        self.pin_green = PWM(Pin(pin_green, Pin.OUT))
        self.pin_blue = PWM(Pin(pin_blue, Pin.OUT))
        
        # Set PWM frequency to 1 kHz
        self.pin_red.freq(1000)
        self.pin_green.freq(1000)
        self.pin_blue.freq(1000)

    def on(self):
        self.pin_red.duty_u16(65535)
        self.pin_green.duty_u16(65535)
        self.pin_blue.duty_u16(65535)

    def off(self):
        self.pin_red.duty_u16(0)
        self.pin_green.duty_u16(0)
        self.pin_blue.duty_u16(0)

    def set_color(self, red, green, blue):
        self.pin_red.duty_u16(red)
        self.pin_green.duty_u16(green)
        self.pin_blue.duty_u16(blue)
