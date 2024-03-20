from machine import Pin, ADC
from hardwares2g import RGB, DOOR

class StateMachine:
    def __init__(self):

        # StatemachineVariables
        self.angle_open = 0
        self.angle_closed = 90
        self.ferrometal_detected = False
        self.user_returned_from_mri = False
        self.emergency_state = False
        self.person_detector_field_a = False
        self.person_detector_field_b = False

        # Define integer constants for states
        self.INITIALISATION_STATE = 0
        self.WAIT_FOR_USER_FIELD_A_STATE = 1
        self.WAIT_FOR_USER_FIELD_B_STATE = 2
        self.FERROMETAL_DETECTION_STATE = 3
        self.UNLOCK_AND_OPEN_DOOR1_STATE = 4
        self.CLOSE_AND_LOCK_DOOR1_STATE = 5
        self.UNLOCK_AND_OPEN_DOOR2_STATE = 6
        self.CLOSE_AND_LOCK_DOOR2_STATE = 7
        self.EMERGENCY_STATE = 8

        # Initialize lights
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
        self.button_door1 = Pin(17, Pin.IN, Pin.PULL_UP)
        self.button_door1.irq(trigger=Pin.IRQ_FALLING, handler=self.unlock_and_open_door1_state)
        self.button_door2 = Pin(18, Pin.IN, Pin.PULL_UP)
        self.button_door2.irq(trigger=Pin.IRQ_FALLING, handler=self.unlock_and_open_door2_state)

    # State Functions
    def initialization_state(self):
        self.user_returned_from_mri = False
        self.ferrometal_detected = False
        self.lock_door1.off()  # Turn indicator off
        self.lock_door2.off()  # Turn indicator off
        self.ferro_led.off()  # Turn indicator off
        print("Initialization state")
        self.door2._close_door()  # _close_door DOOR 2
        self.lock_door2.set_color("red")  # DOOR Locked
        self.door1._open_door()  # _open_door DOOR 1
        self.lock_door1.set_color("green")  # DOOR Unlocked
        return 0 # State Ran succsessfully

    def user_field_a_response_state(self):
        print("Waiting for user field A state")
        if self.person_detector_field_a and not self.person_detector_field_b: 
            return 0 # State Ran succsessfully

    def user_field_b_response_state(self):
        print("Waiting for user field B state")
        if not self.person_detector_field_a and self.person_detector_field_b:
            return 0 # State Ran succsessfully

    def ferrometal_detection_state(self):
        print("Ferrometal detection state")
        pot_value = self.pot1.read_u16()
        if 0 <= pot_value < 40000:
            self.ferro_led.set_color("green")  # Green
            self.ferrometal_detected = False
            return self.ferrometal_detected
        elif 40000 <= pot_value <= 66000:
            self.ferrometal_detected = True
            self.ferro_led.set_color("red")  # Red
            return self.ferrometal_detected

    def unlock_and_open_door1_state(self):
        print("Unlock and _open_door DOOR 1 state")
        self.door1._open_door()
        self.lock_door1.set_color("green") 
        return 0 # State Ran succsessfully

    def close_and_lock_door1_state(self):
        print("Lock and _close_door DOOR 1 state")
        self.door1._close_door() 
        self.lock_door1.set_color("red")  
        return 0 # State Ran succsessfully

    def unlock_and_open_door2_state(self):
        print("Unlock and _open_door DOOR 2 state")
        self.door2._open_door() 
        self.lock_door2.set_color("green") 
        return 0 # State Ran succsessfully

    def close_and_lock_door2_state(self):
        print("Lock and _close_door DOOR 2 state")
        self.door2._close_door() 
        self.lock_door2.set_color("red") 
        return 0 # State Ran succsessfully    

    def handle_emergency_button_press(self, pin):
        print("Emergency state")
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


    # State machine
    def run(self):
        state = self.initialization_state()

        while True:
            if self.emergency_state:  
                print("Emergency state triggered, stopping state machine")
                break

            # user_field_a_response_state
             if not self.user_returned_from_mri and not self.ferrometal_detected:
                return self.close_and_lock_door1_state 
            elif self.user_returned_from_mri: 
                return self.unlock_and_open_door1_state
        else: 
            return self.WAIT_FOR_USER_FIELD_A_STATE
        
            # user_field_b_response_state
                        if not self.user_returned_from_mri and not self.ferrometal_detected:
                print("1")
                return self.FERROMETAL_DETECTION_STATE
            elif self.user_returned_from_mri and self.ferrometal_detected:
                print("2")
                return self.UNLOCK_AND_OPEN_DOOR2_STATE
            elif self.user_returned_from_mri:
                print("3")
                self.door2._close_door()
                self.lock_door2.set_color("red")
                return self.WAIT_FOR_USER_FIELD_A_STATE
        else:
            return self.WAIT_FOR_USER_FIELD_B_STATE
        
        # ferrometeral_detection_state
        if self.ferrometal_detected: = True
            state1
        else:
            state2
            
        
        

            if state == self.INITIALISATION_STATE:
                state = self.initialization_state()
                
            if state == self.WAIT_FOR_USER_FIELD_A_STATE:
                state = self.user_field_a_response_state()

            elif state == self.WAIT_FOR_USER_FIELD_B_STATE:
                state = self.user_field_b_response_state()

            elif state == self.FERROMETAL_DETECTION_STATE:
                state = self.ferrometal_detection_state()

            elif state == self.unlock_and_open_door1_state:
                state = self.unlock_and_open_door1_state()

            elif state == self.close_and_lock_door1_state:
                state = self.close_and_lock_door1_state()

            elif state == self.UNLOCK_AND_OPEN_DOOR2_STATE:
                state = self.unlock_and_open_door2_state()

            elif state == self.close_and_lock_door2_state:
                state = self.close_and_lock_door2_state()

            else:
                print("Invalid state")
                break


if __name__ == "__main__":
    FDS = StateMachine()
    FDS.run()
