import serial
import gpiod

# Seriele poortinstellingen
ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1) # Open seriele poort

# GPIO instellingen
LED_PIN = 17
chip = gpiod.Chip('gpiochip0')
led_line = chip.get_line(LED_PIN)
led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)

def toggle_led():
    led_line.set_value(not led_line.get_value())

try:
    while True:
        # Wacht op invoer van de gebruiker
        user_input = input("Voer 'toggle' in om de LED te togglen: ")

        # Verwerk de invoer en stuur deze via UART naar de Raspberry Pi Pico
        ser.write(user_input.encode())
        print("Invoer verzonden naar Pico:", user_input)

        # Wacht op ontvangst van een bevestiging van de Raspberry Pi Pico
        response = ser.readline().decode().strip()
        print("Ontvangen van Pico:", response)

except KeyboardInterrupt:
    print("Programma afgebroken")

finally:
    ser.close()
    led_line.release()
