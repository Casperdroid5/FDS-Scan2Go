from hardware_s2g import DOOR, PERSONDETECTOR, WS2812
from system_utils import SystemInitCheck
from machine import Pin, ADC
import time

# System running global variable
global running
running = False  


class StateMachine:
    def __init__(self):

        # StatemachineVariables
        self.scanner_result = "ScanInProgress"
        self.user_returned_from_mri = False
        self.user_in_mri = False
        self.emergency_state_triggerd = False
        self.system_initialised = False
        self.system_override_state_triggerd = False

        # Define integer constants for states
        self.INITIALISATION_STATE = 0
        self.USER_FIELD_A_RESPONSE_STATE = 1
        self.USER_FIELD_B_RESPONSE_STATE = 2
        self.SCAN_FOR_FERROMETALS = 3
        self.USER_IN_MR_ROOM = 4
        self.EMERGENCY_STATE = 5

        # Initialize indicator lights
        self.lock_door1 = WS2812(pin_number=2, num_leds=2, brightness=0.05) # brigness is a value between 0.0001 and 1
        self.lock_door2 = WS2812(pin_number=3, num_leds=2, brightness=0.05)
        self.ferro_led = WS2812(pin_number=4, num_leds=2, brightness=0.05)

        # Initialize doors
        self.door1 = DOOR(pin_number=14, angle_closed=90, angle_open=0, position_sensor_pin=19) 
        self.door2 = DOOR(pin_number=15, angle_closed=90, angle_open=185, position_sensor_pin=20)

        # Initialize ferrometal scanner
        self.ferrometalscanner = ADC(Pin(27))

        # Initialize persondetectors
        self.mmWaveFieldA = PERSONDETECTOR(uart_number=0, baudrate=115200, tx_pin=0, rx_pin=1)
        self.mmWaveFieldB = PERSONDETECTOR(uart_number=1, baudrate=115200, tx_pin=4, rx_pin=5)

        # Initialize buttons
        self.button_emergency = Pin(10, Pin.IN, Pin.PULL_UP)
        self.button_emergency.irq(trigger=Pin.IRQ_FALLING, handler=self.handle_override_buttons) # Emergency situation button
        self.button_system_override = Pin(16, Pin.IN, Pin.PULL_UP)  # System override button
        self.button_system_override.irq(trigger=Pin.IRQ_FALLING, handler=self.handle_override_buttons)
        self.button_door1 = Pin(21, Pin.IN, Pin.PULL_UP)  # Door 1 button (open door)
        self.button_door1.irq(trigger=Pin.IRQ_FALLING, handler=self.handle_door1_button_press)
        self.button_door2 = Pin(17, Pin.IN, Pin.PULL_UP)  # Door 2 button (open door)
        self.button_door2.irq(trigger=Pin.IRQ_FALLING, handler=self.handle_door2_button_press)

    def handle_door1_button_press(self, pin):
        if self.state == self.USER_FIELD_A_RESPONSE_STATE or self.state == self.SCAN_FOR_FERROMETALS: 
            if self.door1.door_state == "closed": # check if door is open
                self.door1.open_door()  

    def handle_door2_button_press(self, pin):
        if self.state == self.USER_IN_MR_ROOM or (self.scanner_result == "NoMetalDetected" and self.user_returned_from_mri) or self.user_in_mri:
            if self.door2.door_state == "closed":
                self.door2.open_door()  

    def person_detected_in_field(self, field):
        print(f"Checking for person in field {field}")
        user_input = input("Enter 'True' if person detected, 'False' otherwise: ").strip().lower()

        if user_input == 'true':
            return True
        elif user_input == 'false':
            return False
        else:
            print("Invalid input. Please enter 'True' or 'False'.")
            # Als de invoer ongeldig is, retourneer False om aan te geven dat er geen persoon is gedetecteerd.
            return False
        
        #mmWave code disabled for testing purposes
        # print(f"Checking for person in field {field}")
        # if field == 'A':
        #     self.mmWaveFieldA.poll_uart_data()
        #     print(self.mmWaveFieldA.humanpresence) # for debugging purposes
        #     if self.mmWaveFieldA.humanpresence == "Somebodymoved":
        #         return True
        #     elif self.mmWaveFieldA.humanpresence == "Somebodystoppedmoving":
        #         return False
        # elif field == 'B':
        #     self.mmWaveFieldB.poll_uart_data()
        #     if self.mmWaveFieldB.humanpresence == "Sombodymoved":
        #         return True
        #     elif self.mmWaveFieldB.humanpresence == "Somebodystoppedmoving":   
        #         return False

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

    def handle_override_buttons(self, pin):
        if pin == self.button_emergency:
            print("Emergency button pressed")
            self.door1.open_door()
            self.door2.open_door() 
            self.lock_door1.set_color("yellow")
            self.lock_door2.set_color("yellow")
            self.ferro_led.set_color("yellow")
            self.emergency_state_triggerd = True
            global running
            self.emergency_state_triggerd = not self.emergency_state_triggerd
            running = False
            self.freeze()
        elif pin == self.button_system_override:
            print("System override button pressed")
            self.door1.open_door()
            self.door2.open_door()  
            self.lock_door1.set_color("white")
            self.lock_door2.set_color("white")
            self.ferro_led.set_color("white")
            global running
            self.system_override_state_triggerd = not self.system_override_state_triggerd
            running = not running
            self.freeze()

        return 0

# State machine
    def run(self):

        global running 

        while running: 
            if self.state == self.INITIALISATION_STATE:
                print("initialization")
                if self.person_detected_in_field('A') == False and self.person_detected_in_field('B') == False:
                    self.door1.open_door()
                    if not self.system_initialised:
                        print("First initialization")
                        self.lock_door1.off()
                        self.lock_door2.off()
                        self.ferro_led.off() 
                        self.door2.close_door()  
                        self.door1.close_door()  
                        self.system_initialised = True
                    self.state = self.USER_FIELD_A_RESPONSE_STATE

            elif self.state == self.USER_FIELD_A_RESPONSE_STATE:
                if self.person_detected_in_field('A') == True and not self.user_returned_from_mri:
                    self.door1.close_door()  
                    self.state = self.SCAN_FOR_FERROMETALS
                elif self.user_returned_from_mri == True:
                    if self.person_detected_in_field('A') == True and self.person_detected_in_field('B') == False: 
                        self.user_returned_from_mri = False
                        self.door2.close_door()  
                        self.door1.open_door()  
                        self.state = self.INITIALISATION_STATE 

            elif self.state == self.USER_FIELD_B_RESPONSE_STATE:
                if self.scanner_result == "MetalDetected" and self.person_detected_in_field('B'):
                    self.state = self.INITIALISATION_STATE
                elif self.scanner_result == "NoMetalDetected" and self.person_detected_in_field('B') == True and self.user_returned_from_mri == False:
                    self.door2.open_door()  
                    self.state = self.USER_IN_MR_ROOM
                elif self.user_returned_from_mri == True and self.person_detected_in_field('B') == True:
                    self.door2.close_door()  
                    self.state = self.USER_FIELD_A_RESPONSE_STATE

            elif self.state == self.SCAN_FOR_FERROMETALS:
                self.scan_for_ferrometals()
                if self.scanner_result == "MetalDetected":
                    self.door1.open_door()  
                    if self.person_detected_in_field('A') == False and self.person_detected_in_field('B') == False:
                        self.state = self.INITIALISATION_STATE
                elif self.scanner_result == "NoMetalDetected" and self.person_detected_in_field('A') == False and self.person_detected_in_field('B') == True:
                    self.door2.open_door()  
                    self.state = self.USER_IN_MR_ROOM
                elif self.scanner_result == "ScanInProgress" or self.person_detected_in_field('A') == True:
                    self.state = self.SCAN_FOR_FERROMETALS 

            elif self.state == self.USER_IN_MR_ROOM:
                if self.person_detected_in_field('B') == False:
                    self.user_in_mri = True
                if self.person_detected_in_field('B') == True and self.user_in_mri == True:
                    self.user_in_mri = False
                    self.user_returned_from_mri = True
                    self.state = self.USER_FIELD_B_RESPONSE_STATE

            else:
                print("Invalid state, exiting...")
                break
            time.sleep(0.5) # to prevent the state machine from running too fast

    def freeze(self):
        global running
        if running == True:
            self.system_initialised = False
            self.state = self.INITIALISATION_STATE
        if running == False and self.system_override_state_triggerd == True: # System override for emergency button (reset)
            self.emergency_state_triggerd = False
            self.system_override_state_triggerd = False
            self.state = self.INITIALISATION_STATE


if __name__ == "__main__":
    running = True
    try:
        system_check = SystemInitCheck()
        FDS = StateMachine()
        FDS.state = FDS.INITIALISATION_STATE
        
        while True:
            if running:  
                FDS.run()
            else:
                FDS.freeze() 

    except SystemExit:
        print("Systeeminit failed, shutting down...")
    except Exception as e:
        print("unexpected error", e)

