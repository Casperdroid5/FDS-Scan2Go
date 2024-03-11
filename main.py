import time
import sh1106
from machine import Pin, I2C, PWM, ADC
from servo import Servo
from rgbled import RGBLED

FerroFree = False
PatientReturnedFromMRI = False

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


def WaitForUserFieldAState(): 
    display.fill(0)
    display.text("-State: WFieldA-", 0, 0, 1)
    display.show()
    if FieldA.value() == 0 and FieldB.value() == 1: 
        if not PatientReturnedFromMRI:
            return True
        else:
            return False     


def WaitForUserFieldBState():
    display.fill(0)
    display.text("-State: WFieldB-", 0, 0, 1)
    display.show()
    if FieldA.value() == 1 and FieldB.value() == 0:
        if not PatientReturnedFromMRI and FerroFree:
            return UnlockAndOpenDoor2State()
        elif not PatientReturnedFromMRI and not FerroFree:
            return FerrometalDetectionState()
        elif PatientReturnedFromMRI:
            return WaitForUserFieldAState()    


def FerrometalDetectionState():
    display.fill(0)
    display.text("-State: FerroD-", 0, 0, 1)
    display.show()
    pot_value = Pot1.read_u16()  # Read potentiometer pin
    print("Potentiometer value:", pot_value)
    if 0 <= pot_value < 40000:
        ledScanner.set_color(0, 6000, 0)  # Green    
        FerroFree = True
        time.sleep(1.5)
        return UnlockAndOpenDoor2State()
    elif 40000 <= pot_value <= 66000:
        ledScanner.set_color(6000, 0, 0)  # Red 
        return UnlockAndOpenDoor1State()    


def UnlockAndOpenDoor1State():
    display.fill(0)
    display.text("-State: Open1-", 0, 0, 1)
    display.show()
    time.sleep(2)
    Door1Motor.set_angle(0) # door openend
    ledDoor1Lock.set_color(0, 6000, 0)  # Green - indicating door opened
    ledScanner.off()  #LED OFF
    time.sleep(2) # wait for visual effect
    return WaitForUserFieldAState()


def LockAndCloseDoor1State():
    display.fill(0)
    display.text("-State: Lock1-", 0, 0, 1)
    display.show()
    Door1Motor.set_angle(90)
    ledDoor1Lock.set_color(6000, 0, 0)  # Red - indicating door closed
    return LockAndCloseDoor2State()


def UnlockAndOpenDoor2State():
    display.fill(0)
    display.text("-State: Open2-", 0, 0, 1)
    display.show()
    Door2Motor.set_angle(0) # door openend
    ledDoor2Lock.set_color(0, 6000, 0)  # Green - indicating door opened
    ledScanner.off()  #LED OFF
    time.sleep(2) # wait with closing door for visual effect
    return WaitForUserFieldBState()


def LockAndCloseDoor2State():
    global PatientReturnedFromMRI
    global FerroFree
    
    display.fill(0)
    display.text("-State: Lock2-", 0, 0, 1)
    display.show()
    Door2Motor.set_angle(90) # open
    ledDoor2Lock.set_color(6000, 0, 0)  # Red - indicating door closed
    ledScanner.off()  #LED OFF
    if PatientReturnedFromMRI == True:
        PatientReturnedFromMRI = False # set flag to false
        FerroFree = False # set flag to false   
        return UnlockAndOpenDoor1State()
    elif PatientReturnedFromMRI == False:
        return WaitForUserFieldBState()


def EmergencyState():
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
    state = WaitForUserFieldAState

    while True:
        print("Current State:", state)

        if state == WaitForUserFieldAState:
            WaitForUserFieldAState()
            state = WaitForUserFieldBState

        elif state == WaitForUserFieldBState:
            FerrometalDetectionState()
            state = FerrometalDetectionState

        elif state == FerrometalDetectionState:
            FerrometalDetectionState()
            state = WaitForUserFieldBState

        elif state == EmergencyState:
            EmergencyState()
            state = InitialisationState
            break  # Exit the loop

        # Implement transitions and actions for other states

        # Handle transitions and actions for other states


def main():
    # Initialize the state machine
    run()

    # Main loop
    while True:
        pass

    

if __name__ == "__main__":
    main()

