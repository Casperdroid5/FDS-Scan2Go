# system_utils.py
from machine import RTC
import time
import select
import sys

class Log:
    """Log class to log messages to a file."""
    def __init__(self, filename="log.txt"):
        self.filename = filename
        self.file = None
        self.rtc = RTC()

    def open_log(self):
        self.file = open(self.filename, "a")

    def log_message(self, message):
        if self.file:
            timestamp = self.get_timestamp()
            log_entry = f"{timestamp},{message}\n"
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

class USBCommunication:
    """USBCommunication class to send and receive messages from the host."""
    def __init__(self):
        self.poll_obj = select.poll()
        self.poll_obj.register(sys.stdin, select.POLLIN)

    def send_message(self, message):
        prefixed_message = "[USBCommunication] " + message
        print(prefixed_message)

    def receive_message(self):
        poll_results = self.poll_obj.poll(1)
        if poll_results:
            data = sys.stdin.readline().strip()
            if data.startswith("[USBCommunication]"):
                return data
        return None

class Timer:
    """Timer class to measure time in ms."""
    def __init__(self):
        self.start_time = None

    def start_timer(self):
        self.start_time = time.ticks_ms()

    def get_time(self):
        if self.start_time is None:
            return 0
        return time.ticks_ms() - self.start_time

    def reset(self):
        self.start_time = None

class ErrorHandler:
    """ErrorHandler class to handle errors."""
    def report_error(self, components):
        for component in components:
            self.display_error(component)
            log = Log()
            log.open_log()
            log.log_message(f"Error in component: {component}")
            log.close_log()

    def display_error(self, component):
        print(f"Error in component: {component}")

def check_sensors():
    return True

class SystemInitCheck:
    """SystemInitCheck class to perform system initialization checks."""
    def __init__(self):
        failing_components = self.systemcheck()
        if failing_components:
            ErrorHandler().report_error(failing_components)
            raise SystemExit

    def systemcheck(self):
        failing_components = []
        if not check_sensors():
            failing_components.append("Sensors")
        return failing_components
