from hardware_s2g import RGB, DOOR
from system_utils import SystemUtilsCheck
from machine import Pin, ADC
import time

# State Machine
class StateMachine:
    def __init__(self):

        # StatemachineVariables
        self.angle_open = 0
        self.angle_closed = 90
        self.scanner_result = "NoMetalDetected"
        self.user_returned_from_mri = False
        self.emergency_state = False
        self.initialized = False
        self.person_present_in_field_a = False
        self.person_present_in_field_b = False

        # doorbuttons variables
        self.person_detector_field_a = False
        self.person_detector_field_b = False
        self.button_door1_pressed = False
        self.button_door2_pressed = False

        # Define integer constants for states
        self.INITIALISATION_STATE = 0
        self.USER_FIELD_A_RESPONSE_STATE = 1
        self.USER_FIELD_B_RESPONSE_STATE = 2
        self.SCAN_FOR_FERROMETALS = 3
        self.METAL_DETECTED_STATE = 4
        self.METAL_NOT_DETECTED_STATE = 5
        self.UNLOCK_AND_OPEN_DOOR1_STATE = 6
        self.CLOSE_AND_LOCK_DOOR1_STATE = 7
        self.UNLOCK_AND_OPEN_DOOR2_STATE = 8
        self.CLOSE_AND_LOCK_DOOR2_STATE = 9
        self.EMERGENCY_STATE = 10

        # Initialize indicator lights
        self.lock_door2 = RGB(10, 11, 12)
        self.lock_door1 = RGB(2, 3, 4)
        self.ferro_led = RGB(6, 7, 8)

        # Initialize doors
        self.door1 = DOOR(14, self.angle_closed, self.angle_open)
        self.door2 = DOOR(15, self.angle_closed, self.angle_open)
        self.pot1 = ADC(27)

        # Initialize buttons
        self.button_emergency_mri = Pin(9, Pin.IN, Pin.PULL_UP)
        self.button_emergency_mri.irq(trigger=Pin.IRQ_FALLING, handler=self.handle_emergency_button_press)
        self.button_emergency_scanner = Pin(16, Pin.IN, Pin.PULL_UP)
        self.button_emergency_scanner.irq(trigger=Pin.IRQ_FALLING, handler=self.handle_emergency_button_press)
        self.button_door1 = Pin(21, Pin.IN, Pin.PULL_UP)
        self.button_door1.irq(trigger=Pin.IRQ_FALLING, handler=self.unlock_and_open_door1_state)
        self.button_door2 = Pin(17, Pin.IN, Pin.PULL_UP)
        self.button_door2.irq(trigger=Pin.IRQ_FALLING, handler=self.unlock_and_open_door2_state)
        self.switch_person_detector_field_a = Pin(19, Pin.IN, Pin.PULL_UP)
        self.switch_person_detector_field_b = Pin(20, Pin.IN, Pin.PULL_UP)

    # State Functions
    def initialization_state(self):
        self.lock_door1.off()  # Turn indicator off
        self.lock_door2.off()  # Turn indicator off
        self.ferro_led.off()  # Turn indicator off
        print("initialization_state")
        self.door2._close_door()  # _close_door DOOR 2
        self.lock_door2.set_color("red")  # DOOR Locked
        self.door1._open_door()  # _open_door DOOR 1
        self.lock_door1.set_color("green")  # DOOR Unlocked
        return 0 # State Ran succsessfully

    def user_field_a_response_state(self):
        print("user_field_a_response_state")
        if self.person_detector_field_a == True and self.person_detector_field_b == False: 
            return 0 # State Ran succsessfully

    def user_field_b_response_state(self):
        print("user_field_b_response_state")
        if self.person_detector_field_a == False and self.person_detector_field_b == True:
            return 0 # State Ran succsessfully

    def scan_for_ferrometals(self):
        print("scan_for_ferrometals")
        pot_value = self.pot1.read_u16()
        scaled_value = (pot_value / 65535) * 100 # Convert potentiometer value to a range between 0 and 100
        print("Potentiometer value:", scaled_value)
        if 0 <= scaled_value < 30:
            self.ferro_led.set_color("green")  # Green
            self.scanner_result = "NoMetalDetected"
            return self.scanner_result
        elif 30 <= scaled_value <= 80:
            self.scanner_result = "ScanInProgress"
            self.ferro_led.set_color("blue")
            return self.scanner_result
        elif 90 < scaled_value <= 100:
            self.scanner_result = "MetalDetected"
            self.ferro_led.set_color("red")  # Red

    def metal_detected_state(self):
        print("metal_detected_state")
        self.ferro_led.set_color("red")
        return 0 # State Ran succsessfully

    def metal_not_detected_state(self):
        print("metal_not_detected_state")
        self.ferro_led.set_color("green")
        return 0 # State Ran succsessfully

    def unlock_and_open_door1_state(self, pin):
        if pin == self.button_door1:
            self.button_door1_pressed = True
            return self.button_door1_pressed
        print("unlock_and_open_door1_state")
        self.door1._open_door()
        self.lock_door1.set_color("green") 
        return 0 # State Ran succsessfully

    def close_and_lock_door1_state(self):
        print("close_and_lock_door1_state")
        self.door1._close_door() 
        self.lock_door1.set_color("red")  
        return 0 # State Ran succsessfully

    def unlock_and_open_door2_state(self, pin):
        if pin == self.button_door2:
            self.button_door2_pressed = True
            return self.button_door2_pressed
        print("unlock_and_open_door2_state")
        self.door2._open_door() 
        self.lock_door2.set_color("green") 
        return 0 # State Ran succsessfully

    def close_and_lock_door2_state(self):
        print("close_and_lock_door2_state")
        self.door2._close_door() 
        self.lock_door2.set_color("red") 
        return 0 # State Ran succsessfully    

    def handle_emergency_button_press(self, pin):
        print("handle_emergency_button_press")
        if pin == self.button_emergency_mri:
            print("Emergency button MRIRoom pressed")
            self.door2._open_door()
            self.door1._close_door()
            self.lock_door1.set_color("blue") 
            self.lock_door2.set_color("blue") 
            self.ferro_led.set_color("blue") 
            self.emergency_state = True
            return self.emergency_state
        elif pin == self.button_emergency_scanner:
            print("Emergency button ScannerRoom pressed")
            self.door1._open_door()
            self.door2._close_door()
            self.lock_door1.set_color("blue") 
            self.lock_door2.set_color("blue") 
            self.ferro_led.set_color("blue") 
            self.emergency_state = True
            return self.emergency_state

    def check_person_in_field_a(self):
        print("check_person_in_field_A")
        self.person_present_in_field_a = not self.switch_person_detector_field_a.value()  # Check if the switch is closed
        return self.person_present_in_field_a

    def check_person_in_field_b(self):
        print("check_person_in_field_B")
        self.person_present_in_field_b = not self.switch_person_detector_field_b.value()  # Check if the switch is closed
        return self.person_present_in_field_b

    
    # State machine
    def run(self):

        self.state = self.INITIALISATION_STATE
        while True:
            if self.emergency_state == True:
                print("Emergency state triggered, stopping state machine after")
                break

            if self.button_door1_pressed == True:
                if self.state == self.USER_FIELD_A_RESPONSE_STATE:
                    self.state = self.UNLOCK_AND_OPEN_DOOR1_STATE
                    self.button_door1_pressed = False

            if self.button_door2_pressed == True:
                if self.state == self.USER_FIELD_B_RESPONSE_STATE or self.state == self.METAL_NOT_DETECTED_STATE:
                    self.state = self.UNLOCK_AND_OPEN_DOOR2_STATE
                    self.button_door2_pressed = False

            if self.state == self.INITIALISATION_STATE:
                if not self.initialized:
                    self.initialization_state()
                    self.initialized = True 
                self.state = self.USER_FIELD_A_RESPONSE_STATE

            elif self.state == self.USER_FIELD_A_RESPONSE_STATE:
                self.check_person_in_field_a()
                if self.person_present_in_field_a == True and self.user_returned_from_mri == False:
                    self.state = self.CLOSE_AND_LOCK_DOOR1_STATE
                if  self.person_present_in_field_a == True and self.user_returned_from_mri == True:
                    self.user_returned_from_mri = False
                    self.state = self.UNLOCK_AND_OPEN_DOOR1_STATE

            elif self.state == self.USER_FIELD_B_RESPONSE_STATE:
                self.check_person_in_field_b()
                if self.scanner_result == "MetalDetected" and self.person_present_in_field_b == True:
                    self.state = self.UNLOCK_AND_OPEN_DOOR1_STATE
                if self.scanner_result == "NoMetalDetected" and self.person_present_in_field_b == True:
                    self.state = self.UNLOCK_AND_OPEN_DOOR2_STATE
                if self.user_returned_from_mri == True and self.person_present_in_field_b == True:
                    self.state = self.CLOSE_AND_LOCK_DOOR2_STATE

            elif self.state == self.SCAN_FOR_FERROMETALS:
                self.state = self.scan_for_ferrometals() 
                if self.scanner_result == "MetalDetected":
                    self.state = self.METAL_DETECTED_STATE
                elif self.scanner_result == "NoMetalDetected":
                    self.state = self.METAL_NOT_DETECTED_STATE 
                elif self.scanner_result == "ScanInProgress":
                    self.state = self.SCAN_FOR_FERROMETALS 

            elif self.state == self.METAL_DETECTED_STATE:
                self.state = self.metal_detected_state()
                if self.metal_detected_state() == 0:
                    self.state = self.USER_FIELD_B_RESPONSE_STATE

            elif self.state == self.METAL_NOT_DETECTED_STATE:
                self.state = self.metal_not_detected_state()
                if self.metal_not_detected_state() == 0:
                    self.state = self.USER_FIELD_B_RESPONSE_STATE

            elif self.state == self.UNLOCK_AND_OPEN_DOOR1_STATE:
                self.state = self.unlock_and_open_door1_state(None)
                if self.unlock_and_open_door1_state(None) == 0:
                    self.state = self.USER_FIELD_A_RESPONSE_STATE

            elif self.state == self.CLOSE_AND_LOCK_DOOR1_STATE:
                self.state = self.close_and_lock_door1_state()
                if self.close_and_lock_door1_state() == 0: 
                    self.state = self.SCAN_FOR_FERROMETALS

            elif self.state == self.UNLOCK_AND_OPEN_DOOR2_STATE:
                if self.user_returned_from_mri == False:
                    self.user_returned_from_mri = True	
                    self.state = self.unlock_and_open_door2_state(None)
                    self.state = self.USER_FIELD_B_RESPONSE_STATE
                    print("State reached")

            elif self.state == self.CLOSE_AND_LOCK_DOOR2_STATE:
                self.state = self.close_and_lock_door2_state()
                self.state = self.USER_FIELD_A_RESPONSE_STATE

            else:
                print("Invalid state")
                break
            time.sleep(0.5)

if __name__ == "__main__":
    try:
        system_check = SystemUtilsCheck()
        FDS = StateMachine()
        FDS.run()
    except SystemExit:
        print("System initialization failed. Exiting...")
    except Exception as e:
        print("An unexpected error occurred during initialization:", e)
        
class ErrorHandler:
    def report_error(self, components):
        for component in components:
            self.display_error(component)
            # log error potential to a file or send it to a server

    def display_error(self, component):
        print(f"Error in component: {component}")

def check_sensors():
    # Check if sensors are connected and working
    _SensorFunctional = True  # for testing purposes this is set to...
    return _SensorFunctional

def check_motors():
    # Check if motors are connected and working
    _MotorFunctional = True  # for testing purposes this is set to...
    return _MotorFunctional

def check_leds():
    # Check if LEDs are connected and working
    _LedsFunctional = True  # for testing purposes this is set to...
    return _LedsFunctional

def check_buttons():
    # Check if buttons are connected and working
    _ButtonsFunctional = True  # for testing purposes this is set to...
    return _ButtonsFunctional

class SystemUtilsCheck:
    def __init__(self):
        print("System is starting up, running system check")
        failing_components = self.systemcheck()
        if failing_components:
            print("failed system check, reporting error(s):")
            ErrorHandler().report_error(failing_components)
            print("System check failed, exiting.")
            raise SystemExit
        else:
            print("System check passed, continuing with startup.")

    def systemcheck(self):
        failing_components = [] # List to store failing components
        # Check sensors
        if not check_sensors():
            failing_components.append("Sensors")

        # Check motors
        if not check_motors():
            failing_components.append("Motors")

        # Check LEDs
        if not check_leds():
            failing_components.append("LEDs")

        # Check buttons
        if not check_buttons():
            failing_components.append("Buttons")

        return failing_components # Return the list of failing components