import machine

class UARTCommunication:
    def __init__(self, uart_number, baudrate, tx_pin, rx_pin):
        self.uart = machine.UART(uart_number, baudrate=baudrate, tx=machine.Pin(tx_pin), rx=machine.Pin(rx_pin))

    def receive_command(self):
        if self.uart.any():
            command = self.uart.readline().decode().strip().split(':')  # Splits het ontvangen bericht op ':' om klasse en bericht te scheiden
            if len(command) == 2:
                return command[0], command[1]  # Returnt de klasse en het bericht
            else:
                return None, None
        else:
            return None, None

    def send_command(self, class_name, message):
        command = f"{class_name}:{message}\n"  # Combineert klasse en bericht met ':' als scheidingsteken
        self.uart.write(command.encode())

