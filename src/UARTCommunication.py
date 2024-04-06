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

# prefined class names and messages
class_names = {
    "RaspberryPi": "RaspberryPi",
    "System": "System",
}

messages = {
    "initialisation_complete": "Initialisatie voltooid. Systeem gereed voor gebruik.",
    "metal_detected": "Metaal gedetecteerd. Verwijder metalen voorwerpen.",
    "person_detected": "Persoon gedetecteerd in veld",
    "no_person": "Geen persoon gedetecteerd in veld",
    "emergency_button_pressed": "Noodknop ingedrukt. Systeem in noodmodus.",
    "override_button_pressed": "Systeemoverrideknop ingedrukt. Systeemoverride geactiveerd.",
    "system_unfrozen": "Systeem ontgrendeld. Hervat normale werking.",
    "system_frozen": "Systeem vergrendeld. Wacht op verdere instructies.",
    "invalid_state": "Ongeldige systeemstatus gedetecteerd. Noodverzoek aangemaakt.",
    "initialisation_failed": "Initialisatie mislukt. Systeem wordt afgesloten.",
    "unexpected_error": "Onverwachte fout opgetreden in het systeem.",
}
