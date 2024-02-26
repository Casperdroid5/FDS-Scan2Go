from rgbled import RGBLED  # Importing the RGBLED class from your code
import time 



if __name__ == "__main__":

    print("LEDtest")
    ledDoor2 = RGBLED(10, 11, 12)  # Example pins for RGB LED 1
    ledScanner = RGBLED(6, 7, 8)    # Example pins for RGB LED 2
    ledDoor1 = RGBLED(2, 3, 4)       # Example pins for RGB LED 3
        
#   st individual LEDs
    ledDoor1.set_color(6000, 0, 0)   # Red
    time.sleep(0.5)
    ledDoor1.set_color(0, 6000, 0)   # Green
    time.sleep(0.5)
    ledDoor1.set_color(0, 0, 6000)   # Blue
    time.sleep(0.5)

    # For LED Scanner
    ledScanner.set_color(6000, 0, 0)   # Red
    time.sleep(0.5)
    ledScanner.set_color(0, 6000, 0)   # Green
    time.sleep(0.5)
    ledScanner.set_color(0, 0, 6000)   # Blue
    time.sleep(0.5)

    # For LED Door 2
    ledDoor2.set_color(6000, 0, 0)   # Red
    time.sleep(0.5)
    ledDoor2.set_color(0, 6000, 0)   # Green
    time.sleep(0.5)
    ledDoor2.set_color(0, 0, 6000)   # Blue
    time.sleep(0.5)

    ledDoor1.off()
    ledScanner.off()
    ledDoor2.off()