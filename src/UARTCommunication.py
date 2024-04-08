# UARTCommunication.py

import machine
import time

class UARTCommunication:
    def __init__(self, uart_number, baudrate, tx_pin, rx_pin):
        self.uart = machine.UART(uart_number, baudrate=baudrate, tx=machine.Pin(tx_pin), rx=machine.Pin(rx_pin))

    def send_message(self, message):
        self.uart.write(message.encode())
        self.uart.flush()

    def receive_message(self):
        if self.uart.any():
            return self.uart.readline().decode().strip()
        else:
            return None

    def send_command(self, class_name, message):
        command = f"{class_name}:{message}\n"
        self.send_message(command)
        self.uart.flush()

    def receive_command(self):
        if self.uart.any():
            command = self.uart.readline().decode().strip().split(':')
            if len(command) == 2:
                return command[0], command[1]
            else:
                return None, None
        else:
            return None, None

