import unittest
from time import sleep
from RGBLED import RGBLED  # Assuming RGBLED class is in RGBLED.py

class TestRGBLED(unittest.TestCase):
    def test_led_sequence(self):
        # Create instances of RGBLED for each LED
        ledDoor1 = RGBLED(2, 3, 4)
        ledScanner = RGBLED(6, 7, 8)
        ledDoor2 = RGBLED(10, 11, 12)

        print("LEDtest")

        # Test individual LEDs
        ledDoor1.set_color(6000, 0, 0)   # Red
        sleep(0.5)
        ledDoor1.set_color(0, 6000, 0)   # Green
        sleep(0.5)
        ledDoor1.set_color(0, 0, 6000)   # Blue
        sleep(0.5)

        ledScanner.set_color(6000, 0, 0)   # Red
        sleep(0.5)
        ledScanner.set_color(0, 6000, 0)   # Green
        sleep(0.5)
        ledScanner.set_color(0, 0, 6000)   # Blue
        sleep(0.5)

        ledDoor2.set_color(6000, 0, 0)   # Red
        sleep(0.5)
        ledDoor2.set_color(0, 6000, 0)   # Green
        sleep(0.5)
        ledDoor2.set_color(0, 0, 6000)   # Blue
        sleep(0.5)

        # Turn off all LEDs
        ledDoor1.off()
        ledScanner.off()
        ledDoor2.off()

if __name__ == '__main__':
    unittest.main()
