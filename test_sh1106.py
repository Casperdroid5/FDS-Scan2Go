from machine import Pin, I2C
import sh1106
import time 
# Define the pins for I2C communication
scl_pin = Pin(1)  # SCL pin
sda_pin = Pin(0)  # SDA pin

# Initialize I2C bus
i2c = I2C(0, scl=scl_pin, sda=sda_pin, freq=400000)

# Create SH1106 display object
display = sh1106.SH1106_I2C(128, 64, i2c, Pin(16), 0x3c, 180)

# Turn off sleep mode
display.sleep(False)

# Clear the display
display.fill(0)

# Display text
display.text('Testing 2', 0, 0, 1)

# Update the display
display.show()

time.sleep (3)

display.fill(0)
# Update the display
display.show()