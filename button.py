from machine import Pin


class Button:
    def __init__(self, pin_number, callback=None):
        self.pin = Pin(pin_number, Pin.IN, Pin.PULL_UP)
        self.callback = callback
        self.pin.irq(trigger=Pin.IRQ_FALLING, handler=self._button_pressed)

    def _button_pressed(self, pin):
        if self.callback:
            self.callback()

    def is_pressed(self):
        return self.pin.value() == 0

    def attach_callback(self, callback):
        self.callback = callback

    def detach_callback(self):
        self.callback = None

