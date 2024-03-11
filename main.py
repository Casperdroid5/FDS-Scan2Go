#Todo:
    # altijd iets returnen bij een functie
    # functies zo klein mogelijk houden 1 functie = 1 taak
    # geen print statements in de functies
    # geen global variables gebruiken
    # geen while True gebruiken
    # time sleep vermijden
import time
import sh1106
from machine import Pin, I2C, PWM, ADC
from servo import Servo
from rgbled import RGBLED

# Initialize I2C bus
scl_pin, sda_pin = Pin(1), Pin(0)
i2c = I2C(0, scl=scl_pin, sda=sda_pin, freq=400000)

# Create SH1106 display object
display = sh1106.SH1106_I2C(128, 64, i2c, Pin(16), 0x3c, 180)
display_brightness_level = 100

# Define integer constants for states
INITIALISATION_STATE = 0
WAIT_FOR_USER_FIELD_A_STATE = 1
WAIT_FOR_USER_FIELD_B_STATE = 2
FERROMETAL_DETECTION_STATE = 3
UNLOCK_AND_OPEN_DOOR1_STATE = 4
LOCK_AND_CLOSE_DOOR1_STATE = 5
UNLOCK_AND_OPEN_DOOR2_STATE = 6
LOCK_AND_CLOSE_DOOR2_STATE = 7
EMERGENCY_STATE = 8

# Global variables for state tracking
ferro_free = False
patient_returned_from_mri = False

# Global variables for hardware components
led_door2_lock = RGBLED(10, 11, 12)
led_door1_lock = RGBLED(2, 3, 4)
led_scanner = RGBLED(6, 7, 8)
door1_motor = Servo(14)
door2_motor = Servo(15)
piezo = PWM(16)
fds_reset_button = Pin(5, Pin.IN, Pin.PULL_UP)
emergency_button = Pin(9, Pin.IN, Pin.PULL_UP)
field_a = Pin(18, Pin.IN, Pin.PULL_UP)
field_b = Pin(17, Pin.IN, Pin.PULL_UP)
pot1 = ADC(27)

# Display function
def display_state_info(state_info):
    display.fill(0)
    display.text(state_info, 0, 0, 1)
    display.show()

# Define the functions corresponding to each state
def initialisation_state():
    display_state_info("-State: Init-")
    led_door2_lock.off()
    led_door1_lock.off()
    led_scanner.off()
    door2_motor.set_angle(90)
    door1_motor.set_angle(0)
    return WAIT_FOR_USER_FIELD_A_STATE

def wait_for_user_field_a_state():
    display_state_info("-State: WFieldA-")
    if field_a.value() == 0 and field_b.value() == 1:
        if not patient_returned_from_mri:
            return lock_and_close_door1_state()
        else:
            return WAIT_FOR_USER_FIELD_B_STATE
    return WAIT_FOR_USER_FIELD_A_STATE

def wait_for_user_field_b_state():
    display_state_info("-State: WFieldB-")
    if field_a.value() == 1 and field_b.value() == 0:
        if not patient_returned_from_mri and ferro_free:
            return unlock_and_open_door2_state()
        elif not patient_returned_from_mri and not ferro_free:
            return ferrometal_detection_state()
        elif patient_returned_from_mri:
            return WAIT_FOR_USER_FIELD_A_STATE

def ferrometal_detection_state():
    display_state_info("-State: FerroD-")
    pot_value = pot1.read_u16()
    print("Potentiometer value:", pot_value)
    if 0 <= pot_value < 40000:
        led_scanner.set_color(0, 6000, 0)  # Green    
        ferro_free = True
        time.sleep(1.5)
        return UNLOCK_AND_OPEN_DOOR2_STATE
    elif 40000 <= pot_value <= 66000:
        led_scanner.set_color(6000, 0, 0)  # Red 
        return UNLOCK_AND_OPEN_DOOR1_STATE

def unlock_and_open_door1_state():
    display_state_info("-State: Open1-")
    time.sleep(2)
    door1_motor.set_angle(0)
    led_door1_lock.set_color(0, 6000, 0)
    led_scanner.off()
    time.sleep(2)
    return WAIT_FOR_USER_FIELD_A_STATE

def lock_and_close_door1_state():
    display_state_info("-State: Lock1-")
    door1_motor.set_angle(90)
    led_door1_lock.set_color(6000, 0, 0)
    return LOCK_AND_CLOSE_DOOR2_STATE

def unlock_and_open_door2_state():
    display_state_info("-State: Open2-")
    door2_motor.set_angle(0)
    led_door2_lock.set_color(0, 6000, 0)
    led_scanner.off()
    time.sleep(2)
    return WAIT_FOR_USER_FIELD_B_STATE

def lock_and_close_door2_state():
    display_state_info("-State: Lock2-")
    door2_motor.set_angle(90)
    led_door2_lock.set_color(6000, 0, 0)
    if patient_returned_from_mri:
        patient_returned_from_mri = False
        ferro_free = False
        return unlock_and_open_door1_state()
    elif not patient_returned_from_mri:
        return WAIT_FOR_USER_FIELD_B_STATE

def emergency_state():
    display_state_info("-State: Emergency-")
    door1_motor.set_angle(0)
    door2_motor.set_angle(0)
    led_door1_lock.set_color(0, 0, 6000)
    led_door2_lock.set_color(0, 0, 6000)
    led_scanner.set_color(0, 0, 6000)

# Define the state machine
def run():
    state = initialisation_state()

    while True:
        print("Current State:", state)

        if state == WAIT_FOR_USER_FIELD_A_STATE:
            state = wait_for_user_field_a_state()

        elif state == WAIT_FOR_USER_FIELD_B_STATE:
            state = wait_for_user_field_b_state()

        elif state == FERROMETAL_DETECTION_STATE:
            state = ferrometal_detection_state()

        elif state == UNLOCK_AND_OPEN_DOOR1_STATE:
            state = unlock_and_open_door1_state()

        elif state == LOCK_AND_CLOSE_DOOR1_STATE:
            state = lock_and_close_door1_state()

        elif state == UNLOCK_AND_OPEN_DOOR2_STATE:
            state = unlock_and_open_door2_state()

        elif state == LOCK_AND_CLOSE_DOOR2_STATE:
            state = lock_and_close_door2_state()

        elif state == EMERGENCY_STATE:
            emergency_state()
            break  # Exit the loop

        else:
            print("Invalid state")
            state = INITIALISATION_STATE

# Main function
def main():
    run()

if __name__ == "__main__":
    main()
