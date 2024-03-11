from servo import ServoMotor
import time

if __name__ == "__main__":
    servo1 = ServoMotor(pin_number=26)  # Assuming pin 28 is connected to the servo
    
    # Move to initial positions gradually
    servo1.set_angle(0)  # Set the initial position as 0

    print("Current angle:", servo1.get_current_angle())  # Print initial angle
    time.sleep(0.5)
    servo1.set_angle(90)  # Move to angle 90
    print("Current angle:", servo1.get_current_angle())  # Print angle after movement
    time.sleep(0.5)
    servo1.set_angle(180)  # Move to angle 180
    print("Current angle:", servo1.get_current_angle())  # Print angle after movement
    time.sleep(1)
    
    try:
        while True:
            # Move servo from 0 to 180 degrees
            for angle in range(0, 181, 10):
                servo1.set_angle(angle)
                print("Current angle:", servo1.get_current_angle())
                time.sleep(0.2)  # Wait for servo to reach position
            # Move servo from 180 to 0 degrees
            for angle in range(180, -1, -10):
                servo1.set_angle(angle)
                print("Current angle:", servo1.get_current_angle())
                time.sleep(0.2)  # Wait for servo to reach position
                
                
            print("Current angle:", servo1.get_current_angle())  # Print initial angle
            time.sleep(0.5)
            servo1.set_angle(120)  # Move to angle 90
            print("Current angle:", servo1.get_current_angle())  # Print angle after movement
            time.sleep(0.5)
            servo1.set_angle(160)  # Move to angle 180
            print("Current angle:", servo1.get_current_angle())  # Print angle after movement
            time.sleep(1)
            servo1.set_angle(20)  # Move to angle 180
            print("Current angle:", servo1.get_current_angle())  # Print angle after movement
            time.sleep(1)         
              
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        servo1.set_angle(0)  # Set servo to 0 degrees before exiting
