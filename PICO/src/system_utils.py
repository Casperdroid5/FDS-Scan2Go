import os
import time
import select
import sys


class USBCommunication:
    def __init__(self):
        self.poll_obj = select.poll() # Initialize the poll object for monitoring input from stdin
        self.poll_obj.register(sys.stdin, select.POLLIN)

    def send_message(self, message):
        prefixed_message = "[USBCommunication] " + message # Add a prefix to the message
        print(prefixed_message)
        if prefixed_message.startswith("[USBCommunication] showimage"):
            # Extract the image number from the message
            image_number = prefixed_message.split(" ")[-1]
            # Construct the image file path
            image_path = f"{image_number}.png"
            # Open the image
            self.open_image(image_path)
        elif prefixed_message == "[USBCommunication] closeimage":
            # Close the image
            self.close_image()

    def receive_message(self):
        poll_results = self.poll_obj.poll(1) # Poll for input on stdin for a certain duration
        if poll_results:
            data = sys.stdin.readline().strip() # Read data from stdin
            if data.startswith("[USBCommunication]"): # Check if the message starts with the desired prefix
                return data
        return None  # Return None if no message with the prefix is received

    def open_image(self, image_path):
        if os.path.exists(image_path):
            print(f"Opening image: {image_path}")
            os.system(f"feh {image_path} &")  # Open the image using feh in the background
        else:
            print("Image file not found:", image_path)

    def close_image(self):
        os.system("pkill feh")  # Close all instances of feh

class Timer: # Timer class to measure time in ms
    def __init__(self):
        self.start_time = None  # Start time is set to None initially

    def start_timer(self):
        self.start_time = time.ticks_ms()  # Start the timer by storing the current time

    def get_time(self):
        if self.start_time is None:  # If timer is not started, return 0
            print("Timer not started")
            return 1
        else:
            return time.ticks_ms() - self.start_time  # Return the time difference  

    def reset(self):
        self.start_time = None  # Reset the timer


class ErrorHandler:
    def report_error(self, components):
        for component in components:
            self.display_error(component)
            # log error potential to a file or send it to a server

    def display_error(self, component):
        print(f"Error in component: {component}")

def check_sensors():
    # Check if sensors are connected and working
    _SensorFunctional = True  # for testing purposes this is set to...
    return _SensorFunctional

def check_mmWave():
    # Check if mmWave sensors are connected and working
    _mmWaveFunctional = True  # for testing purposes this is set to...
    return _mmWaveFunctional

class SystemInitCheck:
    def __init__(self):
        print("System is starting up, running system check")
        failing_components = self.systemcheck()
        if failing_components:
            print("failed system check, reporting error(s):")
            ErrorHandler().report_error(failing_components)
            print("System check failed, exiting.")
            raise SystemExit
        else:
            print("System check passed, continuing with startup.")

    def systemcheck(self):
        failing_components = [] # List to store failing components
        # Check sensors
        if not check_sensors():
            failing_components.append("Sensors")
        return failing_components # Return the list of failing components
