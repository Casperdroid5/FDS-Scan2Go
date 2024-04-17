import time
import select
import sys

class UARTCommunication:
    def __init__(self):
        self.poll_obj = select.poll()
        self.poll_obj.register(sys.stdin, select.POLLIN)

    def send_message(self, message):
        print(message)

    def receive_message(self):
        poll_results = self.poll_obj.poll(1)  # wait for input on stdin for x seconds
        if poll_results:
            data = sys.stdin.readline().strip() # read data from stdin
            return data

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
