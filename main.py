from machine import Pin, I2C
import time

from button import Button
from potmeter import Potentiometer
from rgbled import RGBLED
from led import LED
from sh1106 import SH1106_I2C



ledDoor2Lock = RGBLED(10, 11, 12) 
ledScanner = RGBLED(6, 7, 8)      
ledDoor1Lock = RGBLED(2, 3, 4)     

ledDoor1Motor = LED(21) 
ledDoor2Motor = LED(22) 

Button1 = Button(pin_number=5, callback=None)
Button2 = Button(pin_number=9, callback=None)
Button3 = Button(pin_number=13, callback=None)

Pot1 = Potentiometer(pin_number=27, callback=None)

scl_pin, sda_pin = Pin(1), Pin(0) # Define the pins for I2C communication
OLEDi2c = I2C(0, scl=scl_pin, sda=sda_pin, freq=400000) # Initialize I2C bus
display = SH1106_I2C(128, 64, OLEDi2c, Pin(16), 0x3c, 180) # Create SH1106 display object

OLEDbrightnesslevel = 100 #brightness 0-255

