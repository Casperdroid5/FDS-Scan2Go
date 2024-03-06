import time
from machine import Pin, I2C, PWM
from button import Button
from potmeter import Potentiometer
from rgbled import RGBLED
from sh1106 import SH1106_I2C
from servo import Servo
import time
import _thread


FerroFree = False
PatientReturnedFromMRI = False

class States:
    InitialisationState = 0
    WaitForUserFieldAState = 1  
    WaitForUserFieldBState = 2
    FerrometalDetectionState = 3    
    Lockandclosedoor1State = 4  
    Unlockandopendoor1State = 5     
    Lockandclosedoor2State = 6  
    Unlockandopendoor2State = 7

# Hardware Abstraction Layer
class Hardware:
    def __init__(self):
        # Initialize hardware components
        self.testled = Pin(22, Pin.OUT)
        self.ledDoor2Lock = RGBLED(10, 11, 12)
        self.ledDoor1Lock = RGBLED(2, 3, 4)
        self.ledScanner = RGBLED(6, 7, 8)
        self.Door1Motor = Servo(14)
        self.Door2Motor = Servo(15)
        self.Piezo = PWM(16)
        self.Button1 = Button(5)
        self.Button2 = Button(9)
        self.Button3 = Button(13)
        self.Switch1 = Button(20)
        self.Switch2 = Button(19)
        self.Switch3 = Button(18)
        self.Switch4 = Button(17)
        self.Pot1 = Potentiometer(27)

        # Initialize display
        self.display = self._initialize_display()

    def _initialize_display(self):
        # Initialize OLED display
        scl_pin, sda_pin = Pin(1), Pin(0)
        OLEDi2c = I2C(0, scl=scl_pin, sda=sda_pin, freq=400000)
        display = SH1106_I2C(128, 64, OLEDi2c, Pin(16), 0x3c, 180)
        return display

# State Machine
class StateMachine:
    def __init__(self, hardware):
        self.hardware = hardware
        self.current_state = None
        _thread.start_new_thread(self.CheckEmmergencyButton, ())

    def start(self):
        self.current_state = InitialisationState(self.hardware)
        self.current_state.enter_state()

    def update(self):
        while True:
            new_state = self.current_state.check_transition()
            if new_state:
                self.current_state.exit_state()
                self.current_state = new_state
                self.current_state.enter_state()
            self.current_state.execute_action()


    def CheckEmmergencyButton(self):
           while True:
               if self.hardware.Button3.is_pressed():
                   print("Emergency button pressed.")
                   print("Transitioning to EmergencyState.")
                   self.current_state = EmergencyState(self.hardware)
                   self.current_state.enter_state()
                   time.sleep(0.1)
#    States
class StateBase:
    def __init__(self, hardware):
        self.hardware = hardware

    def enter_state(self):
        pass

    def exit_state(self):
        pass

    def check_transition(self):
        pass

    def execute_action(self):
        pass


# States
class State:
    def __init__(self, hardware):
        self.hardware = hardware

    def enter_state(self):
        pass

    def exit_state(self):
        pass

    def check_transition(self):
        pass

    def execute_action(self):
        pass

class InitialisationState(State):
    def __init__(self, hardware):
        super().__init__(hardware)
        
    def enter_state(self):
        self.hardware.display.fill(0)
        self.hardware.display.text("-State: Init-", 0, 0, 1)
        self.hardware.display.show()
        self.hardware.ledDoor2Lock.off() # Corrected method call
        self.hardware.ledDoor1Lock.off() # Corrected method call
        self.hardware.ledScanner.off()   # Corrected method call
        self.hardware.Door2Motor.set_angle(90)
        self.hardware.Door1Motor.set_angle(0)
    
    def check_transition(self):
        print("Transitioning to WaitForUserFieldAState")        
        return WaitForUserFieldAState(self.hardware)

class WaitForUserFieldAState(State):
    def __init__(self, hardware):
        super().__init__(hardware)
        
    def enter_state(self):
        self.hardware.display.fill(0)
        self.hardware.display.text("-State: WFieldA-", 0, 0, 1)
        self.hardware.display.show()

    def check_transition(self):
        global PatientReturnedFromMRI
        if self.hardware.Switch3.is_pressed() and self.hardware.Switch4.is_not_pressed(): 
            if PatientReturnedFromMRI == False:
                print("Transitioning to Lockandclosedoor1State")
                return Lockandclosedoor1State(self.hardware)  
            elif PatientReturnedFromMRI == True:
                print("Transitioning to Lockandclosedoor2State")
                return Lockandclosedoor2State(self.hardware)
        else:
            return None
        
class WaitForUserFieldBState(State):
    def __init__(self, hardware):
        super().__init__(hardware)
        
    def enter_state(self):
        self.hardware.display.fill(0)
        self.hardware.display.text("-State: WFieldB-", 0, 0, 1)
        self.hardware.display.show()

    def check_transition(self):
        global FerroFree
        global PatientReturnedFromMRI
        if self.hardware.Switch3.is_not_pressed() and self.hardware.Switch4.is_pressed(): 
           if PatientReturnedFromMRI == False and FerroFree == True:
               print("Transitioning to Unlockandopendoor2State")
               return Unlockandopendoor2State(self.hardware)
           if PatientReturnedFromMRI == False and FerroFree == False: 
                print("Transitioning to FerrometalDetectionState")
                return FerrometalDetectionState(self.hardware)
           if PatientReturnedFromMRI == True:    
                print("Transitioning to WaitForUserFieldAState")   
                return WaitForUserFieldAState(self.hardware)
        else:
            return None        
class FerrometalDetectionState(State):
    def __init__(self, hardware):
        super().__init__(hardware)

    def enter_state(self):
        self.hardware.display.fill(0)
        self.hardware.display.text("-State: FerroD-", 0, 0, 1)
        self.hardware.display.show()

    def check_transition(self):
        global FerroFree # Import global variable
        print("Checking transition in FerrometalDetection")
        pot_value = self.hardware.Pot1.read_value()
        print("Potentiometer value:", pot_value)
        if 0 <= pot_value < 40000:
            self.hardware.ledScanner.set_color(0, 6000, 0)  # Green    
            print("Transitioning to Unlockandopendoor2State")
            FerroFree = True
            time.sleep(1.5)
            return Unlockandopendoor2State(self.hardware)
        elif 40000 <= pot_value <= 66000:
            self.hardware.ledScanner.set_color(6000, 0, 0)  # Red 
            print("Transitioning to Unlockandopendoor1State")      
            return Unlockandopendoor1State(self.hardware)   


class Lockandclosedoor1State(State):
    def __init__(self, hardware):
        super().__init__(hardware)
        
    def enter_state(self):
        self.hardware.display.fill(0)
        self.hardware.display.text("-State: Lock1-", 0, 0, 1)
        self.hardware.display.show()
        self.hardware.Door1Motor.set_angle(90)
        self.hardware.ledDoor1Lock.set_color(6000, 0, 0)  # Red - indicating door closed
    
    def check_transition(self):
        print("Transitioning to Lockandclosedoor2State")   
        return Lockandclosedoor2State(self.hardware)    

class Unlockandopendoor1State(State):
    def __init__(self, hardware):
        super().__init__(hardware)

    def enter_state(self):
        self.hardware.display.fill(0)
        self.hardware.display.text("-State: Open1-", 0, 0, 1)
        self.hardware.display.show()
        time.sleep(2)
        self.hardware.Door1Motor.set_angle(0) # door openend
        self.hardware.ledDoor1Lock.set_color(0, 6000, 0)  # Green - indicating door opened
        self.hardware.ledScanner.off()  #LED OFF
        time.sleep(2) # wait for visual effect
    def check_transition(self):
        print("Transitioning to WaitForUserFieldAState")
        return WaitForUserFieldAState(self.hardware)  
    
class Lockandclosedoor2State(State):
    def __init__(self, hardware):
        super().__init__(hardware)
        
    def enter_state(self):

        self.hardware.display.fill(0)
        self.hardware.display.text("-State: Lock2-", 0, 0, 1)
        self.hardware.display.show() 
        self.hardware.Door2Motor.set_angle(90) # open
        self.hardware.ledDoor2Lock.set_color(6000, 0, 0)  # Red - indicating door closed
        self.hardware.ledScanner.off()  #LED OFF

    def check_transition(self):
        global PatientReturnedFromMRI
        global FerroFree
        if PatientReturnedFromMRI == True:
            print("Transitioning to Unlockandopendoor1State")
            PatientReturnedFromMRI = False
            FerroFree = False
            return Unlockandopendoor1State(self.hardware)       
        elif PatientReturnedFromMRI == False:
            print("Transitioning to WaitForUserFieldBState")
            return WaitForUserFieldBState(self.hardware)

class Unlockandopendoor2State(State):
    def __init__(self, hardware):
        super().__init__(hardware)

    def enter_state(self):
        global PatientReturnedFromMRI 
        PatientReturnedFromMRI = True
        self.hardware.display.fill(0)
        self.hardware.display.text("-State: Open2-", 0, 0, 1)
        self.hardware.display.show()
        self.hardware.Door2Motor.set_angle(0) # door openend
        self.hardware.ledDoor2Lock.set_color(0, 6000, 0)  # Green - indicating door opened
        self.hardware.ledScanner.off()  #LED OFF
        time.sleep(2) # wait with closing door for visual effect
        
    def check_transition(self):
        print("Transitioning to WaitForUserFieldBState")
        return WaitForUserFieldBState(self.hardware)

class EmergencyState(State):
    def __init__(self, hardware):
        super().__init__(hardware)

    def enter_state(self):
        self.hardware.display.fill(0)
        self.hardware.display.text("-State: Emergency-", 0, 0, 1)
        self.hardware.display.show()
        self.hardware.Door1Motor.set_angle(0)  # Open door 1
        self.hardware.Door2Motor.set_angle(0)  # Open door 2
        self.hardware.ledDoor1Lock.set_color(0, 0, 6000)  # Blue
        self.hardware.ledDoor2Lock.set_color(0, 0, 6000)  # Blue
        self.hardware.ledScanner.set_color(0, 0, 6000)  # Blue

    def check_transition(self):
        if self.hardware.Button2.is_pressed():
            print("Reset button pressed.")
            print("Transitioning to InitialisationState")
            return InitialisationState(self.hardware)
        else:
            return None

if __name__ == "__main__":
    hardware = Hardware()
    machine = StateMachine(hardware)
    machine.start()
    while True:
        machine.update()
