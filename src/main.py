from hardware_s2g import RGB, DOOR
from system_utils import SystemInitCheck
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
        self.EMERGENCY_STATE = 4
        self.USER_IN_MRIROOM = 5

        # Initialize indicator lights
        self.lock_door2 = RGB(10, 11, 12)
        self.lock_door1 = RGB(2, 3, 4)
        self.ferro_led = RGB(6, 7, 8)

        # Initialize doors
        self.door1 = DOOR(14, self.angle_closed, self.angle_open)
        self.door2 = DOOR(15, self.angle_closed, self.angle_open)
        self.ferrometalscanner = ADC(27)

        # Initialize buttons
        self.button_emergency_mri = Pin(9, Pin.IN, Pin.PULL_UP)
        self.button_emergency_mri.irq(trigger=Pin.IRQ_FALLING, handler=self.handle_emergency_button_press)
        self.button_emergency_scanner = Pin(16, Pin.IN, Pin.PULL_UP)
        self.button_emergency_scanner.irq(trigger=Pin.IRQ_FALLING, handler=self.handle_emergency_button_press)
        self.button_door1 = Pin(21, Pin.IN, Pin.PULL_UP)
        self.button_door1.irq(trigger=Pin.IRQ_FALLING, handler=lambda pin: self.operate_door(self.door1, 'open'))
        self.button_door2 = Pin(17, Pin.IN, Pin.PULL_UP)
        self.button_door2.irq(trigger=Pin.IRQ_FALLING, handler=lambda pin: self.operate_door(self.door2, 'open'))
        self.switch_person_detector_field_a = Pin(19, Pin.IN, Pin.PULL_UP)
        self.switch_person_detector_field_b = Pin(20, Pin.IN, Pin.PULL_UP)

    def person_detected_in_field(self, field):
        print(f"Checking for person in field {field}")    # Bericht afdrukken om aan te geven welk veld wordt gecontroleerd
        if field == 'A':     # Detector selecteren op basis van het veld ('A' of 'B')
            detector = self.switch_person_detector_field_a
        elif field =='B':
            detector = self.switch_person_detector_field_b
        peron_detection_result = not detector.value() # waarde meten van schakelaar
        if peron_detection_result:
            print("Person detected in the field")
        else:
            print("No person detected in the field")
        return peron_detection_result     # Retourneren of er wel of geen persoon wordt gedetecteerd in het veld (true of false)

    def scan_for_ferrometals(self):
        print("scan_for_ferrometals")
        metalsensorvalue = self.ferrometalscanner.read_u16()
        scaled_value = (metalsensorvalue / 65535) * 100 # Convert potentiometer value to a range between 0 and 100
        print("Potentiometer value:", scaled_value)
        if 0 <= scaled_value < 30:
            self.ferro_led.set_color("green")  # Green
            self.scanner_result = "NoMetalDetected"
        elif 30 <= scaled_value <= 80:
            self.scanner_result = "ScanInProgress"
            self.ferro_led.set_color("blue")
        elif 90 < scaled_value <= 100:
            self.scanner_result = "MetalDetected"
            self.ferro_led.set_color("red")  # Red
        return self.scanner_result

    def operate_door(self, door, action):
        door_function_map = {
            'open': door._open_door,
            'close': door._close_door
        }
        door_function_map[action]()
        return 0
    
    def handle_emergency_button_press(self, pin):
        print("handle_emergency_button_press")
        door1_action = door2_action = 'open'
        if pin == self.button_emergency_mri:
            print("Emergency button MRIRoom pressed")
            door2_action = 'close'
        elif pin == self.button_emergency_scanner:
            print("Emergency button ScannerRoom pressed")
            door1_action = 'close'
        self.operate_door(self.door1, door1_action)
        self.operate_door(self.door2, door2_action)
        self.lock_door1.set_color("blue") 
        self.lock_door2.set_color("blue") 
        self.ferro_led.set_color("blue") 
        self.emergency_state = True
        return 0

    # State machine
    def run(self):
        print("supertest2")
        self.state = self.INITIALISATION_STATE
        while True:
            if self.emergency_state:
                print("Emergency state triggered, stopping state machine after")
                break

            if self.button_door1_pressed:
                if self.state in [self.USER_FIELD_A_RESPONSE_STATE, self.SCAN_FOR_FERROMETALS]:
                    self.open_door(self.door1)
                    self.button_door1_pressed = False

            if self.button_door2_pressed:
                if self.state in [self.USER_FIELD_B_RESPONSE_STATE, self.scanner_result == "NoMetalDetected"]:
                    self.open_door(self.door2)
                    self.button_door2_pressed = False

            if self.state == self.INITIALISATION_STATE:
                if self.person_detected_in_field('A') == False and self.person_detected_in_field('B') == False:
                    if not self.initialized:
                        print("initialization")
                        self.lock_door1.off()  # Turn indicator off
                        self.lock_door2.off()  # Turn indicator off
                        self.ferro_led.off()  # Turn indicator off
                        self.door2._close_door()  
                        self.door1._close_door()  
                        self.initialized = True
                    self.state = self.USER_FIELD_A_RESPONSE_STATE

            elif self.state == self.USER_FIELD_A_RESPONSE_STATE:
                if self.person_detected_in_field('A') and not self.user_returned_from_mri:
                    self.close_door(self.door1)
                    self.state = self.SCAN_FOR_FERROMETALS
                elif self.user_returned_from_mri:
                    if self.person_detected_in_field('A'): 
                        self.user_returned_from_mri = False
                        self.open_door(self.door1)
                        self.state = self.INITIALISATION_STATE 


            elif self.state == self.USER_FIELD_B_RESPONSE_STATE:
                if self.scanner_result == "MetalDetected" and self.person_detected_in_field('B'):
                    self.open_door(self.door1)
                    self.state = self.INITIALISATION_STATE
                elif self.scanner_result == "NoMetalDetected" and self.person_detected_in_field('B') and self.user_returned_from_mri == False:
                    self.open_door(self.door2)
                    self.state = self.USER_IN_MRIROOM
                elif self.user_returned_from_mri == True and self.person_detected_in_field('B'):
                    self.state = self.close_door(self.door2)
                    self.state = self.USER_FIELD_A_RESPONSE_STATE

            elif self.state == self.SCAN_FOR_FERROMETALS:
                self.state = self.scan_for_ferrometals() 
                if self.scanner_result == "MetalDetected":
                    self.open_door(self.door1)
                    self.state = self.INITIALISATION_STATE
                elif self.scanner_result == "NoMetalDetected" and not self.person_detected_in_field('A'): # not metal and field A emtpy
                    self.open_door(self.door2)
                    self.state = self.USER_IN_MRIROOM
                elif self.scanner_result == "ScanInProgress" or self.person_detected_in_field('A') == True:
                    self.state = self.SCAN_FOR_FERROMETALS 

            elif self.state == self.USER_IN_MRIROOM:
                if self.person_detected_in_field('B') == True:
                    self.user_returned_from_mri = True
                    self.state = self.USER_FIELD_B_RESPONSE_STATE

            else:
                print("Invalid state")
                break
            time.sleep(0.5) # to prevent the state machine from running too fast

    def open_door(self, door):
        print(f"unlock_and_open_{door}")
        self.operate_door(door, 'open')
        return 0 # State Ran successfully

    def close_door(self, door):
        print(f"close_and_lock_{door}")
        self.operate_door(door, 'close')
        return 0 # State Ran successfully

if __name__ == "__main__":

    try:
        system_check = SystemInitCheck()  # Perform system check
        FDS = StateMachine()
        FDS.run()
    except SystemExit:
        print("System initialization failed. Exiting...")
    except Exception as e:
        print("An unexpected error occurred during initialization:", e)

