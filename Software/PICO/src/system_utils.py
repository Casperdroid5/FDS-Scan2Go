from machine import RTC
import time
import select
import sys


class Log: 
    """
    Log class to log messages to a file.
    """

    def __init__(self, filename="log.txt"):
        """
        Initialize the Log object.

        Args:
            filename (str): The name of the log file.
        """
        self.filename = filename
        self.file = None
        self.rtc = RTC()  # Initialize RTC

    def open_log(self):
        """
        Open the log file.

        Returns:
            None
        """
        self.file = open(self.filename, "a")  # Open the file in append mode

    def log_message(self, message):
        """
        Log a message to the file.

        Args:
            message (str): The message to be logged.

        Returns:
            None
        """
        if self.file:
            timestamp = self.get_timestamp()
            log_entry = f"{timestamp},{message}\n"
            print("Logging:", log_entry)
            self.file.write(log_entry)
            self.file.flush()

    def get_timestamp(self):
        """
        Get the current timestamp.

        Returns:
            str: The current timestamp.
        """
        timestamp = self.rtc.datetime()
        timestring = "%04d-%02d-%02d %02d:%02d:%02d.%03d" % timestamp[:7]
        return timestring

    def close_log(self):
        """
        Close the log file.

        Returns:
            None
        """
        if self.file:
            self.file.close()
            self.file = None


class USBCommunication: 
    """
    USBCommunication class to send and receive messages from the host.
    """

    def __init__(self):
        """
        Initialize the USBCommunication object.
        """
        self.poll_obj = select.poll() # Initialize the poll object for monitoring input from stdin
        self.poll_obj.register(sys.stdin, select.POLLIN)

    def send_message(self, message):
        """
        Send a message.

        Args:
            message (str): The message to be sent.

        Returns:
            None
        """
        prefixed_message = "[USBCommunication] " + message # Add a prefix to the message
        print(prefixed_message)

    def receive_message(self):
        """
        Receive a message.

        Returns:
            str: The received message.
        """
        poll_results = self.poll_obj.poll(1) # Poll for input on stdin for a certain duration
        if poll_results:
            data = sys.stdin.readline().strip() # Read data from stdin
            if data.startswith("[USBCommunication]"): # Check if the message starts with the desired prefix
                return data
        return None  # Return None if no message with the prefix is received


class Timer: 
    """
    Timer class to measure time in ms.
    """

    def __init__(self):
        """
        Initialize the Timer object.
        """
        self.start_time = None  # Start time is set to None initially

    def start_timer(self):
        """
        Start the timer.

        Returns:
            None
        """
        self.start_time = time.ticks_ms()  # Start the timer by storing the current time

    def get_time(self):
        """
        Get the elapsed time.

        Returns:
            int: The elapsed time.
        """
        if self.start_time is None:  # If timer is not started, return 0
            print("Timer not started")
            return 1
        else:
            return time.ticks_ms() - self.start_time  # Return the time difference  

    def reset(self):
        """
        Reset the timer.

        Returns:
            None
        """
        self.start_time = None  # Reset the timer


class ErrorHandler: 
    """
    ErrorHandler class to handle errors.
    """

    def report_error(self, components):
        """
        Report errors.

        Args:
            components (list): The list of components with errors.

        Returns:
            None
        """
        for component in components:
            self.display_error(component)
            Log().open_log() # Open the log file
            Log().log_message(f"Error in component: {component}") # log error potential to a file or send it to a server
            Log().close_log() # Close the log file

    def display_error(self, component):
        """
        Display an error message.

        Args:
            component (str): The component name.

        Returns:
            None
        """
        print(f"Error in component: {component}")


def check_sensors():     
    """
    Check if sensors are connected and working.

    Returns:
        bool: True if sensors are functional, False otherwise.
    """
    _SensorFunctional = True  # for testing purposes this is set to...
    if _SensorFunctional == True:
        print("Sensors are functional")
    return _SensorFunctional


class SystemInitCheck: 
    """
    SystemInitCheck class to perform system initialization checks.
    """

    def __init__(self):
        """
        Initialize the SystemInitCheck object.
        """
        print("System is starting up, running system check")
        failing_components = self.systemcheck()
        if failing_components:
            print("system detected errors, reporting error(s):")
            ErrorHandler().report_error(failing_components)
            raise SystemExit
        else:
            print("system detected NO errors, continuing with startup.")

    def systemcheck(self):
        """
        Perform system checks.

        Returns:
            list: The list of failing components.
        """
        failing_components = [] # List to store failing components
        # Check sensors
        if not check_sensors():
            failing_components.append("Sensors")
        return failing_components # Return the list of failing components
