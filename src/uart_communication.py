import machine
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
