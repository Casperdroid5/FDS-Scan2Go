from potmeter import Potentiometer  # Importing the Potentiometer class from your code
import time

if __name__ == "__main__":
    
# Define a simple callback function for testing
    def value_changed_callback(value):
        print("Potentiometer value changed to:", value)

    
    # Create a Potentiometer instance with pin number 28 and the value_changed_callback as the callback function
    potentiometer = Potentiometer(pin_number=27, callback=value_changed_callback)

    # Continuously check the potentiometer value
    while True:
        value = potentiometer.read_value()  # Read the potentiometer value
        value_changed_callback(value)  # Call the callback function with the value
        # Add a small delay to avoid high CPU usage
        time.sleep(0.1)  # Adjust the sleep time as needed
