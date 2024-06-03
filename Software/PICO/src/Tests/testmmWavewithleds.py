from hardware_s2g import SeeedPersonDetector, WS2812
import time

def initialize_person_detector(uart_number, tx_pin, rx_pin):
    return SeeedPersonDetector(uart_number=uart_number, tx_pin=tx_pin, rx_pin=rx_pin)


def initialize_leds(pin_number, num_leds=2, brightness=50):
    return WS2812(pin_number=pin_number, num_leds=num_leds, brightness=brightness)


def check_and_update_led_for_field_A(mmWaveFieldA, led_fieldA):
    #print("Checking for person in field A")
    person_detected_A = mmWaveFieldA.scan_for_people()
    if person_detected_A and mmWaveFieldA.get_detection_distance() < 160:
        print("Person detected in field A")
        led_fieldA.set_color("green")  # Green LED when a person is detected
    else:
        led_fieldA.set_color("red")  # Red LED when no person is detected


def check_and_update_led_for_field_B(mmWaveFieldB, led_fieldB):
    #print("Checking for person in field B")
    person_detected_B = mmWaveFieldB.scan_for_people()
    if person_detected_B and mmWaveFieldB.get_detection_distance() < 160:
        print("Person detected in field B")
        led_fieldB.set_color("green")  # Green LED when a person is detected
    else:
        led_fieldB.set_color("red")  # Red LED when no person is detected

def test_person_detection_with_leds():
    # Initialization of person detectors
    mmWaveFieldA = initialize_person_detector(uart_number=0, tx_pin=0, rx_pin=1)
    mmWaveFieldB = initialize_person_detector(uart_number=1, tx_pin=4, rx_pin=5)

    # Initialization of LEDs for each field
    led_fieldA = initialize_leds(pin_number=3)
    led_fieldB = initialize_leds(pin_number=2)

    while True:  # Continuously execute the detection logic for each field
        check_and_update_led_for_field_A(mmWaveFieldA, led_fieldA)
        check_and_update_led_for_field_B(mmWaveFieldB, led_fieldB)

if __name__ == "__main__":
    # Initialization of person detectors
    mmWaveFieldA = initialize_person_detector(uart_number=0, tx_pin=0, rx_pin=1)
    mmWaveFieldB = initialize_person_detector(uart_number=1, tx_pin=4, rx_pin=5)

    # Initialization of LEDs for each field
    led_fieldA = initialize_leds(pin_number=3)
    led_fieldB = initialize_leds(pin_number=2)

    # Test individual field functions
    while True:
        check_and_update_led_for_field_B(mmWaveFieldB, led_fieldB)
        check_and_update_led_for_field_A(mmWaveFieldA, led_fieldA)




