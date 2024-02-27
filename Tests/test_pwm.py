from pwm import pwm
import time

if __name__ == "__main__":
    led1 = pwm(pin_number=21)  # Assuming pin 21 is connected to the LED
    led1.off()  # Turn the LED off
    time.sleep(1)
    led1.on()  # Turn the LED on
    time.sleep(1)
    led1.set_brightness_percent(50)  # Set the brightness level to 10%
    time.sleep(1)
    led1.set_brightness_percent(10)  # Set the brightness level to 10%
    time.sleep(1)
    led1.off()  # Turn the LED off
