import machine

class UARTCommunication:
    def __init__(self, uart_number, baudrate, tx_pin, rx_pin):
        self.uart = machine.UART(uart_number, baudrate=baudrate, tx=machine.Pin(tx_pin), rx=machine.Pin(rx_pin))

    def send_message(self, message):
        self.uart.write(message.encode('utf-8'))
        self.uart.flush()

    def receive_message(self):
        if self.uart.any():  # Check if there's data available to read
            message = self.uart.readline()
            return message
        return None  # No data available, return None
