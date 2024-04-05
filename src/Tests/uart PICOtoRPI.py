import machine
import time

# UART instellingen
uart = machine.UART(1, baudrate=9600, tx=machine.Pin(4), rx=machine.Pin(5)) # uart 1 on gpio pin 4 and 5 of pico

try:
    while True:
        # Wacht op ontvangst van een bericht van de Raspberry Pi
        if uart.any():
            received_data = uart.readline().decode().strip()
            print("Ontvangen van Raspberry Pi:", received_data)

            # Verwerk het ontvangen bericht en stuur een reactie terug
            response = "Hello Raspberry Pi!"
            uart.write(response.encode())
            print("Verzonden naar Raspberry Pi:", response)

        time.sleep(1)  # Wacht 1 seconde voordat het volgende bericht wordt verwerkt

except KeyboardInterrupt:
    print("Programma afgebroken")

