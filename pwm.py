from machine import Pin, PWM

class pwm:
    def __init__(self, pin_number):
        self.pin = PWM(Pin(pin_number, Pin.OUT))
        self.pin.freq(1000)  # Set PWM frequency to 1 kHz
        self.max_duty = 65535  # Maximum duty cycle

    def on(self):
        self.pin.duty_u16(self.max_duty)  # Set duty cycle to maximum to turn the LED on

    def off(self):
        self.pin.duty_u16(0)  # Set duty cycle to 0 to turn the LED off

    def set_brightness_percent(self, percent):
        # Set brightness level as a percentage (0 to 100)
        brightness = int(percent / 100 * self.max_duty)
        self.pin.duty_u16(brightness)
