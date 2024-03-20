from hardware_s2g import RGB  # Importing the RGB class from your code
import time 



if __name__ == "__main__":

    print("LEDtest")
    ledDoor2 = RGB(10, 11, 12)  # Example pins for RGB LED 1
    ledScanner = RGB(6, 7, 8)    # Example pins for RGB LED 2
    ledDoor1 = RGB(2, 3, 4)       # Example pins for RGB LED 3
        
#   st individual LEDs
    ledDoor1.set_color("white")   # Red

    # For LED Scanner
    ledScanner.set_color("white")   # Red

    # For LED Door 2
    ledDoor2.set_color("white")   # Red

    time.sleep (2) # Wait for 2 seconds

    ledDoor1.off()
    ledScanner.off()
    ledDoor2.off()