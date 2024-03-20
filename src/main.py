from machine import Pin, ADC
from hardwares2g import RGB, DOOR
import time

class StateMachine:
    def __init__(self):

        # StatemachineVariables
        self.angle_open = 0
        self.angle_closed = 90
        self.ferrometal_detected = False
        self.user_returned_from_mri = False
        self.emergency_state = False
        self.initialized = False  # Flag to track initialization
        # doorbuttons variables
        self.person_detector_field_a = False
        self.person_detector_field_b = False
        self.button_door1_pressed = False
        self.button_door2_pressed = False
        
        # Define integer constants for states
        self.INITIALISATION_STATE = 0
        self.USER_FIELD_A_RESPONSE_STATE = 1
        self.USER_FIELD_B_RESPONSE_STATE = 2
        self.FERROMETAL_DETECTION_STATE = 3
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
        self.button_door1 = Pin(17, Pin.IN, Pin.PULL_UP)
        self.button_door1.irq(trigger=Pin.IRQ_FALLING, handler=self.toggle_person_detector_field_a)
        self.button_door2 = Pin(18, Pin.IN, Pin.PULL_UP)
        self.button_door2.irq(trigger=Pin.IRQ_FALLING, handler=self.toggle_person_detector_field_b)
        


    # State Functions
    def initialization_state(self):
        # self.user_returned_from_mri = False
        # self.ferrometal_detected = False
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
        if self.person_detector_field_a == True and self.person_detector_field_b == False: # TEMPORARY CONDITION FOR TESTING
            return 0 # State Ran succsessfully

    def ferrometal_detection_state(self):
        print("ferrometal_detection_state")
        pot_value = self.pot1.read_u16()
        if 0 <= pot_value < 40000:
            self.ferro_led.set_color("green")  # Green
            self.ferrometal_detected = False
            return self.ferrometal_detected
        elif 40000 <= pot_value <= 66000:
            self.ferrometal_detected = True
            self.ferro_led.set_color("red")  # Red
            return self.ferrometal_detected

    def metal_detected_state(self):
        print("metal_detected_state")
        self.ferro_led.set_color("red")
        return 0 # State Ran succsessfully

    def metal_not_detected_state(self):
        print("metal_not_detected_state")
        self.ferro_led.set_color("green")
        return 0 # State Ran succsessfully

    def unlock_and_open_door1_state(self):
        print("unlock_and_open_door1_state")
        self.door1._open_door()
        self.lock_door1.set_color("green") 
        return 0 # State Ran succsessfully

    def close_and_lock_door1_state(self):
        print("close_and_lock_door1_state")
        self.door1._close_door() 
        self.lock_door1.set_color("red")  
        return 0 # State Ran succsessfully

    def unlock_and_open_door2_state(self):
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
        
    def toggle_person_detector_field_a(self, pin):
        print("Toggle person_detector_field_a")
        self.person_detector_field_a = not self.person_detector_field_a
        self.button_door1_pressed = True

    def toggle_person_detector_field_b(self, pin):
        print("Toggle person_detector_field_b")
        self.person_detector_field_b = not self.person_detector_field_b
        self.button_door2_pressed = True


    # State machine
    def run(self):
    
        self.state = self.INITIALISATION_STATE
        while True:
            if self.emergency_state:
                print("Emergency state triggered, stopping state machine after")
                break

            if self.state == self.INITIALISATION_STATE:
                if not self.initialized:  # Check if initialization has been done
                    self.initialization_state()
                    self.initialized = True  # Set the flag to True after initialization
                self.state = self.USER_FIELD_A_RESPONSE_STATE

            elif self.state == self.USER_FIELD_A_RESPONSE_STATE:
                if self.button_door1_pressed:
                    self.toggle_person_detector_field_a  # Toggle person_detector_field_a with the pin argument
                    self.button_door1_pressed = False
                if self.person_detector_field_a:
                    self.state = self.CLOSE_AND_LOCK_DOOR1_STATE
                else:
                    self.state = self.USER_FIELD_B_RESPONSE_STATE

            elif self.state == self.USER_FIELD_B_RESPONSE_STATE:
                if self.button_door2_pressed:
                    self.toggle_person_detector_field_b  # Toggle person_detector_field_b
                    self.button_door2_pressed = False
                if self.person_detector_field_b:
                    self.state = self.CLOSE_AND_LOCK_DOOR2_STATE
                else:
                    self.state = self.FERROMETAL_DETECTION_STATE

            elif self.state == self.FERROMETAL_DETECTION_STATE:
                self.state = self.ferrometal_detection_state()
                if self.ferrometal_detected == False:
                    self.state = self.METAL_NOT_DETECTED_STATE
                elif self.ferrometal_detected == True:
                    self.state = self.METAL_DETECTED_STATE # this makes the servo flipper

            elif self.state == self.METAL_DETECTED_STATE:
                self.state = self.metal_detected_state()
                if self.metal_detected_state() == 0:
                    self.state = self.UNLOCK_AND_OPEN_DOOR1_STATE

            elif self.state == self.METAL_NOT_DETECTED_STATE:
                self.state = self.metal_not_detected_state()
                if self.metal_not_detected_state() == 0:
                    self.state = self.UNLOCK_AND_OPEN_DOOR2_STATE

            elif self.state == self.UNLOCK_AND_OPEN_DOOR1_STATE:
                self.state = self.unlock_and_open_door1_state()
                if self.unlock_and_open_door1_state == 0:
                    self.state = self.USER_FIELD_A_RESPONSE_STATE

            elif self.state == self.CLOSE_AND_LOCK_DOOR1_STATE:
                self.state = self.close_and_lock_door1_state
                if self.close_and_lock_door1_state() == 0: 
                    self.state = self.FERROMETAL_DETECTION_STATE   # Transition back to ferrometal detection

            elif self.state == self.UNLOCK_AND_OPEN_DOOR2_STATE:
                self.state = self.unlock_and_open_door2_state()
                if self.unlock_and_open_door2_state() == 0:
                    self.state = self.USER_FIELD_B_RESPONSE_STATE

            elif self.state == self.CLOSE_AND_LOCK_DOOR2_STATE:
                self.state = self.close_and_lock_door2_state()
            else:
                print("Invalid state")
                break
            time.sleep(0.3) # Sleep for 100ms

                    
        #     # user_field_a_response_state
        #            if not self.user_returned_from_mri and not self.ferrometal_detected:
        #               return self.close_and_lock_door1_state 
        #           elif self.user_returned_from_mri: 
        #               return self.unlock_and_open_door1_state
        #       else: 
        #           return self.USER_FIELD_A_RESPONSE_STATE
        
        #     # user_field_b_response_state
        #                 if not self.user_returned_from_mri and not self.ferrometal_detected:
        #         print("1")
        #         return self.FERROMETAL_DETECTION_STATE
        #     elif self.user_returned_from_mri and self.ferrometal_detected:
        #         print("2")
        #         return self.UNLOCK_AND_OPEN_DOOR2_STATE
        #     elif self.user_returned_from_mri:
        #         print("3")
        #         self.door2._close_door()
        #         self.lock_door2.set_color("red")
        #         return self.USER_FIELD_A_RESPONSE_STATE
        # else:
        #     return self.USER_FIELD_B_RESPONSE_STATE
        
        # # ferrometeral_detection_state
        # if self.ferrometal_detected: = True
        #     state1
        # else:
        #     state2
            
        
        

        #     if state == self.INITIALISATION_STATE:
        #         state = self.initialization_state()
                
        #     if state == self.USER_FIELD_A_RESPONSE_STATE:
        #         state = self.user_field_a_response_state()

        #     elif state == self.USER_FIELD_B_RESPONSE_STATE:
        #         state = self.user_field_b_response_state()

        #     elif state == self.FERROMETAL_DETECTION_STATE:
        #         state = self.ferrometal_detection_state()

        #     elif state == self.unlock_and_open_door1_state:
        #         state = self.unlock_and_open_door1_state()

        #     elif state == self.close_and_lock_door1_state:
        #         state = self.close_and_lock_door1_state()

        #     elif state == self.UNLOCK_AND_OPEN_DOOR2_STATE:
        #         state = self.unlock_and_open_door2_state()

        #     elif state == self.close_and_lock_door2_state:
        #         state = self.close_and_lock_door2_state()

        #     else:
        #         print("Invalid state")
        #         break


if __name__ == "__main__":
    FDS = StateMachine()
    FDS.run()
