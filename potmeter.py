from machine import Pin, ADC

class Potentiometer:
    def __init__(self, pin_number, callback=None):
        self.adc = ADC(Pin(pin_number))
        self.callback = callback

    def read_value(self):
        return self.adc.read_u16()

    def attach_callback(self, callback):
        self.callback = callback

    def detach_callback(self):
        self.callback = None
