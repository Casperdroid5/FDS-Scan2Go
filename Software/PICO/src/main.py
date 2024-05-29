from hardware_s2g import LD2410PersonDetector, Door, WS2812
from system_utils import SystemInitCheck, Timer, USBCommunication, Log
from machine import Pin
import uasyncio as asyncio

global running   # system running global variable
running = False  # wait for system to be initialised before starting the state machine

class StateMachine:
    def __init__(self, led_controllers, door_controllers, sensor_controllers, communication, logger, timer):
        self.state = None
        self.user_in_mri = False
        self.emergency_state_triggered = False
        self.system_initialised = False
        self.system_override_state_triggered = False
        self.user_returned_from_mri = False
        self.sensor_to_object_distance_threshold = 180
        self.audio_played = False
        self.image_opened = False

        self.led_controllers = led_controllers
        self.door_controllers = door_controllers
        self.sensor_controllers = sensor_controllers
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

        self.initialize_buttons()

    def initialize_buttons(self):
        self.button_emergency = Pin(10, Pin.IN, Pin.PULL_UP)
        self.button_emergency.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_emergencybutton_press)

        self.button_system_bypass = Pin(13, Pin.IN, Pin.PULL_UP)
        self.button_system_bypass.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_bypassbutton_press)

        self.button_system_reset = Pin(17, Pin.IN, Pin.PULL_UP)
        self.button_system_reset.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_button_system_reset)

        self.ferrometalscanner = Pin(16, Pin.IN, Pin.PULL_UP)
        
        self.ferrometalscanner_latchreset = Pin(22, Pin.OUT)
        self.ferrometalscanner_latchreset.value(1)

    def IRQ_handler_door_changeroom_button_press(self, pin):
        if self.state == self.USER_FIELD_A_RESPONSE_STATE:
            if self.door_controllers['changeroom'].door_state == "closed":
                self.door_controllers['changeroom'].open_door()

    def IRQ_handler_door_mri_room_button_press(self, pin):
        if self.state == self.USER_IN_MR_ROOM_STATE or (self.ferrometalscanner.value() == 1 and self.user_returned_from_mri) or self.user_in_mri:
            if self.door_controllers['mri_room'].door_state == "closed":
                self.door_controllers['mri_room'].open_door()

    def IRQ_handler_emergencybutton_press(self, pin):
        self.communication.send_message("Emergency button")
        self.communication.send_message("showimage 7")
        self.logger.log_message("Emergency button pressed")
        self.emergency_state_triggered = True
        self.led_controllers['fieldALeds'].off()
        self.led_controllers['fieldBLeds'].off()
        global running
        running = False

    def IRQ_handler_button_system_reset(self, pin):
        global running
        self.logger.log_message("System reset button pressed")
        self.communication.send_message("System reset button was pressed")
        self.system_initialised = False
        self.system_override_state_triggered = False
        self.emergency_state_triggered = False
        self.audio_played = False
        self.image_opened = False
        self.communication.send_message("closeimage")
        self.led_controllers['fieldALeds'].off()
        self.led_controllers['fieldBLeds'].off()
        self.logger.log_message("System has been reset")
        self.state = self.INITIALISATION_STATE
        running = True
        self.ferrometalscanner_latchreset.value(0)

    def IRQ_handler_bypassbutton_press(self, pin):
        self.communication.send_message("Override button pressed")
        self.communication.send_message("showimage 8")
        self.logger.log_message("System override button pressed")
        self.emergency_state_triggered = False
        self.led_controllers['fieldALeds'].off()
        self.led_controllers['fieldBLeds'].off()
        self.system_override_state_triggered = True
        global running
        running = False

    def person_detected_in_field(self, field):
        return self.sensor_controllers[field].scan_for_people() and self.sensor_controllers[field].get_detection_distance() < self.sensor_to_object_distance_threshold

    def systeminit(self):
        for led in self.led_controllers.values():
            led.off()
        self.door_controllers['mri_room'].close_door()
        self.door_controllers['changeroom'].open_door()
        self.system_initialised = True
        self.communication.send_message("System initialised")
        self.communication.send_message("playaudio 1")

    async def run(self):
        global running
        self.state = self.INITIALISATION_STATE
        while running:
            try:
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
                await asyncio.sleep(0.1)  # Small delay to prevent tight loop
            except Exception as e:
                self.logger.log_message(f"State machine error: {e}")
                print(f"State machine error: {e}")

    def handle_initialisation_state(self): 
        if not self.system_initialised:
            self.systeminit()
            self.led_controllers['fieldALeds'].set_color("white")
        elif not self.image_opened:
            self.communication.send_message("showimage 0")
            self.image_opened = True
        elif not self.audio_played:
            self.communication.send_message("playaudio 4")
            self.audio_played = True
        elif not self.person_detected_in_field('A') and not self.person_detected_in_field('B'):
            self.ferrometalscanner_latchreset.value(1)
            self.led_controllers['fieldALeds'].off()
            self.led_controllers['fieldBLeds'].off()
            self.led_controllers['FerrometalDetectorLeds'].off()
            self.ferrometalscanner_latchreset.value(0)
            self.start_pulsing_leds('fieldALeds', 'white', 0.0030)
            self.communication.send_message("showimage 1")
            self.state = self.USER_FIELD_A_RESPONSE_STATE

    def handle_user_field_a_response_state(self):
        if not self.audio_played:
            self.communication.send_message("playaudio 5")
            self.audio_played = True
            
        if self.person_detected_in_field('A') and not self.person_detected_in_field('B'):
            self.stop_pulsing_leds('fieldALeds')
            self.audio_played = False
            self.door_controllers['changeroom'].close_door()
            self.communication.send_message("showimage 2")
            self.communication.send_message("playaudio 6")
            if self.ferrometalscanner.value() == 1:
                self.state = self.METAL_DETECTED_STATE
            else:
                self.led_controllers['fieldALeds'].off()
                self.led_controllers['fieldBLeds'].set_color("white")
                self.state = self.USER_FIELD_B_RESPONSE_STATE
        elif not self.person_detected_in_field('A') and self.person_detected_in_field('B'):
            return

    def handle_user_field_b_response_state(self):
        if self.person_detected_in_field('B') and not self.person_detected_in_field('A') and self.ferrometalscanner.value() == 0:
            self.communication.send_message("showimage 3")
            self.communication.send_message("playaudio 8")
            self.door_controllers['mri_room'].open_door()
            self.led_controllers['fieldBLeds'].off()
            self.led_controllers['FerrometalDetectorLeds'].set_color("green")
            self.state = self.USER_IN_MR_ROOM_STATE
        if self.ferrometalscanner.value() == 1:
            self.state = self.METAL_DETECTED_STATE
        else:
            self.led_controllers['FerrometalDetectorLeds'].set_color("yellow")

    def handle_user_in_mr_room_state(self):
        if not self.person_detected_in_field('B') and not self.person_detected_in_field('A'):
            self.communication.send_message("showimage 5")
            self.led_controllers['FerrometalDetectorLeds'].off()
            self.led_controllers['fieldBLeds'].set_color("white")
            self.led_controllers['fieldALeds'].off()
            self.state = self.USER_RETURNS_FROM_MR_ROOM_STATE

    def handle_user_returns_from_mr_room_state(self):
        if self.person_detected_in_field('B') or self.person_detected_in_field('A'):
            self.communication.send_message("showimage 6")
            self.communication.send_message("playaudio 10")
            self.door_controllers['mri_room'].close_door()
            self.led_controllers['fieldBLeds'].off()
            self.led_controllers['fieldALeds'].set_color("white")
            self.state = self.USER_EXITS_FDS_STATE

    def handle_user_exits_fds_state(self):
        if not self.person_detected_in_field('B') and self.person_detected_in_field('A'):
            self.door_controllers['changeroom'].open_door()
            self.state = self.INITIALISATION_STATE

    def handle_metal_detected(self):
        self.image_opened = False
        self.communication.send_message("Ferrometaldector detected metal")
        self.logger.log_message("Ferrometaldetector detected metal")
        self.led_controllers['FerrometalDetectorLeds'].set_color("red")
        self.led_controllers['fieldALeds'].set_color("white")
        self.led_controllers['fieldBLeds'].off()
        if not self.image_opened:
            self.communication.send_message("showimage 4")
            self.image_opened = True
        if not self.audio_played:
            self.communication.send_message("playaudio 9")
            self.audio_played = True
        self.door_controllers['changeroom'].open_door()
        self.door_controllers['mri_room'].close_door()
        self.state = self.INITIALISATION_STATE

    def freeze(self):
        global running
        if not running and self.system_override_state_triggered:
            self.led_controllers['fieldALeds'].set_color("white")
            self.led_controllers['fieldBLeds'].set_color("white")
            self.led_controllers['FerrometalDetectorLeds'].set_color("white")
            self.door_controllers['changeroom'].open_door()
            self.door_controllers['mri_room'].open_door()
            self.emergency_state_triggered = False
        elif not running and self.emergency_state_triggered and not self.system_override_state_triggered:
            self.led_controllers['fieldALeds'].set_color("yellow")
            self.led_controllers['fieldBLeds'].set_color("yellow")
            self.led_controllers['FerrometalDetectorLeds'].set_color("yellow")
            self.door_controllers['changeroom'].open_door()
            self.door_controllers['mri_room'].open_door()

    def start_pulsing_leds(self, field, color, delay):
        self.led_controllers[field].start_pulse(color=color, delay=delay)

    def stop_pulsing_leds(self, field):
        self.led_controllers[field].stop_pulse()

async def main():
    global running
    try:
        running = True
        print("Initializing log...")
        systemlog = Log()
        systemlog.open_log()
        print("Log initialized.")
        
        print("Initializing components...")
        led_controllers = {
            "fieldALeds": WS2812(pin_number=2, num_leds=2, brightness=30),
            "fieldBLeds": WS2812(pin_number=3, num_leds=2, brightness=30),
            "FerrometalDetectorLeds": WS2812(pin_number=6, num_leds=2, brightness=30)
        }
        door_controllers = {
            "changeroom": Door(pin_number=14, angle_closed=90, angle_open=0, position_sensor_pin=19),
            "mri_room": Door(pin_number=15, angle_closed=90, angle_open=185, position_sensor_pin=20)
        }
        sensor_controllers = {
            "B": LD2410PersonDetector(uart_number=0, baudrate=256000, tx_pin=0, rx_pin=1),
            "A": LD2410PersonDetector(uart_number=1, baudrate=256000, tx_pin=4, rx_pin=5)
        }
        communication = USBCommunication()
        timer = Timer()
        print("Components initialized.")
        
        FDS = StateMachine(led_controllers, door_controllers, sensor_controllers, communication, systemlog, timer)
        
        print("Running system check...")
        SystemInitCheck().systemcheck()
        systemlog.log_message("Systemcheck passed. Starting FDS...")
        
        try:
            while True:
                if running:
                    await FDS.run()
                else:
                    FDS.freeze()
                await asyncio.sleep(0.1)
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

    except Exception as e:
        print(f"Initialization failed: {e}")
        if 'communication' in locals():
            communication.send_message(f"Initialization failed: {e}")
        if 'systemlog' in locals():
            systemlog.log_message(f"Initialization failed: {e}")
            systemlog.close_log()

try:
    asyncio.run(main())
except Exception as e:
    print(f"Error running main: {e}")


