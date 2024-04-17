from hardware_s2g import LD2410PERSONDETECTOR, DOORWITHLED, WS2812
from system_utils import SystemInitCheck, Timer, USBCommunication
from machine import Pin

global running   # system running global variable
running = False  # wait for system to be initialised before starting the state machine
global ferrometaldetected
ferrometaldetected = False  # Global variable to check if metal is detected

class StateMachine:
    def __init__(self):

        # StatemachineVariables
        self.user_in_mri = False
        self.emergency_state_triggerd = False
        self.system_initialised = False
        self.system_override_state_triggerd = False
        self.user_returned_from_mri = False
        self.sensor_to_object_distance_threshold = 180 # distance threshold for person detection in cm

        # Define the initial state of the state machine
        self.state = None

        # Define integer constants for states
        self.INITIALISATION_STATE = 0
        self.USER_FIELD_A_RESPONSE_STATE = 1
        self.USER_FIELD_B_RESPONSE_STATE = 2
        self.USER_IN_MR_ROOM_STATE = 3
        self.USER_RETURNS_FROM_MR_ROOM_STATE = 4
        self.USER_EXITS_FDS_STATE = 5

        # Initialize indicator lights
        self.door1_leds = WS2812(pin_number=2, num_leds=2, brightness=0.0005)  # brigness is a value between 0.0001 and 1
        self.door2_leds = WS2812(pin_number=3, num_leds=2, brightness=0.0005)
        self.ferro_leds = WS2812(pin_number=6, num_leds=2, brightness=0.0005)

        # Initialize doors with LEDs
        self.door1 = DOORWITHLED(door_pin_number=14, door_angle_closed=90, door_angle_open=0, door_position_sensor_pin=19, led_pin_number=2, num_leds=2, brightness=0.0005)
        self.door2 = DOORWITHLED(door_pin_number=15, door_angle_closed=90, door_angle_open=185, door_position_sensor_pin=20, led_pin_number=3, num_leds=2, brightness=0.0005)

        # Initialize persondetectors
        self.mmWaveFieldA = LD2410PERSONDETECTOR(uart_number=1, baudrate=256000, tx_pin=4, rx_pin=5)
        self.mmWaveFieldB = LD2410PERSONDETECTOR(uart_number=0, baudrate=256000, tx_pin=0, rx_pin=1)

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

        # Initialize UART-communication with RPI5
        self.RPI5_USB_LINE = USBCommunication()

        # Initialize the timer
        self.FDStimer = Timer()  
        self.FDStimer.start_timer() # Start the timer 

    def IRQ_handler_door1_button_press(self, pin):
        if self.state == self.USER_FIELD_A_RESPONSE_STATE:
            if self.door1.door_state == "closed": # check if door is open
                self.door1.open_door() 

    def IRQ_handler_door2_button_press(self, pin):
        if self.state == self.USER_IN_MR_ROOM_STATE or (ferrometaldetected == "NoMetalDetected" and self.user_returned_from_mri) or self.user_in_mri:
            if self.door2.door_state == "closed":
                self.door2.open_door()  

    def IRQ_handler_emergencybutton_press(self, pin):
        #print("Emergency button pressed")
        self.RPI5_USB_LINE.send_message( "Emergency button")  # Pass the message parameter
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
        #print("System override button pressed")
        self.RPI5_USB_LINE.send_message("Override button pressed")
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
        #print("Ferrometalscanner detected metal")
        ferrometaldetected = True

    def person_detected_in_field(self, field): 
            #print(f"Checking for person in field {field}")
            if field == 'A':
                if self.mmWaveFieldA.scan_for_people() and self.mmWaveFieldA.get_detection_distance() < self.sensor_to_object_distance_threshold:
                    #print("Person detected in field A")
                    return True
                else:
                    #print("No person detected in field A")
                    return False
            elif field == 'B':
                if self.mmWaveFieldB.scan_for_people() and self.mmWaveFieldB.get_detection_distance() < self.sensor_to_object_distance_threshold:
                    ##print("Person detected in field B")
                    return True
                else:
                    #print("No person detected in field B")
                    return False

    def systemset (self):
        #print("FIRST initialization")
        self.door1_leds.off()
        self.door2_leds.off()
        self.ferro_leds.off() 
        self.door2.close_door()  
        self.door1.open_door()  
        #print(self.FDStimer.get_time())
        #print("system initialised")
        self.RPI5_USB_LINE.send_message("RPI, are you awake?")
        if self.RPI5_USB_LINE.receive_message() == "Yes":
            self.system_initialised = True
            self.RPI5_USB_LINE.send_message("System initialised")
            return 0

# State machine
    def run(self):
        
        global ferrometaldetected
        global running 

        while running: 
            if self.state == self.INITIALISATION_STATE:
                #print("INITIALISATION_STATE")
                self.RPI5_USB_LINE.send_message("System initialised") # Send message to RPI5
                self.RPI5_USB_LINE.send_message( "showimage1") # Show image on RPI5
                if self.person_detected_in_field('A') == False and self.person_detected_in_field('B') == False:
                    self.door1.open_door()
                    ferrometaldetected = False
                    self.ferro_leds.off()
                    self.state = self.USER_FIELD_A_RESPONSE_STATE
                    if self.system_initialised == False:
                        self.systemset()

            elif self.state == self.USER_FIELD_A_RESPONSE_STATE:
                #print("USER_FIELD_A_RESPONSE_STATE")
                if self.person_detected_in_field('A') == True and self.person_detected_in_field('B') == False: 
                    self.door1.close_door()
                    if ferrometaldetected == True:
                        self.door1.open_door()
                        #print("Metal detected, please remove metal objects")
                        self.state = self.INITIALISATION_STATE
                    elif ferrometaldetected == False:
                        #print("No metal detected, please proceed to field B")
                        self.state = self.USER_FIELD_B_RESPONSE_STATE
                elif self.person_detected_in_field('A') == False and self.person_detected_in_field('B') == True:
                    #print("Please position in field A, before the scanner")
                    return 0

            elif self.state == self.USER_FIELD_B_RESPONSE_STATE:
                #print("USER_FIELD_B_RESPONSE_STATE")
                if self.person_detected_in_field('B') == True and self.person_detected_in_field('A') == False and ferrometaldetected == False:
                    self.door2.open_door()
                    self.ferro_leds.set_color("green")
                    self.state = self.USER_IN_MR_ROOM_STATE
                    #print("No metal detected, please proceed to MR room")
                elif ferrometaldetected == True:
                    self.door1.open_door()
                    self.ferro_leds.set_color("red")
                    #print("Metal detected, please remove metal objects")
                    self.state = self.INITIALISATION_STATE
                else:
                    self.ferro_leds.set_color("yellow")
                    #print("person in field A and B detected, please remove person from field A")

            elif self.state == self.USER_IN_MR_ROOM_STATE:
                #print("USER_IN_MR_ROOM_STATE")
                if self.person_detected_in_field('B') == False and self.person_detected_in_field('A') == False:
                    self.state = self.USER_RETURNS_FROM_MR_ROOM_STATE

            elif self.state == self.USER_RETURNS_FROM_MR_ROOM_STATE:
                #print("USER_RETURNS_FROM_MR_ROOM_STATE")
                if self.person_detected_in_field('B') == True or self.person_detected_in_field('A') == True:
                    self.door2.close_door()
                    self.state = self.USER_EXITS_FDS_STATE
            
            elif self.state == self.USER_EXITS_FDS_STATE:
                #print("USER_EXITS_FDS_STATE")
                if self.person_detected_in_field('B') == False and self.person_detected_in_field('A') == True: 
                    self.door1.open_door()
                    self.state = self.INITIALISATION_STATE

            else:
                #print("Invalid state, create emergency request")
                self.freeze()

    def freeze(self):
        global running
        if running == True:
            self.system_initialised = False
            #print("SYSTEM IS NO LONGER FROZEN")
            #print("Enter text to continue")
            self.state = self.INITIALISATION_STATE
            return 0
        elif running == False and self.system_override_state_triggerd == True: # System override for emergency button (reset)
            #print("SYSTEM IS FROZEN")
            self.emergency_state_triggerd = False
            self.system_override_state_triggerd = False
            self.state = self.INITIALISATION_STATE
            return 0

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
            #print("Systeeminit failed, shutting down...")
            USBCommunication.send_message(FDS.RPI5_USB_LINE, "System failed to initialise")
        except Exception as e:
            #print("unexpected error", e)
            USBCommunication.send_message(FDS.RPI5_USB_LINE, "System encountered unexpected error")



