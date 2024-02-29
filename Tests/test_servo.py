from servo import Servo
import time

if __name__ == "__main__":
    servo1 = Servo(pin_number=28)  # Assuming pin 28 is connected to the servo
    try:
        while True:
            # Move servo from 0 to 190 degrees
            for angle in range(0, 190, 10):
                servo1.set_angle(angle)
                print("Current angle:", angle)
                time.sleep(0.2)  # Wait for servo to reach position
            # Move servo from 190 to 0 degrees
            for angle in range(190, -1, -10):
                servo1.set_angle(angle)
                print("Current angle:", angle)
                time.sleep(0.2)  # Wait for servo to reach position
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        servo1.set_angle(0)  # Set servo to 0 degrees before exiting
