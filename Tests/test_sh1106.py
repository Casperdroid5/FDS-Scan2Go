import sh1106
import time 
from machine import Pin, I2C

# Define the pins for I2C communication
scl_pin, sda_pin = Pin(1), Pin(0)

# Initialize I2C bus
i2c = I2C(0, scl=scl_pin, sda=sda_pin, freq=400000)

# Create SH1106 display object
display = sh1106.SH1106_I2C(128, 64, i2c, Pin(16), 0x3c, 180)
OLEDbrightnesslevel = 100

# Turn off sleep mode, clear the display, and display text
display.sleep(False)
display.fill(0)
display.text('Testing, testing', 0, 0, 1) # (text, x, y, color)
display.text('1,2,3', 0,10,1)
display.contrast(OLEDbrightnesslevel) #brightness 0-255

# Update the display and pause for 3 seconds
display.show()
time.sleep(3)

# Clear the display and update it
display.fill(0)
display.show()

