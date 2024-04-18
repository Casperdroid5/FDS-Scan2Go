from hardware_s2g import LD2410PERSONDETECTOR, DOOR, WS2812
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
        self.mmWaveFieldALEDS = WS2812(pin_number=2, num_leds=2, brightness=0.0005)  # brigness is a value between 0.0001 and 1
        self.mmWaveFieldBLEDS = WS2812(pin_number=3, num_leds=2, brightness=0.0005)
        self.FerroDetectorLEDS = WS2812(pin_number=6, num_leds=2, brightness=0.0005)

        # Initialize persondetectors
        self.mmWaveFieldA = LD2410PERSONDETECTOR(uart_number=1, baudrate=256000, tx_pin=4, rx_pin=5)
        self.mmWaveFieldB = LD2410PERSONDETECTOR(uart_number=0, baudrate=256000, tx_pin=0, rx_pin=1)
        
        # Initialize doors
        self.door1 = DOOR(pin_number=14, angle_closed=90, angle_open=0, position_sensor_pin=19)
        self.door2 = DOOR(pin_number=15, angle_closed=90, angle_open=185, position_sensor_pin=20)

        # Initialize buttons
        self.button_emergency = Pin(10, Pin.IN, Pin.PULL_UP)  # Emergency situation button
        self.button_emergency.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_emergencybutton_press)
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

        # Variable to track if an image is currently open
        self.image_opened = False

        # Variable to track if audio is currently playing
        self.audio_playing = False

    def IRQ_handler_door1_button_press(self, pin):
        if self.state == self.USER_FIELD_A_RESPONSE_STATE:
            if self.door1.door_state == "closed": # check if door is open
                self.door1.open_door() 

    def IRQ_handler_door2_button_press(self, pin):
        if self.state == self.USER_IN_MR_ROOM_STATE or (ferrometaldetected == "NoMetalDetected" and self.user_returned_from_mri) or self.user_in_mri:
            if self.door2.door_state == "closed":
                self.door2.open_door()  

    def IRQ_handler_emergencybutton_press(self, pin):
        self.RPI5_USB_LINE.send_message( "Emergency button")  # Pass the message parameter
        self.door1.open_door()
        self.door2.open_door() 
        self.FerroDetectorLEDS.set_color("yellow")
        self.emergency_state_triggerd = True
        global running
        running = False # stop the state machine
        self.freeze()
        return 0

    def IRQ_handler_overridebutton_press(self, pin):
        self.RPI5_USB_LINE.send_message("Override button pressed")
        self.door1.open_door()
        self.door2.open_door()  
        self.mmWaveFieldALEDS.set_color("white")
        self.mmWaveFieldBLEDS.set_color("white")
        self.FerroDetectorLEDS.set_color("white")
        global running
        self.system_override_state_triggerd = not self.system_override_state_triggerd # toggle system override state
        running = not running # toggle statemachine running state
        self.freeze()
        return 0

    def IRQ_handler_ferrometal_detected(self, pin):
        global ferrometaldetected
        self.RPI5_USB_LINE.send_message("Ferrometalscanner detected metal")
        ferrometaldetected = True

    def show_image(self, image_number):
        if not self.image_opened:
            self.RPI5_USB_LINE.send_message(f"showimage {image_number}")
            self.image_opened = True
        else:
            self.close_image()
            self.show_image(image_number)  

    def close_image(self):
        if self.image_opened:
            self.RPI5_USB_LINE.send_message("closeimage")
            self.image_opened = False

    def play_audio(self, audio_number):
        if not self.audio_playing:
            self.RPI5_USB_LINE.send_message(f"playaudio {audio_number}")
            self.audio_playing = True
        else:
            self.stop_audio() 
            self.play_audio(audio_number)

    def stop_audio(self):
        if self.audio_playing:
            self.RPI5_USB_LINE.send_message("stopaudio")
            self.audio_playing = False

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
        self.play_audio(1) # system initialised audio

    def run(self):
        global ferrometaldetected
        global running 

        while running: 
            if self.state == self.INITIALISATION_STATE:
                self.RPI5_USB_LINE.send_message("System initialised") 
                self.play_audio(4) # remove all people from the system audio    
                if self.person_detected_in_field('A') == False and self.person_detected_in_field('B') == False:
                    self.door1.open_door()
                    ferrometaldetected = False
                    self.FerroDetectorLEDS.off()
                    self.state = self.USER_FIELD_A_RESPONSE_STATE
                    self.show_image(1)  # move to field A image
                    if self.system_initialised == False:
                        self.systemset()

            elif self.state == self.USER_FIELD_A_RESPONSE_STATE:
                
                self.play_audio(5) # move to field A audio 
                if self.person_detected_in_field('A') == True and self.person_detected_in_field('B') == False: 
                    self.door1.close_door()
                    self.show_image(2) # move to field B image
                    self.play_audio(6) # move to field B audio
                    if ferrometaldetected == True:
                        self.show_image(4) # metal detected image
                        self.play_audio(9) # metal detected audio
                        self.door1.open_door()
                        self.state = self.INITIALISATION_STATE
                    elif ferrometaldetected == False:
                        self.state = self.USER_FIELD_B_RESPONSE_STATE
                elif self.person_detected_in_field('A') == False and self.person_detected_in_field('B') == True:
                    return 0

            elif self.state == self.USER_FIELD_B_RESPONSE_STATE:
                if self.person_detected_in_field('B') == True and self.person_detected_in_field('A') == False and ferrometaldetected == False:
                    self.show_image(3) # move to MR room image
                    self.play_audio(8) # you may proceed to MR room audio
                    self.door2.open_door()
                    self.FerroDetectorLEDS.set_color("green")
                    self.state = self.USER_IN_MR_ROOM_STATE
                elif ferrometaldetected == True:
                    self.door1.open_door()
                    self.FerroDetectorLEDS.set_color("red")
                    self.state = self.INITIALISATION_STATE
                else:
                    self.FerroDetectorLEDS.set_color("yellow")

            elif self.state == self.USER_IN_MR_ROOM_STATE:
                if self.person_detected_in_field('B') == False and self.person_detected_in_field('A') == False:
                    self.show_image(5) # wait for return from MR room image
                    self.state = self.USER_RETURNS_FROM_MR_ROOM_STATE

            elif self.state == self.USER_RETURNS_FROM_MR_ROOM_STATE:
                if self.person_detected_in_field('B') == True or self.person_detected_in_field('A') == True:
                    self.show_image(6) # exit to change room image
                    self.play_audio(10) # exit to change room audio      
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
        if running == True:
            self.system_initialised = False
            self.state = self.INITIALISATION_STATE
            return 0
        elif running == False and self.system_override_state_triggerd == True:
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
        USBCommunication.send_message(FDS.RPI5_USB_LINE, "System failed to initialise")
    except Exception as e:
        USBCommunication.send_message(FDS.RPI5_USB_LINE, "System encountered unexpected error")
