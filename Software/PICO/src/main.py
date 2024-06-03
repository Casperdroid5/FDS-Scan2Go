from hardware_s2g import LD2410PersonDetector, Door, WS2812
from system_utils import SystemInitCheck, Timer, USBCommunication, Log
from machine import Pin

global running   # system running global variable
running = False  # wait for system to be initialized before starting the state machine

class StateMachine:
    def __init__(self, communication, logger, timer):
        self.state = None
        self.user_in_mri = False
        self.emergency_state_triggered = False
        self.system_initialized = False
        self.system_override_state_triggered = False
        self.user_returned_from_mri = False
        self.sensor_to_object_distance_threshold = 180
        self.audio_played = False
        self.image_opened = False

        self.communication = communication
        self.logger = logger
        self.timer = timer

        self.INITIALISATION_STATE = 0
        self.USER_FIELD_A_RESPONSE_STATE = 1
        self.USER_FIELD_B_RESPONSE_STATE = 2
        self.USER_IN_MR_ROOM_STATE = 3
        self.USER_RETURNS_FROM_MR_ROOM_STATE = 4
        self.USER_EXITS_FDS_STATE = 5
        self.METAL_DETECTED_STATE = 6

        self.field_A_leds = WS2812(pin_number=2, num_leds=2, brightness=30)
        self.field_B_leds = WS2812(pin_number=3, num_leds=2, brightness=30)
        self.ferrometal_detector_leds = WS2812(pin_number=6, num_leds=2, brightness=30)

        self.changeroom_door = Door(pin_number=14, angle_closed=90, angle_open=0, position_sensor_pin=19)
        self.mri_room_door = Door(pin_number=15, angle_closed=90, angle_open=185, position_sensor_pin=20)

        self.mmWaveField_B = LD2410PersonDetector(uart_number=0, tx_pin=0, rx_pin=1)
        self.mmWaveField_A = LD2410PersonDetector(uart_number=1, tx_pin=4, rx_pin=5)

        self.button_emergency = Pin(10, Pin.IN, Pin.PULL_UP)
        self.button_emergency.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_emergencybutton_press)

        self.button_system_bypass = Pin(13, Pin.IN, Pin.PULL_UP)
        self.button_system_bypass.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_bypassbutton_press)

        self.button_system_reset = Pin(17, Pin.IN, Pin.PULL_UP)
        self.button_system_reset.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_button_system_reset)

        self.ferrometalscanner = Pin(16, Pin.IN, Pin.PULL_UP)

        self.latchreset = Pin(22, Pin.OUT)
        self.latchreset.value(1)

    def IRQ_handler_emergencybutton_press(self, pin):
        self.communication.send_message("Emergency button")
        self.communication.send_message("showimage 7")  # Emergency button pressed
        self.logger.log_message("Emergency button pressed")
        self.emergency_state_triggered = True
        self.field_A_leds.off()
        self.field_B_leds.off()
        global running
        running = False

    def IRQ_handler_bypassbutton_press(self, pin):
        self.communication.send_message("Override button pressed")
        self.communication.send_message("showimage 8")  # System override button pressed
        self.logger.log_message("System override button pressed")
        self.emergency_state_triggered = False
        self.field_A_leds.off()
        self.field_B_leds.off()
        self.system_override_state_triggered = True
        global running
        running = False

    def IRQ_handler_button_system_reset(self, pin):
        global running
        self.logger.log_message("System reset button pressed")
        self.communication.send_message("System reset button was pressed")
        self.system_initialized = False
        self.system_override_state_triggered = False
        self.emergency_state_triggered = False
        self.audio_played = False
        self.image_opened = False
        self.communication.send_message("closeimage")  # close all images
        self.field_A_leds.off()
        self.field_B_leds.off()
        systemlog.log_message("System has been reset")
        self.state = self.INITIALISATION_STATE
        running = True
        self.latchreset.value(0)

    def systeminit(self):
        self.field_A_leds.off()
        self.field_B_leds.off()
        self.ferrometal_detector_leds.off()
        self.mri_room_door.close_door()
        self.changeroom_door.open_door()
        self.system_initialized = True
        self.communication.send_message("System initialized")
        self.communication.send_message("playaudio 1")  # System started

    def run(self):
        global running
        self.state = self.INITIALISATION_STATE

        while running:
            if self.state == self.INITIALISATION_STATE:
                self.handle_initialisation_state()
            elif self.state == self.USER_FIELD_A_RESPONSE_STATE:
                self.handle_user_field_a_response_state()
            elif self.state == self.USER_FIELD_B_RESPONSE_STATE:
                self.handle_user_field_b_response_state()
            elif self.state == self.USER_IN_MR_ROOM_STATE:
                self.handle_user_in_mr_room_state()
            elif self.state == self.USER_RETURNS_FROM_MR_ROOM_STATE:
                self.handle_user_returns_from_mr_room_state()
            elif self.state == self.USER_EXITS_FDS_STATE:
                self.handle_user_exits_fds_state()
            elif self.state == self.METAL_DETECTED_STATE:
                self.handle_metal_detected()
            else:
                self.freeze()

    def handle_initialisation_state(self):
        if not self.system_initialized:
            self.systeminit()
            self.field_A_leds.set_color("white")
        elif not self.image_opened:
            self.communication.send_message("showimage 0")  # Please leave the area
            self.image_opened = True
        elif not self.audio_played:
            self.communication.send_message("playaudio 4")  # Please leave the area
            self.audio_played = True
        elif not self.mmWaveField_B.scan_for_people() and not self.mmWaveField_A.scan_for_people():
            self.latchreset.value(1)
            self.field_A_leds.off()
            self.field_B_leds.off()
            self.ferrometal_detector_leds.off()
            self.latchreset.value(0)
            self.field_A_leds.set_color("white")
            self.communication.send_message("playaudio 5")  # Take place in area A
            self.audio_played = False
            self.image_opened = False
            self.state = self.USER_FIELD_A_RESPONSE_STATE

    def handle_user_field_a_response_state(self):
        self.field_A_leds.set_color("white")
        if not self.mmWaveField_B.scan_for_people() and self.mmWaveField_A.scan_for_people():
            self.changeroom_door.close_door()
            if not self.audio_played:
                self.communication.send_message("playaudio 6") # move through the metaldetector to field B
                self.audio_played = True
            if not self.image_opened:
                self.communication.send_message("showimage 2") # move through the metaldetector to field B
                self.image_opened = True
            self.field_A_leds.off()
            self.field_B_leds.set_color("white")
            self.state = self.USER_FIELD_B_RESPONSE_STATE
        
    def handle_user_field_b_response_state(self):
        if self.mmWaveField_B.scan_for_people() and not self.mmWaveField_A.scan_for_people():
            if not self.ferrometalscanner.value():
                self.communication.send_message("showimage 3")  # No metals detected
                self.communication.send_message("playaudio 8")  # No metals detected, please proceed to MRI room
                self.mri_room_door.open_door()
                self.field_B_leds.off()
                self.ferrometal_detector_leds.set_color("green")
                self.state = self.USER_IN_MR_ROOM_STATE
            else:
                self.state = self.METAL_DETECTED_STATE
        else:
            self.ferrometal_detector_leds.set_color("yellow")

    def handle_user_in_mr_room_state(self):
        if not self.mmWaveField_B.scan_for_people() and not self.mmWaveField_A.scan_for_people():
            self.communication.send_message("showimage 5")  # After your scan, please take place in area B
            self.ferrometal_detector_leds.off()
            self.field_B_leds.set_color("white")
            self.field_A_leds.off()
            self.state = self.USER_RETURNS_FROM_MR_ROOM_STATE

    def handle_user_returns_from_mr_room_state(self):
        if  self.mmWaveField_B.scan_for_people() or self.mmWaveField_A.scan_for_people():
            self.communication.send_message("showimage 6")  # Welcome back, you may proceed to the changing room
            self.communication.send_message("playaudio 10")  # Welcome back, you may proceed to the changing room
            self.mri_room_door.close_door()
            self.field_B_leds.off()
            self.field_A_leds.set_color("white")
            self.image_opened = False
            self.audio_played = False
            self.state = self.USER_EXITS_FDS_STATE

    def handle_user_exits_fds_state(self):
        if not self.mmWaveField_B.scan_for_people() and self.mmWaveField_A.scan_for_people():
            self.changeroom_door.open_door()
            self.state = self.INITIALISATION_STATE

    def handle_metal_detected(self):
        self.communication.send_message("Ferrometal detector detected metal")
        self.logger.log_message("Ferrometal detector detected metal")
        self.ferrometal_detector_leds.set_color("red")
        self.field_A_leds.set_color("white")
        self.field_B_leds.off()
        self.communication.send_message("showimage 4")  # Ferrometals detected, please leave the sluice
        self.communication.send_message("playaudio 9")  # Ferrometals detected, please leave the sluice
        self.changeroom_door.open_door()
        self.mri_room_door.close_door()
        self.state = self.INITIALISATION_STATE

    def freeze(self):
        global running
        if not running and self.system_override_state_triggered:
            self.field_A_leds.set_color("white")
            self.field_B_leds.set_color("white")
            self.ferrometal_detector_leds.set_color("white")
            self.changeroom_door.open_door()
            self.mri_room_door.open_door()
            self.emergency_state_triggered = False
        elif not running and self.emergency_state_triggered and not self.system_override_state_triggered:
            self.field_A_leds.set_color("yellow")
            self.field_B_leds.set_color("yellow")
            self.ferrometal_detector_leds.set_color("yellow")
            self.changeroom_door.open_door()
            self.mri_room_door.open_door()

if __name__ == "__main__":
    running = True
    systemlog = Log()
    systemlog.open_log()
    communication = USBCommunication()
    timer = Timer()
    FDS = StateMachine(communication, systemlog, timer)

    try:
        SystemInitCheck().systemcheck()
        systemlog.log_message("System check passed. Starting FDS...")
        while True:
            if running:
                FDS.run()
            else:
                FDS.freeze()
    except SystemExit as s:
        running = False
        communication.send_message("System Exiting")
        systemlog.log_message("System Exiting")
        systemlog.close_log()
    except Exception as e:
        running = False
        communication.send_message(f"System encountered unexpected error: {e}")
        systemlog.log_message(f"System encountered unexpected error: {e}")
        systemlog.close_log()


