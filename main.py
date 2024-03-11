import time
from machine import Pin, I2C, PWM, ADC
from rgbled import RGBLED
import sh1106
from servo import Servo


class States:
    InitialisationState = 0
    WaitForUserFieldAState = 1  
    WaitForUserFieldBState = 2
    FerrometalDetectionState = 3    
    Lockandclosedoor1State = 4  
    Unlockandopendoor1State = 5     
    Lockandclosedoor2State = 6  
    Unlockandopendoor2State = 7
    EmergencyState = 8

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

#States
state = "WaitForUserFieldAState" # Initial state

def initialize_hardware():
    # Your hardware initialization code goes here
    pass

def handle_emergency_button(pin):
    # Handle the emergency button press
    pass

def check_userbfield(door, sensor1, sensor2):
    # Your implementation of check_userbfield
    pass

def update_FerrometalDetectionState():
    # Your implementation of update_FerrometalDetectionState
    pass

def ferro_handler():
    # Your implementation of ferro_handler
    pass

def error_handler():
    # Your implementation of error_handler
    pass

#StateMachine
while True:
    print(state)
    
    if state == "WaitForUserFieldAState":
        if check_userbfield(door, sensor1, sensor2):
            state = "WaitForUserFieldBState"
            
    elif state == "WaitForUserFieldBState":
        update_FerrometalDetectionState()
        state = "FerrometalDetectionState"
        
    elif state == "FerrometalDetectionState":
        ferro_handler()  # Assuming this function handles ferrometal detection
        state = "WaitForUserFieldBState"  # Transition back to WaitForUserFieldBState
        
    elif state == "errorstate":
        error_handler()
        # Reset to an empty state machine
        state = "empty"
        break  # Exit the loop

    # Add more cases as needed

    # Handle transitions and actions for other states

# End of while loop




    def handle_emergency_button():

        global EmergencyButtonFlag
        print (EmergencyButtonFlag)
        EmergencyButtonFlag = True
        print (EmergencyButtonFlag)
        print("Emergency button pressed.")
        print("Transitioning to EmergencyState.")
        .current_state = EmergencyState()
        .current_state.enter_state()
        while state is not resumefromemerghency():
        
    def handle_reset_button():
        print("Reset button pressed.")
        print("Transitioning to InitialisationState.")
        .current_state = InitialisationState()
        .current_state.enter_state()    


class InitialisationState(State):
    def __init__(, hardware):
        super().__init__(hardware)
        
    def enter_state():
       display.fill(0)
       display.text("-State: Init-", 0, 0, 1)
       display.show()
       ledDoor2Lock.off() 
       ledDoor1Lock.off() 
       ledScanner.off()   
       Door2Motor.set_angle(90)
       Door1Motor.set_angle(0)
    
    def check_transition():
        print("Transitioning to WaitForUserFieldAState")        
        return WaitForUserFieldAState(.hardware)

class WaitForUserFieldAState(State):
    def __init__(, hardware):
        super().__init__(hardware)
        
    def enter_state():
       display.fill(0)
       display.text("-State: WFieldA-", 0, 0, 1)
       display.show()

    def check_transition():
        global PatientReturnedFromMRI
        ifFieldA.value() == 0 andFieldB.value() == 1: 
            if not PatientReturnedFromMRI:
                print("Transitioning to Lockandclosedoor1State")
                return Lockandclosedoor1State(.hardware)
            else:
                print("Transitioning to Lockandclosedoor2State")
                return Lockandclosedoor2State(.hardware)
        else:
            return None

class WaitForUserFieldBState(State):
    def __init__(, hardware):
        super().__init__(hardware)
        
    def enter_state():
       display.fill(0)
       display.text("-State: WFieldB-", 0, 0, 1)
       display.show()

    def check_transition():
        global FerroFree, PatientReturnedFromMRI
        ifFieldA.value() == 1 andFieldB.value() == 0:
            if not PatientReturnedFromMRI and FerroFree:
                print("Transitioning to Unlockandopendoor2State")
                return Unlockandopendoor2State(.hardware)
            elif not PatientReturnedFromMRI and not FerroFree:
                print("Transitioning to FerrometalDetectionState")
                return FerrometalDetectionState(.hardware)
            elif PatientReturnedFromMRI:
                print("Transitioning to WaitForUserFieldAState")
                return WaitForUserFieldAState(.hardware)
        else:
            return None

class FerrometalDetectionState(State):
    def __init__(, hardware):
        super().__init__(hardware)

    def enter_state():
       display.fill(0)
       display.text("-State: FerroD-", 0, 0, 1)
       display.show()

    def check_transition():
        global FerroFree # Import global variable
        print("Checking transition in FerrometalDetection")
        pot_value =Pot1.read_u16()  # Read potentiometer pin
        print("Potentiometer value:", pot_value)
        if 0 <= pot_value < 40000:
           ledScanner.set_color(0, 6000, 0)  # Green    
            print("Transitioning to Unlockandopendoor2State")
            FerroFree = True
            time.sleep(1.5)
            return Unlockandopendoor2State(.hardware)
        elif 40000 <= pot_value <= 66000:
           ledScanner.set_color(6000, 0, 0)  # Red 
            print("Transitioning to Unlockandopendoor1State")      
            return Unlockandopendoor1State(.hardware)

class Lockandclosedoor1State(State):
    def __init__(, hardware):
        super().__init__(hardware)
        
    def enter_state():
       display.fill(0)
       display.text("-State: Lock1-", 0, 0, 1)
       display.show()
       Door1Motor.set_angle(90)
       ledDoor1Lock.set_color(6000, 0, 0)  # Red - indicating door closed
    
    def check_transition():
        print("Transitioning to Lockandclosedoor2State")   
        return Lockandclosedoor2State(.hardware)    

class Unlockandopendoor1State(State):
    def __init__(hardware):
        super().__init__(hardware)

    def enter_state():
       display.fill(0)
       display.text("-State: Open1-", 0, 0, 1)
       display.show()
        time.sleep(2)
       Door1Motor.set_angle(0) # door openend
       ledDoor1Lock.set_color(0, 6000, 0)  # Green - indicating door opened
       ledScanner.off()  #LED OFF
        time.sleep(2) # wait for visual effect
    def check_transition():
        print("Transitioning to WaitForUserFieldAState")
        return WaitForUserFieldAState(hardware)  
    
class Lockandclosedoor2State(State):
    def __init__(, hardware):
        super().__init__(hardware)
        
    def enter_state():

       display.fill(0)
       display.text("-State: Lock2-", 0, 0, 1)
       display.show() 
       Door2Motor.set_angle(90) # open
       ledDoor2Lock.set_color(6000, 0, 0)  # Red - indicating door closed
       ledScanner.off()  #LED OFF

    def check_transition():
        global PatientReturnedFromMRI
        global FerroFree
        if PatientReturnedFromMRI == True:
            print("Transitioning to Unlockandopendoor1State")
            PatientReturnedFromMRI = False
            FerroFree = False
            return Unlockandopendoor1State(.hardware)       
        elif PatientReturnedFromMRI == False:
            print("Transitioning to WaitForUserFieldBState")
            return WaitForUserFieldBState(.hardware)

class Unlockandopendoor2State(State):
    def __init__(hardware):
        super().__init__(hardware)

    def enter_state():
        global PatientReturnedFromMRI 
        PatientReturnedFromMRI = True
       display.fill(0)
       display.text("-State: Open2-", 0, 0, 1)
       display.show()
       Door2Motor.set_angle(0) # door openend
       ledDoor2Lock.set_color(0, 6000, 0)  # Green - indicating door opened
       ledScanner.off()  #LED OFF
        time.sleep(2) # wait with closing door for visual effect
        
    def check_transition():
        print("Transitioning to WaitForUserFieldBState")
        return WaitForUserFieldBState(hardware)

class EmergencyState(State):

    def __init__(hardware):
        super().__init__(hardware)

    def enter_state():
       display.fill(0)
       display.text("-State: Emergency-", 0, 0, 1)
       display.show()
       Door1Motor.set_angle(0)  # Open door 1
       Door2Motor.set_angle(0)  # Open door 2
       ledDoor1Lock.set_color(0, 0, 6000)  # Blue
       ledDoor2Lock.set_color(0, 0, 6000)  # Blue
       ledScanner.set_color(0, 0, 6000)  # Blue
        

    def check_transition(): 
        return None

main()
    hardware = Hardware()
    machine = StateMachine(hardware)
    machine.start()
    machine.update()
    

if __name__ == "__main__":
    main()

