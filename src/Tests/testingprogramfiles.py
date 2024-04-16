from hardware_s2g import NEWPERSONDETECTOR, WS2812
import time

def test_person_detection_with_leds():
    # Initialisatie van de personendetectors
    mmWaveFieldA = NEWPERSONDETECTOR(uart_number=0, baudrate=256000, tx_pin=0, rx_pin=1)
    mmWaveFieldB = NEWPERSONDETECTOR(uart_number=1, baudrate=256000, tx_pin=4, rx_pin=5)

    # Initialisatie van de LEDs voor elk veld
    led_fieldA = WS2812(pin_number=3, num_leds=2, brightness=0.5)  # LED op pin 2 voor veld A
    led_fieldB = WS2812(pin_number=2, num_leds=2, brightness=0.5)  # LED op pin 3 voor veld B

    while True:  # Voer continu de detectielogica uit voor elk veld
        # Veld A
        # print("Checking for person in field A")
        if mmWaveFieldA.scan_for_people() == True and mmWaveFieldA.get_detection_distance() < 160:
            # print("Person detected in field A")
            led_fieldA.set_color("green")  # Groene LED brandt wanneer een persoon wordt gedetecteerd
        elif mmWaveFieldA.scan_for_people() == False:
            led_fieldA.set_color("red")  # Rode LED brandt wanneer geen persoon wordt gedetecteerd

        # Veld B
        # print("Checking for person in field B")
        if mmWaveFieldB.scan_for_people() == True and mmWaveFieldB.get_detection_distance() < 160:
            # print("Person detected in field B")
            led_fieldB.set_color("green")  # Groene LED brandt wanneer een persoon wordt gedetecteerd
        elif mmWaveFieldB.scan_for_people() == False:
            led_fieldB.set_color("red")  # Rode LED brandt wanneer geen persoon wordt gedetecteerd

        time.sleep(0.1)  # Wacht 1 seconde tussen elke detectiepoging

if __name__ == "__main__":
    test_person_detection_with_leds()
