import time
from machine import Pin, I2C, PWM, ADC
from rgbled import RGBLED
import sh1106

# Global variables for hardware components
ledDoor2Lock = RGBLED(10, 11, 12)
ledDoor1Lock = RGBLED(2, 3, 4)
ledScanner = RGBLED(6, 7, 8)
Door1Motor = Servo(14)
Door2Motor = Servo(15)
Piezo = PWM(16)
FDSResetButton = Pin(5, Pin.IN, Pin.PULL_UP)
EmergencyButton = Pin(9, Pin.IN, Pin.PULL_UP)
FieldA = Pin(18, Pin.IN, Pin.PULL_UP)
FieldB = Pin(17, Pin.IN, Pin.PULL_UP)
Pot1 = ADC(27)

# Define the pins for I2C communication
scl_pin, sda_pin = Pin(1), Pin(0)
# Initialize I2C bus
i2c = I2C(0, scl=scl_pin, sda=sda_pin, freq=400000)
# Create SH1106 display object
display = sh1106.SH1106_I2C(128, 64, i2c, Pin(16), 0x3c, 180)
OLEDbrightnesslevel = 100


# Define the functions corresponding to each state
def initialisation_state():
    display.fill(0)
    display.text("-State: Init-", 0, 0, 1)
    display.show()
    ledDoor2Lock.off() 
    ledDoor1Lock.off() 
    ledScanner.off()   
    Door2Motor.set_angle(90)
    Door1Motor.set_angle(0)    

def wait_for_user_field_a_state():
    display.fill(0)
    display.text("-State: WFieldA-", 0, 0, 1)
    display.show()
    if FieldA.value() == 0 and FieldB.value() == 1: 
        if not PatientReturnedFromMRI:
            return lock_and_close_door1_state()
        else:
            return lock_and_close_door2_state()     

def wait_for_user_field_b_state():
    display.fill(0)
    display.text("-State: WFieldB-", 0, 0, 1)
    display.show()
    if FieldA.value() == 1 and FieldB.value() == 0:
        if not PatientReturnedFromMRI and FerroFree:
            return unlock_and_open_door2_state()
        elif not PatientReturnedFromMRI and not FerroFree:
            return ferrometal_detection_state()
        elif PatientReturnedFromMRI:
            return wait_for_user_field_a_state()    

def ferrometal_detection_state():
    display.fill(0)
    display.text("-State: FerroD-", 0, 0, 1)
    display.show()
    pot_value = Pot1.read_u16()  # Read potentiometer pin
    print("Potentiometer value:", pot_value)
    if 0 <= pot_value < 40000:
        ledScanner.set_color(0, 6000, 0)  # Green    
        FerroFree = True
        time.sleep(1.5)
        return unlock_and_open_door2_state()
    elif 40000 <= pot_value <= 66000:
        ledScanner.set_color(6000, 0, 0)  # Red 
        return unlock_and_open_door1_state()    

def unlock_and_open_door1_state():
    display.fill(0)
    display.text("-State: Open1-", 0, 0, 1)
    display.show()
    time.sleep(2)
    Door1Motor.set_angle(0) # door openend
    ledDoor1Lock.set_color(0, 6000, 0)  # Green - indicating door opened
    ledScanner.off()  #LED OFF
    time.sleep(2) # wait for visual effect
    return wait_for_user_field_a_state()


def lock_and_close_door1_state():
    display.fill(0)
    display.text("-State: Lock1-", 0, 0, 1)
    display.show()
    Door1Motor.set_angle(90)
    ledDoor1Lock.set_color(6000, 0, 0)  # Red - indicating door closed
    return lock_and_close_door2_state()


def unlock_and_open_door2_state():
    display.fill(0)
    display.text("-State: Open2-", 0, 0, 1)
    display.show()
    Door2Motor.set_angle(0) # door openend
    ledDoor2Lock.set_color(0, 6000, 0)  # Green - indicating door opened
    ledScanner.off()  #LED OFF
    time.sleep(2) # wait with closing door for visual effect
    return wait_for_user_field_b_state()

def lock_and_close_door2_state():
    display.fill(0)
    display.text("-State: Lock2-", 0, 0, 1)
    display.show()
    Door2Motor.set_angle(90) # open
    ledDoor2Lock.set_color(6000, 0, 0)  # Red - indicating door closed
    ledScanner.off()  #LED OFF
    if PatientReturnedFromMRI == True:
        PatientReturnedFromMRI = False
        FerroFree = False
        return unlock_and_open_door1_state()
    elif PatientReturnedFromMRI == False:
        return wait_for_user_field_b_state()
    

def emergency_state():
    display.fill(0)
    display.text("-State: Emergency-", 0, 0, 1)
    display.show()
    Door1Motor.set_angle(0)  # Open door 1
    Door2Motor.set_angle(0)  # Open door 2
    ledDoor1Lock.set_color(0, 0, 6000)  # Blue
    ledDoor2Lock.set_color(0, 0, 6000)  # Blue
    ledScanner.set_color(0, 0, 6000)  # Blue
    return None

# Define the state machine
def run():
    state = States.WaitForUserFieldAState

    while True:
        print("Current State:", state.name)

        match state:
            case States.WaitForUserFieldAState:
                if check_userbfield():
                    state = States.WaitForUserFieldBState

            case States.WaitForUserFieldBState:
                update_FerrometalDetectionState()
                state = States.FerrometalDetectionState

            case States.FerrometalDetectionState:
                ferro_handler()
                state = States.WaitForUserFieldBState

            case States.EmergencyState:
                error_handler()
                state = States.InitialisationState
                break  # Exit the loop

        # Implement transitions and actions for other states

        # Handle transitions and actions for other states

main()
    hardware = Hardware()
    machine = StateMachine(hardware)
    machine.start()
    machine.update()
    

if __name__ == "__main__":
    main()

