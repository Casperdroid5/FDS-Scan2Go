
from PERSONDETECTOR import PERSONDETECTOR

# Definieer callbackfuncties
def on_person_detected(message):
    print("Person detected:", message)

def on_person_not_detected(message):
    print("Person not detected:", message)

if __name__ == "__main__":
    # Definieer UART-configuratie
    uart_config = (1, 9600, (tx_pin, rx_pin))  # Vul de juiste UART-pinnummers in

    # Maak een instantie van PERSONDETECTOR
    person_detector = PERSONDETECTOR(uart_config, on_person_detected, on_person_not_detected)

    # Start de detectie
    person_detector.start_detection()
