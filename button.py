from machine import Pin

class Button:
    def __init__(self, pin_number):
        self.pin = Pin(pin_number, Pin.IN, Pin.PULL_UP)

    def is_pressed(self):
        # Returns True if the button is pressed (active low)
        return self.pin.value() == 0

    def is_not_pressed(self):
        # Returns True if the button is not pressed
        return self.pin.value() == 1
