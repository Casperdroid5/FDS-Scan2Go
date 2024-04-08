import machine

class UARTCommunication:
    def __init__(self, uart_number, baudrate, tx_pin, rx_pin):
        self.uart = machine.UART(uart_number, baudrate=baudrate, tx=machine.Pin(tx_pin), rx=machine.Pin(rx_pin))

    def send_message(self, message):
        self.uart.write(message.encode('utf-8'))
        self.uart.flush()
    
    def receive_message(self):
        if self.uart.any():  # Check if there's data available to read
            try:
                message = self.uart.readline()
                decoded_message = message.decode('utf-8')
                return decoded_message.strip()
            except UnicodeError as e:
                print("Unicode decoding error:", e)
                return None
        else:
            return None  # No data available, return None


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

