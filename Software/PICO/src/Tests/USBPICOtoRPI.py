import machine
import select
import sys
import time

# Configureer de LED-pin
LED_PIN = 25  # Pas dit aan als je een andere pin gebruikt
led = machine.Pin(LED_PIN, machine.Pin.OUT)

# Set up the poll object
poll_obj = select.poll()
poll_obj.register(sys.stdin, select.POLLIN)

# Loop indefinitely
while True:
    # Wacht op invoer op stdin
    poll_results = poll_obj.poll(1)  # de '1' is hoelang het zal wachten op een bericht voordat het opnieuw gaat lussen (in microseconden)
    if poll_results:
        # Lees de data van stdin (lees gegevens die vanaf de pc komen)
        data = sys.stdin.readline().strip()
        
        
        # Controleer of het ontvangen commando overeenkomt met het gewenste commando om de LED in te schakelen
        if data == "on":
            # Schakel de LED in
            led.value(1)
            print("Ontvangen data:", data)
            print("LED ingeschakeld")
        elif data == "off":
            # Schakel de LED uit
            led.value(0)
            print("Ontvangen data:", data)
            print("LED uitgeschakeld")
        
    else:
        continue

