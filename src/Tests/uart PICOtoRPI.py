import machine
import time

# UART instellingen
uart = machine.UART(1, baudrate=9600, tx=machine.Pin(4), rx=machine.Pin(5))

# LED instellingen
led = machine.Pin(25, machine.Pin.OUT)

def toggle_led():
    led.value(not led.value())

try:
    while True:
        # Wacht op ontvangst van een bericht van de Raspberry Pi 5
        if uart.any():
            received_data = uart.readline().decode().strip()
            print("Ontvangen van Raspberry Pi:", received_data)

            # Verwerk het ontvangen bericht en toggle de LED indien nodig
            if received_data == "toggle":
                toggle_led()
                print("LED getoggled")

        time.sleep(0.1)  # Korte wachttijd om de CPU niet te zwaar te belasten

except KeyboardInterrupt:
    print("Programma afgebroken")

