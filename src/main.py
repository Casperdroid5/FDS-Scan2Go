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
        self.scanner_result = False
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
        self.scan_for_ferrometals = 3
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
        self.button_person_detector_field_a = Pin(19, Pin.IN, Pin.PULL_UP)
        self.button_person_detector_field_a.irq(trigger=Pin.IRQ_FALLING, handler=self.person_detected_in_field_a)
        self.button_person_detector_field_b = Pin(20, Pin.IN, Pin.PULL_UP)
        self.button_person_detector_field_b.irq(trigger=Pin.IRQ_FALLING, handler=self.person_detected_in_field_b)


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
        if 0 <= pot_value < 50:
            self.ferro_led.set_color("green")  # Green
            self.scanner_result = False
            return self.scanner_result
        elif 50 <= pot_value <= 80:
            self.scanner_result = None
            self.ferro_led.set_color("blue")
            return self.scanner_result
        elif 80 < pot_value <= 100:
            self.scanner_result = True
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

    def person_detected_in_field_a(self, pin):
        print("person_detected_in_field_a")
        self.person_present_in_field_a = True
        return self.person_present_in_field_a

    def person_not_detected_in_field_a(self, pin):
        print("person_not_detected_in_field_a")
        self.person_present_in_field_a = False
        return self.person_present_in_field_a

    def person_detected_in_field_b(self, pin):
        print("person_detected_in_field_b")
        self.person_present_in_field_b = True
        return self.person_present_in_field_b

    def person_not_detected_in_field_b(self, pin):
        print("person_not_detected_in_field_b")
        self.person_present_in_field_b = False
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
                if not self.initialized:  # Check if initialization has been done
                    self.initialization_state()
                    self.initialized = True  # Set the flag to True after initialization
                self.state = self.USER_FIELD_A_RESPONSE_STATE

            elif self.state == self.USER_FIELD_A_RESPONSE_STATE:
                if self.person_present_in_field_a == True:
                    self.state = self.CLOSE_AND_LOCK_DOOR1_STATE

            elif self.state == self.USER_FIELD_B_RESPONSE_STATE:
                if self.person_present_in_field_b == True:
                    self.state = self.CLOSE_AND_LOCK_DOOR2_STATE

            elif self.state == self.scan_for_ferrometals:
                self.state = self.scan_for_ferrometals()
                if self.scanner_result == False:
                    self.state = self.METAL_NOT_DETECTED_STATE
                elif self.scanner_result == True:
                    self.state = self.METAL_DETECTED_STATE 
                elif self.scanner_result == None:
                    self.state = self.scan_for_ferrometals

            elif self.state == self.METAL_DETECTED_STATE:
                self.state = self.metal_detected_state()
                if self.metal_detected_state() == 0:
                    self.state = self.UNLOCK_AND_OPEN_DOOR1_STATE

            elif self.state == self.METAL_NOT_DETECTED_STATE:
                self.state = self.metal_not_detected_state()
                if self.metal_not_detected_state() == 0:
                    self.state = self.UNLOCK_AND_OPEN_DOOR2_STATE

            elif self.state == self.UNLOCK_AND_OPEN_DOOR1_STATE:
                self.state = self.unlock_and_open_door1_state(None)
                if self.unlock_and_open_door1_state(None) == 0:
                    self.state = self.USER_FIELD_A_RESPONSE_STATE

            elif self.state == self.CLOSE_AND_LOCK_DOOR1_STATE:
                self.state = self.close_and_lock_door1_state()
                if self.close_and_lock_door1_state() == 0: 
                    self.state = self.scan_for_ferrometals 

            elif self.state == self.UNLOCK_AND_OPEN_DOOR2_STATE:
                self.state = self.unlock_and_open_door2_state(None)
                if self.unlock_and_open_door2_state(None) == 0:
                    self.state = self.USER_FIELD_B_RESPONSE_STATE

            elif self.state == self.CLOSE_AND_LOCK_DOOR2_STATE:
                self.state = self.close_and_lock_door2_state()
            else:
                print("Invalid state")
                break
            time.sleep(0.3) # Sleep for 300ms to avoid a very fast loop

if __name__ == "__main__":
    try:
        system_check = SystemUtilsCheck()  # Perform system check
        FDS = StateMachine()
        FDS.run()
    except SystemExit:
        print("System initialization failed. Exiting...")
    except Exception as e:
        print("An unexpected error occurred during initialization:", e)