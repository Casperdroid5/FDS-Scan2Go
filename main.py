#Todo:
    # altijd iets returnen bij een functie
    # functies zo klein mogelijk houden 1 functie = 1 taak
    # geen print statements in de functies
    # geen global variables gebruiken
    # geen while True gebruiken
    # time sleep vermijden
    # klasses gebruiken voor hardware
    # Alles functioneel, dus geen waardes in de code
    


import sh1106
from machine import Pin, I2C, PWM, ADC
from servo import ServoMotor
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

# Display function
def display_state_info(state_info):
    display.fill(0)
    display.text(state_info, 0, 0, 1)
    display.show()

# State functions
def initialisation_state(led_door2_lock, led_door1_lock, door2_motor, door1_motor):
    display_state_info("-State: Init-")
    door2_motor.set_angle(90)
    door1_motor.set_angle(0)
    return WAIT_FOR_USER_FIELD_A_STATE

def wait_for_user_field_a_state(field_a, field_b, patient_returned_from_mri, led_door1_lock, door1_motor):
    display_state_info("-State: WFieldA-")
    if field_a.value() == 0 and field_b.value() == 1:
        return LOCK_AND_CLOSE_DOOR1_STATE if not patient_returned_from_mri else WAIT_FOR_USER_FIELD_B_STATE
    return WAIT_FOR_USER_FIELD_A_STATE

def wait_for_user_field_b_state(field_a, field_b, patient_returned_from_mri, ferro_free, led_door2_lock, door2_motor):
    display_state_info("-State: WFieldB-")
    if field_a.value() == 1 and field_b.value() == 0:
        if not patient_returned_from_mri and ferro_free:
            return UNLOCK_AND_OPEN_DOOR2_STATE
        elif not patient_returned_from_mri and not ferro_free:
            return FERROMETAL_DETECTION_STATE
        elif patient_returned_from_mri:
            return WAIT_FOR_USER_FIELD_A_STATE

def ferrometal_detection_state(pot1_value, ferro_free, led_scanner):
    display_state_info("-State: FerroD-")
    if 0 <= pot1_value < 40000:
        led_scanner.set_color(0, 6000, 0)  # Green    
        ferro_free = True
        return UNLOCK_AND_OPEN_DOOR2_STATE
    elif 40000 <= pot1_value <= 66000:
        led_scanner.set_color(6000, 0, 0)  # Red 
        return UNLOCK_AND_OPEN_DOOR1_STATE

def unlock_and_open_door1_state(led_door1_lock, door1_motor):
    display_state_info("-State: Open1-")
    door1_motor.set_angle(0)
    led_door1_lock.set_color(0, 6000, 0)
    return WAIT_FOR_USER_FIELD_A_STATE

def lock_and_close_door1_state(led_door1_lock, door1_motor):
    display_state_info("-State: Lock1-")
    door1_motor.set_angle(90)
    led_door1_lock.set_color(6000, 0, 0)
    return LOCK_AND_CLOSE_DOOR2_STATE

def unlock_and_open_door2_state(led_door2_lock, door2_motor):
    display_state_info("-State: Open2-")
    door2_motor.set_angle(0)
    led_door2_lock.set_color(0, 6000, 0)
    return WAIT_FOR_USER_FIELD_B_STATE

def lock_and_close_door2_state(led_door2_lock, door2_motor, patient_returned_from_mri, ferro_free):
    display_state_info("-State: Lock2-")
    door2_motor.set_angle(90)
    led_door2_lock.set_color(6000, 0, 0)
    if patient_returned_from_mri:
        patient_returned_from_mri = False
        ferro_free = False
        return UNLOCK_AND_OPEN_DOOR1_STATE
    else:
        return WAIT_FOR_USER_FIELD_B_STATE

def emergency_state(led_door1_lock, led_door2_lock, led_scanner, door1_motor, door2_motor):
    display_state_info("-State: Emergency-")
    hw.door1.open()
    door1_motor.set_angle(0)
    door2_motor.set_angle(0)
    led_door1_lock.set_color(0, 0, 6000)
    led_door2_lock.set_color(0, 0, 6000)
    led_scanner.set_color(0, 0, 6000)

class Door()
    set_open()
        set_color(0, 0, 6000)
    

class hw:
    init():
        self.door1=Door()
        self.door2=Door()
        self.door3=Door()

# Main function
def run():
    # Hardware components initialization
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
    
    state = initialisation_state(led_door2_lock, led_door1_lock, door2_motor, door1_motor)

    while True:
        field_a_value = field_a.value()
        field_b_value = field_b.value()
        pot1_value = pot1.read_u16()

        if state == WAIT_FOR_USER_FIELD_A_STATE:
            state = wait_for_user_field_a_state(field_a, field_b, patient_returned_from_mri, led_door1_lock, door1_motor)

        elif state == WAIT_FOR_USER_FIELD_B_STATE:
            state = wait_for_user_field_b_state(field_a, field_b, patient_returned_from_mri, ferro_free, led_door2_lock, door2_motor)

        elif state == FERROMETAL_DETECTION_STATE:
            state = ferrometal_detection_state(pot1_value, ferro_free, led_scanner)

        elif state == UNLOCK_AND_OPEN_DOOR1_STATE:
            state = unlock_and_open_door1_state(led_door1_lock, door1_motor)

        elif state == LOCK_AND_CLOSE_DOOR1_STATE:
            state = lock_and_close_door1_state(led_door1_lock, door1_motor)

        elif state == UNLOCK_AND_OPEN_DOOR2_STATE:
            state = unlock_and_open_door2_state(led_door2_lock, door2_motor)

        elif state == LOCK_AND_CLOSE_DOOR2_STATE:
            state = lock_and_close_door2_state(led_door2_lock, door2_motor, patient_returned_from_mri, ferro_free)

        elif state == EMERGENCY_STATE:
            emergency_state(led_door1_lock, led_door2_lock, led_scanner, door1_motor, door2_motor)
            break  # Exit the loop

        else:
            print("Invalid state")
            state = INITIALISATION_STATE

if __name__ == "__main__":
    run()
