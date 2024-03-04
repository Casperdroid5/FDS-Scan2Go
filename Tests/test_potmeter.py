from potmeter import Potentiometer  # Importing the Potentiometer class from your code
import time

if __name__ == "__main__":
    
    # Create a Potentiometer instance with pin number 27
    potentiometer1 = Potentiometer(pin_number=27)

    # Continuously check the potentiometer value
    while True:
        value = potentiometer1.read_value()  # Read the potentiometer value
        print("Potentiometer value:", value)  # Print the potentiometer value
        time.sleep(0.1)  # Adjust the sleep time as needed
