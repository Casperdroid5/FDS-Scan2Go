from machine import Pin, I2C
import sh1106
import time 

# Define the pins for I2C communication
scl_pin, sda_pin = Pin(1), Pin(0)

# Initialize I2C bus
i2c = I2C(0, scl=scl_pin, sda=sda_pin, freq=400000)

# Create SH1106 display object
display = sh1106.SH1106_I2C(128, 64, i2c, Pin(16), 0x3c, 180)

# Turn off sleep mode, clear the display, and display text
display.sleep(False)
display.fill(0)
display.text('Testing 2', 0, 0, 1)

# Update the display and pause for 3 seconds
display.show()
time.sleep(3)

# Clear the display again and update it
display.fill(0)
display.show()
