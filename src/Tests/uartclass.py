import machine
import time

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

# In je hoofdcode kun je nu een instantie van deze klasse maken voor communicatie
uart_communication = UARTCommunication(uart_number=1, baudrate=9600, tx_pin=4, rx_pin=5)

# Vervolgens kun je de ontvangen commando's controleren en verwerken
try:
    while True:
        class_name, message = uart_communication.receive_command()
        if class_name is not None and message is not None:
            print("Ontvangen commando - Klasse:", class_name, "- Bericht:", message)
            # Voer de benodigde acties uit op basis van de klasse en het bericht

        # Plaats hier de logica om de toestand van de machine te controleren en de relevante commando's te verzenden
        # Bijvoorbeeld:
        # if machine_state == "some_state":
        #     uart_communication.send_command("some_class", "some_message")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Programma afgebroken")
