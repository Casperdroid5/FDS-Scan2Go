from machine import Pin, ADC
import time

# Configure ADC on pin 27
potentiometer = ADC(Pin(27))

while True:
    # Read potentiometer value
    pot_value = potentiometer.read_u16()

    # Convert potentiometer value to a range between 0 and 100
    scaled_value = (pot_value / 65535) * 100

    # Print the scaled value
    print("Potentiometer value:", scaled_value)

    # Wait for a short interval before reading again
    time.sleep(0.1)
