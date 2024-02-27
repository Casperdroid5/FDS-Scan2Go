from machine import Pin, I2C
import time

from button import Button
from potmeter import Potentiometer
from rgbled import RGBLED
from pwm import pwm
from sh1106 import SH1106_I2C



ledDoor2Lock = RGBLED(10, 11, 12) 
ledDoor1Lock = RGBLED(2, 3, 4)     
ledScanner = RGBLED(6, 7, 8)      

ledDoor1Motor = pwm(21) 
ledDoor2Motor = pwm(22) 

Piezo = pwm(16)

Button1 = Button(pin_number=5, callback=None)
Button2 = Button(pin_number=9, callback=None)
Button3 = Button(pin_number=13, callback=None)

Switch1 = Button(pin_number=20, callback=None)
Switch2 = Button(pin_number=19, callback=None)
Switch3 = Button(pin_number=18, callback=None)
Switch4 = Button(pin_number=17, callback=None)

Pot1 = Potentiometer(pin_number=27, callback=None)



scl_pin, sda_pin = Pin(1), Pin(0) # Define the pins for I2C communication
OLEDi2c = I2C(0, scl=scl_pin, sda=sda_pin, freq=400000) # Initialize I2C bus
display = SH1106_I2C(128, 64, OLEDi2c, Pin(16), 0x3c, 180) # Create SH1106 display object

OLEDbrightnesslevel = 100 #brightness 0-255

