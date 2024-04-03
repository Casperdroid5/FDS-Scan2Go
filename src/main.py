from hardware_s2g import PERSONDETECTOR, DOORWITHLED, WS2812
from system_utils import SystemInitCheck
from machine import Pin, RTC
import time


global running   # System running global variable
running = False  # wait for system to be initialised before starting the state machine
rtc = RTC()      # init on-board RTC
global ferrometaldetected
ferrometaldetected = False  # Global variable to check if metal is detected

# File to log the system events
file = open("log.txt", "w")  # open the file in write mode:

class StateMachine:
    def __init__(self):

        # StatemachineVariables
        self.user_in_mri = False
        self.emergency_state_triggerd = False
        self.system_initialised = False
        self.system_override_state_triggerd = False
        self.user_returned_from_mri = False

        # Define the initial state of the state machine
        self.state = None

        # Define integer constants for states
        self.INITIALISATION_STATE = 0
        self.USER_FIELD_A_RESPONSE_STATE = 1
        self.USER_FIELD_B_RESPONSE_STATE = 2
        self.USER_IN_MR_ROOM = 3
        self.USER_RETURNS_FROM_MR_ROOM = 4
        self.USER_EXITS_FDS = 5
        
        # Initialize indicator lights
        self.door1_leds = WS2812(pin_number=2, num_leds=2, brightness=0.0005)  # brigness is a value between 0.0001 and 1
        self.door2_leds = WS2812(pin_number=3, num_leds=2, brightness=0.0005)
        self.ferro_leds = WS2812(pin_number=4, num_leds=2, brightness=0.0005)

        # Initialize doors with LEDs
        self.door1 = DOORWITHLED(door_pin_number=14, door_angle_closed=90, door_angle_open=0, door_position_sensor_pin=19, led_pin_number=2, num_leds=2, brightness=0.0005)
        self.door2 = DOORWITHLED(door_pin_number=15, door_angle_closed=90, door_angle_open=185, door_position_sensor_pin=20, led_pin_number=3, num_leds=2, brightness=0.0005)


        # Initialize persondetectors
        self.mmWaveFieldA = PERSONDETECTOR(uart_number=0, baudrate=115200, tx_pin=0, rx_pin=1)
        self.mmWaveFieldB = PERSONDETECTOR(uart_number=1, baudrate=115200, tx_pin=4, rx_pin=5)

        # Initialize buttons
        self.button_emergency = Pin(10, Pin.IN, Pin.PULL_UP)
        self.button_emergency.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_emergencybutton_press)  # Emergency situation button
        self.button_system_override = Pin(16, Pin.IN, Pin.PULL_UP)  # System override button
        self.button_system_override.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_overridebutton_press)
        self.button_door1 = Pin(21, Pin.IN, Pin.PULL_UP)  # Door 1 button (open door)
        self.button_door1.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_door1_button_press)
        self.button_door2 = Pin(17, Pin.IN, Pin.PULL_UP)  # Door 2 button (open door)
        self.button_door2.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_door2_button_press)
        
        # Initialize ferrometal scanner
        self.ferrometalscanner = Pin(18, Pin.IN, Pin.PULL_UP)
        self.ferrometalscanner.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_ferrometal_detected)

    def log(self, message):
        if file:
            print("Logging: ", message)
            timestamp = rtc.datetime()		# Timeregistration
            timestring = "%04d-%02d-%02d %02d:%02d:%02d.%03d" % timestamp[:7] 
            file.write(timestring + "," + message + "\n")		# Write time and message to the file
            file.flush()  # Write the data immediately to the file

    def IRQ_handler_door1_button_press(self, pin):
        if self.state == self.USER_FIELD_A_RESPONSE_STATE:
            if self.door1.door_state == "closed": # check if door is open
                self.door1.open_door()  
                self.log("Door 1 button pressed.")

    def IRQ_handler_door2_button_press(self, pin):
        if self.state == self.USER_IN_MR_ROOM or (ferrometaldetected == "NoMetalDetected" and self.user_returned_from_mri) or self.user_in_mri:
            if self.door2.door_state == "closed":
                self.door2.open_door()  
                self.log("Door 2 button pressed.")

    def IRQ_handler_emergencybutton_press(self, pin):
        self.log("Emergency button pressed.")
        print("Emergency button pressed")
        self.door1.open_door()
        self.door2.open_door() 
        self.door1_leds.set_color("yellow")
        self.door2_leds.set_color("yellow")
        self.ferro_leds.set_color("yellow")
        self.emergency_state_triggerd = True
        global running
        running = False # stop the state machine
        self.freeze()
        return 0

    def IRQ_handler_overridebutton_press(self, pin):
        self.log("System override button pressed.")
        print("System override button pressed")
        self.door1.open_door()
        self.door2.open_door()  
        self.door1_leds.set_color("white")
        self.door2_leds.set_color("white")
        self.ferro_leds.set_color("white")
        global running
        self.system_override_state_triggerd = not self.system_override_state_triggerd # toggle system override state
        running = not running # toggle statemachine running state
        self.freeze()
        return 0

    def IRQ_handler_ferrometal_detected(self, pin):
        global ferrometaldetected
        self.log("Ferrometalscanner detected metal.")
        print("Ferrometalscanner detected metal")
        ferrometaldetected = True

    def person_detected_in_field(self, field):
        print(f"Checking for person in field {field}")
        user_input = input("Enter 'True' if person detected, 'False' otherwise: ").strip().lower()

        if user_input == 'true':
            return True
        elif user_input == 'false':
            return False
        else:
            print("Invalid input. Please enter 'True' or 'False'.")
            return False
        
        #mmWave code disabled for testing purposes
        # print(f"Checking for person in field {field}")
        # if field == 'A':
        #     self.mmWaveFieldA.check_humanpresence()
        #     print(self.mmWaveFieldA.humanpresence) # for debugging purposes
        #     if self.mmWaveFieldA.humanpresence == "Somebodymoved":
        #         return True
        #     elif self.mmWaveFieldA.humanpresence == "Somebodystoppedmoving":
        #         return False
        # elif field == 'B':
        #     self.mmWaveFieldB.check_humanpresence()
        #     if self.mmWaveFieldB.humanpresence == "Sombodymoved":
        #         return True
        #     elif self.mmWaveFieldB.humanpresence == "Somebodystoppedmoving":   
        #         return False

    def systemset (self):
        print("FIRST initialization")
        self.door1_leds.off()
        self.door2_leds.off()
        self.ferro_leds.off() 
        self.door2.close_door()  
        self.door1.close_door()  
        return 0

# State machine
    def run(self):
        
        global ferrometaldetected
        global running 
        
        while running: 
            if self.state == self.INITIALISATION_STATE:
                if self.person_detected_in_field('A') == False and self.person_detected_in_field('B') == False:
                    ferrometaldetected = False
                    self.door1.open_door()
                    if self.system_initialised == False:
                        self.systemset()
                self.state = self.USER_FIELD_A_RESPONSE_STATE

            elif self.state == self.USER_FIELD_A_RESPONSE_STATE:
                print ("ferrometal detected: ")
                print (ferrometaldetected)
                if self.person_detected_in_field('A') == True and self.person_detected_in_field('B') == False: 
                    self.door1.close_door()
                    if ferrometaldetected == True:
                        self.door1.open_door()
                        print("Metal detected, please remove metal objects")
                        self.state = self.INITIALISATION_STATE
                    elif ferrometaldetected == False:
                        print("No metal detected, please proceed to field B")
                        self.state = self.USER_FIELD_B_RESPONSE_STATE
                elif self.person_detected_in_field('A') == False and self.person_detected_in_field('B') == True:
                    print("please position yourself in field A, before the scanner")

            elif self.state == self.USER_FIELD_B_RESPONSE_STATE:
                if self.person_detected_in_field('B') == True and self.person_detected_in_field('A') == False and ferrometaldetected == False:
                    self.door2.open_door()
                    self.state = self.USER_IN_MR_ROOM
                elif ferrometaldetected == True:
                    self.door1.open_door()
                    print("Metal detected, please remove metal objects")
                    self.state = self.INITIALISATION_STATE
                else:
                    self.scanner_result = "invalidState"
                    self.ferro_leds.set_color("yellow")
                    print("invalid state ferroscanner")
                    self.state = self.INITIALISATION_STATE

            elif self.state == self.USER_IN_MR_ROOM:
                if self.person_detected_in_field('B') == False:
                    self.state = self.USER_RETURNS_FROM_MR_ROOM

            elif self.state == self.USER_RETURNS_FROM_MR_ROOM:
                if self.person_detected_in_field('B') == True:
                    self.door2.close_door()
                    self.state = self.USER_EXITS_FDS
            
            elif self.state == self.USER_EXITS_FDS:
                if self.person_detected_in_field('B') == False and self.person_detected_in_field('A') == True: 
                    self.door1.open_door()
                    self.state = self.INITIALISATION_STATE

            else:
                print("Invalid state, create emergency request")
                self.log("Invalid state, create emergency request")
                self.freeze()
            time.sleep(0.5) # to prevent the state machine from running too fast

    def freeze(self):
        global running
        if running == True:
            self.system_initialised = False
            print("SYSTEM IS NO LONGER FROZEN")
            print("Enter text to continue")
            self.state = self.INITIALISATION_STATE
            return 0
        elif running == False and self.system_override_state_triggerd == True: # System override for emergency button (reset)
            print("SYSTEM IS FROZEN")
            self.emergency_state_triggerd = False
            self.system_override_state_triggerd = False
            return 0

if __name__ == "__main__":

        running = True

        rtc.datetime((2024, 4, 2, 1, 0, 0, 0, 0)) # set a specific date and time for the RTC (year, month, day, weekday, hours, minutes, seconds, subseconds)
        print(rtc.datetime())

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





