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


# Define a simple callback function for testing
def test_callback():
    print("Button pressed!")

def main():
    # Create a Button instance with pin number 10 and the test_callback as the callback function
    button = Button(pin_number=5, callback=test_callback)

    # Simulate button press
    print("Is button pressed?", button.is_pressed())

    # Detach callback
    button.detach_callback()

    # Simulate button press after detaching callback
    print("Is button pressed?", button.is_pressed())

    # Attach callback again
    button.attach_callback(test_callback)

    # Simulate button press after attaching callback again
    print("Is button pressed?", button.is_pressed())


if __name__ == "__main__":
    main()
