from machine import RTC
import time
import select
import sys


class Log: # Log class to log messages to a file
    def __init__(self, filename="log.txt"):
        self.filename = filename
        self.file = None
        self.rtc = RTC()  # Initialize RTC

    def open_log(self):
        self.file = open(self.filename, "a")  # Open the file in append mode

    def log_message(self, message):
        if self.file:
            timestamp = self.get_timestamp()
            log_entry = f"{timestamp},{message}\n"
            print("Logging:", log_entry)
            self.file.write(log_entry)
            self.file.flush()

    def get_timestamp(self):
        timestamp = self.rtc.datetime()
        timestring = "%04d-%02d-%02d %02d:%02d:%02d.%03d" % timestamp[:7]
        return timestring

    def close_log(self):
        if self.file:
            self.file.close()
            self.file = None

class USBCommunication: # USBCommunication class to send and receive messages from the host
    def __init__(self):
        self.poll_obj = select.poll() # Initialize the poll object for monitoring input from stdin
        self.poll_obj.register(sys.stdin, select.POLLIN)

    def send_message(self, message):
        prefixed_message = "[USBCommunication] " + message # Add a prefix to the message
        print(prefixed_message)

    def receive_message(self):
        poll_results = self.poll_obj.poll(1) # Poll for input on stdin for a certain duration
        if poll_results:
            data = sys.stdin.readline().strip() # Read data from stdin
            if data.startswith("[USBCommunication]"): # Check if the message starts with the desired prefix
                return data
        return None  # Return None if no message with the prefix is received

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
            Log().log_message(f"Error in component: {component}") # log error potential to a file or send it to a server

    def display_error(self, component):
        print(f"Error in component: {component}")

def check_sensors():     # Check if sensors are connected and working
    _SensorFunctional = True  # for testing purposes this is set to...
    if _SensorFunctional == True:
        print("Sensors are functional")
    return _SensorFunctional

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
