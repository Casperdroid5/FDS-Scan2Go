from machine import Pin, PWM
from time import sleep

class RGB_LED:
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

if __name__ == "__main__":
    # Define the pins for each color of the RGB LEDs
    ledScanner = RGB_LED(12, 13, 14)  # Example pins for RGB LED 1
    ledDoor2 = RGB_LED(20, 19, 18)    # Example pins for RGB LED 2
    ledDoor1 = RGB_LED(2, 3, 4)       # Example pins for RGB LED 3

    print('RGB LED Example')

    try:
        # Test individual LEDs
        ledDoor1.set_color(6000, 0, 0)   # Red
        sleep(2)
        ledDoor1.off()
        sleep(2)
        ledDoor2.set_color(0, 6000, 0)   # Green
        sleep(2)
        ledDoor2.off()
        sleep(2)
        ledScanner.set_color(0, 0, 6000)   # Blue
        sleep(2)
        ledScanner.off()

        # Now, test the scenario where both doors have different colors
        ledDoor1.set_color(6000, 0, 0)   # Red
        sleep(2)
        ledDoor1.off()
        sleep(2)
        ledDoor2.set_color(0, 6000, 0)   # Green
        sleep(2)
        ledDoor2.off()

    except Exception as e:
        print("An error occurred:", e)
