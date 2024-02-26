from button import Button  # Importing the Button class from your code
import time
# Define a simple callback function for testing


if __name__ == "__main__":

    def pressed_callback():
        print("Button pressed!")

    def notpressed_callback():
        print("Button not pressed")
    # Create a Button instance with pin number 5 and the pressed_callback as the callback function
    button = Button(pin_number=5, callback=pressed_callback)

    # Continuously check the button state
import time

while True:  # You need a colon after `while 1` and `while True`
    if button.is_pressed():
        pressed_callback()  # Call the callback function
        # Add a small delay to avoid high CPU usage
        time.sleep(0.1)  # Adjust the sleep time as needed for debounce measurement
    else:
        notpressed_callback()
        time.sleep(1)  # Adjust the sleep time as needed for debounce measurement

        