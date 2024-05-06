from hardware_s2g import LD2410PERSONDETECTOR, DOOR, WS2812
from system_utils import SystemInitCheck, Timer, USBCommunication, Log
from machine import Pin


global running   # system running global variable
running = False  # wait for system to be initialised before starting the state machine
global ferrometaldetected
ferrometaldetected = False  # Global variable to check if metal is detected

class StateMachine:
    def __init__(self):

        # StatemachineVariables
        self.state = None
        self.user_in_mri = False
        self.emergency_state_triggerd = False
        self.system_initialised = False
        self.system_override_state_triggerd = False
        self.user_returned_from_mri = False
        self.sensor_to_object_distance_threshold = 180 # distance threshold for person detection in cm
        self.audio_played = False  # Flag to track whether the audio has been played
        self.image_opened = False

        # Define integer constants for states
        self.INITIALISATION_STATE = 0
        self.USER_FIELD_A_RESPONSE_STATE = 1
        self.USER_FIELD_B_RESPONSE_STATE = 2
        self.USER_IN_MR_ROOM_STATE = 3
        self.USER_RETURNS_FROM_MR_ROOM_STATE = 4
        self.USER_EXITS_FDS_STATE = 5

        # Initialize indicator lights
        self.mmWaveFieldALEDS = WS2812(pin_number=2, num_leds=2, brightness=50)  # brigness is a value between 1 and 100
        self.mmWaveFieldBLEDS = WS2812(pin_number=3, num_leds=2, brightness=50)
        self.FerroDetectorLEDS = WS2812(pin_number=6, num_leds=2, brightness=50)

        # Initialize persondetectors
        self.mmWaveFieldA = LD2410PERSONDETECTOR(uart_number=0, baudrate=256000, tx_pin=0, rx_pin=1)
        self.mmWaveFieldB = LD2410PERSONDETECTOR(uart_number=1, baudrate=256000, tx_pin=4, rx_pin=5)

        # Initialize doors
        self.door1 = DOOR(pin_number=14, angle_closed=90, angle_open=0, position_sensor_pin=19)
        self.door2 = DOOR(pin_number=15, angle_closed=90, angle_open=185, position_sensor_pin=20)

        # Initialize buttons
        self.button_emergency = Pin(10, Pin.IN, Pin.PULL_UP)  # Emergency situation button
        self.button_emergency.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_emergencybutton_press)
        self.button_system_bypass = Pin(16, Pin.IN, Pin.PULL_UP)  # System override button
        self.button_system_bypass.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_bypassbutton_press)
        self.button_system_reset = Pin(17, Pin.IN, Pin.PULL_UP) # System bypass button
        self.button_system_reset.irq(trigger=Pin.IRQ_FALLING, handler= self.IRQ_handler_button_system_reset)
        #self.button_door1 = Pin(X, Pin.IN, Pin.PULL_UP)  # Door 1 button (open door)
        #self.button_door1.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_door1_button_press)
        #self.button_door2 = Pin(X, Pin.IN, Pin.PULL_UP)  # Door 2 button (open door)
        #self.button_door2.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_door2_button_press)

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
        self.RPI5_USB_LINE.send_message("Emergency button")  # Pass the message parameter
        self.RPI5_USB_LINE.send_message("showimage 7") # emergency situation image
        systemlog.log_message("Emergency button pressed")
        self.emergency_state_triggerd = True
        global running
        running = False # stop the state machine

    def IRQ_handler_button_system_reset(self, pin):
        self.RPI5_USB_LINE.send_message("System reset button")  # Pass the message parameter
        systemlog.log_message("System reset button pressed")
        self.system_initialised = False
        self.system_override_state_triggerd = False
        self.emergency_state_triggerd = False
        self.state = self.INITIALISATION_STATE
        global running 
        running = True # start the state machine

    def IRQ_handler_bypassbutton_press(self, pin):
        self.RPI5_USB_LINE.send_message("Override button pressed")
        self.RPI5_USB_LINE.send_message("showimage 8") # system override image 
        systemlog.log_message("System override button pressed")
        self.emergency_state_triggerd = False
        self.system_override_state_triggerd = not self.system_override_state_triggerd # toggle system override state
        global running
        running = False # toggle statemachine running state

    def IRQ_handler_ferrometal_detected(self, pin):
        global ferrometaldetected
        self.RPI5_USB_LINE.send_message("Ferrometalscanner detected metal")
        systemlog.log_message("Ferrometalscanner detected metal")
        ferrometaldetected = True

    def person_detected_in_field(self, field): 
        if field == 'A':
            if self.mmWaveFieldA.scan_for_people() and self.mmWaveFieldA.get_detection_distance() < self.sensor_to_object_distance_threshold:
                self.mmWaveFieldALEDS.set_color("green")
                return True
            else:
                self.mmWaveFieldALEDS.set_color("red")
                return False
        elif field == 'B':
            if self.mmWaveFieldB.scan_for_people() and self.mmWaveFieldB.get_detection_distance() < self.sensor_to_object_distance_threshold:
                self.mmWaveFieldBLEDS.set_color("green")
                return True
            else:
                self.mmWaveFieldBLEDS.set_color("red")
                return False

    def systemset(self):
        self.mmWaveFieldALEDS.off()
        self.mmWaveFieldBLEDS.off()
        self.FerroDetectorLEDS.off() 
        self.door2.close_door()  
        self.door1.open_door()  
        self.system_initialised = True
        self.RPI5_USB_LINE.send_message("System initialised")
        self.RPI5_USB_LINE.send_message("playaudio 1") # system initialised audio

    def run(self):
        global ferrometaldetected
        global running 
        self.state = self.INITIALISATION_STATE # default state when statemachine is started
        # print("Loop restarted")
        while running: 
            if self.state == self.INITIALISATION_STATE:
                if self.system_initialised == False:
                    self.systemset()
                elif not self.image_opened:
                    self.RPI5_USB_LINE.send_message("showimage 0")
                    self.image_opened = True
                elif not self.audio_played :
                    self.RPI5_USB_LINE.send_message("playaudio 4")  
                    self.audio_played = True   
                elif self.person_detected_in_field('A') == False and self.person_detected_in_field('B') == False:
                    self.RPI5_USB_LINE.send_message("closeimage") # close all images
                    self.audio_played = False 
                    self.image_opened = False
                    self.door1.open_door()
                    ferrometaldetected = False
                    self.state = self.USER_FIELD_A_RESPONSE_STATE
                    self.RPI5_USB_LINE.send_message("showimage 1")  # move to field A image

            elif self.state == self.USER_FIELD_A_RESPONSE_STATE:
                if not self.audio_played:
                    self.RPI5_USB_LINE.send_message("playaudio 5") # move to field A audio 
                    self.audio_played = True  # Set the flag to indicate that audio has been played  
                if self.person_detected_in_field('A') == True and self.person_detected_in_field('B') == False: 
                    self.audio_played = False 
                    self.door1.close_door()
                    self.RPI5_USB_LINE.send_message("showimage 2") # move to field B image
                    self.RPI5_USB_LINE.send_message("playaudio 6") # move to field B audio
                    if ferrometaldetected == True:
                        if not self.image_opened:
                            self.RPI5_USB_LINE.send_message("showimage 4") # metal detected image
                            self.image_opened = True
                        if not self.audio_played:
                            self.RPI5_USB_LINE.send_message("playaudio 9")  
                            self.audio_played = True  # Set the flag to indicate that audio has been played   
                        self.door1.open_door()
                    if self.person_detected_in_field('B') == False and self.person_detected_in_field('A') == False and ferrometaldetected == True:
                        self.image_opened = False
                        self.state = self.INITIALISATION_STATE
                    elif ferrometaldetected == False:
                        self.image_opened = False
                        self.state = self.USER_FIELD_B_RESPONSE_STATE
                elif self.person_detected_in_field('A') == False and self.person_detected_in_field('B') == True:
                    # Wait for user to move to field A
                    return 0

            elif self.state == self.USER_FIELD_B_RESPONSE_STATE:
                if self.person_detected_in_field('B') == True and self.person_detected_in_field('A') == False and ferrometaldetected == False:
                    self.RPI5_USB_LINE.send_message("showimage 3") # move to MR room image
                    self.RPI5_USB_LINE.send_message("playaudio 8") # you may proceed to MR room audio
                    self.door2.open_door()
                    self.FerroDetectorLEDS.set_color("green")
                    self.state = self.USER_IN_MR_ROOM_STATE
                elif ferrometaldetected == True:
                    if not self.image_opened:
                        self.RPI5_USB_LINE.send_message("showimage 4") # metal detected image
                        self.image_opened = True
                    self.door1.open_door()
                    self.FerroDetectorLEDS.set_color("red")
                    if not self.audio_played :
                        self.RPI5_USB_LINE.send_message("playaudio 9")  
                        self.audio_played = True  # Set the flag to indicate that audio has been played   
                    if self.person_detected_in_field('B') == False and self.person_detected_in_field('A') == False and ferrometaldetected == True:
                        self.image_opened = False
                        self.state = self.INITIALISATION_STATE
                else:
                    self.FerroDetectorLEDS.set_color("yellow")

            elif self.state == self.USER_IN_MR_ROOM_STATE:
                if self.person_detected_in_field('B') == False and self.person_detected_in_field('A') == False:
                    self.RPI5_USB_LINE.send_message("showimage 5") # wait for return from MR room image
                    self.state = self.USER_RETURNS_FROM_MR_ROOM_STATE

            elif self.state == self.USER_RETURNS_FROM_MR_ROOM_STATE:
                if self.person_detected_in_field('B') == True or self.person_detected_in_field('A') == True:
                    self.RPI5_USB_LINE.send_message("showimage 6") # exit to change room image
                    self.RPI5_USB_LINE.send_message("playaudio 10") # exit to change room audio      
                    self.door2.close_door()
                    self.state = self.USER_EXITS_FDS_STATE
            
            elif self.state == self.USER_EXITS_FDS_STATE:
                if self.person_detected_in_field('B') == False and self.person_detected_in_field('A') == True: 
                    self.door1.open_door()
                    self.state = self.INITIALISATION_STATE

            else:
                self.freeze()

    def freeze(self):
        global running
        if running == False and self.system_override_state_triggerd == True: # override system
            #print("System is bypassed")
            self.FerroDetectorLEDS.set_color("white")
            self.mmWaveFieldALEDS.set_color("white")
            self.mmWaveFieldBLEDS.set_color("white")
            self.door1.open_door()
            self.door2.open_door() 
            self.emergency_state_triggerd = False
        elif running == False and self.emergency_state_triggerd == True and self.system_override_state_triggerd == False: # emergency system
            #print("Emergency triggerd")
            self.FerroDetectorLEDS.set_color("yellow")
            self.mmWaveFieldALEDS.set_color("yellow")
            self.mmWaveFieldBLEDS.set_color("yellow")
            self.door1.open_door()
            self.door2.open_door() 


if __name__ == "__main__":
    running = True
    systemlog = Log()
    systemlog.open_log()
    FDS = StateMachine()
    try:
        SystemInitCheck().systemcheck()
        while True:
            if running:  
                FDS.run()
            else:
                FDS.freeze() 

    except SystemExit as s:
        running = False
        USBCommunication.send_message(FDS.RPI5_USB_LINE, "System failed to initialise")
        systemlog.log_message("System failed to initialise")
        systemlog.close_log()

    except Exception as e:
        running = False
        USBCommunication.send_message(FDS.RPI5_USB_LINE, "System encountered unexpected error")
        systemlog.log_message("System encountered unexpected error")
        systemlog.close_log()
