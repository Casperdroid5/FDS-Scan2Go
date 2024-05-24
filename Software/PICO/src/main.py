from hardware_s2g import LD2410PersonDetector, Door, WS2812
from system_utils import SystemInitCheck, Timer, USBCommunication, Log
from machine import Pin

global running   # system running global variable
running = False  # wait for system to be initialised before starting the state machine
global ferrometaldetected
ferrometaldetected = False  # Global variable to check if metal is detected

class StateMachine:
    def __init__(self, led_controller, door_controller, sensor_controller, communication, logger, timer):

        self.state = None
        self.user_in_mri = False
        self.emergency_state_triggerd = False
        self.system_initialised = False
        self.system_override_state_triggerd = False
        self.user_returned_from_mri = False
        self.sensor_to_object_distance_threshold = 180
        self.audio_played = False
        self.image_opened = False

        self.led_controller = led_controller
        self.door_controller = door_controller
        self.sensor_controller = sensor_controller
        self.communication = communication
        self.logger = logger
        self.timer = timer

        self.INITIALISATION_STATE = 0
        self.USER_FIELD_A_RESPONSE_STATE = 1
        self.USER_FIELD_B_RESPONSE_STATE = 2
        self.USER_IN_MR_ROOM_STATE = 3
        self.USER_RETURNS_FROM_MR_ROOM_STATE = 4
        self.USER_EXITS_FDS_STATE = 5

        self.initialize_buttons()

    def initialize_buttons(self):
        self.button_emergency = Pin(10, Pin.IN, Pin.PULL_UP)
        self.button_emergency.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_emergencybutton_press)

        self.button_system_bypass = Pin(13, Pin.IN, Pin.PULL_UP)
        self.button_system_bypass.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_bypassbutton_press)

        self.button_system_reset = Pin(17, Pin.IN, Pin.PULL_UP)
        self.button_system_reset.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_button_system_reset)

        self.ferrometalscanner = Pin(16, Pin.IN, Pin.PULL_UP)
        self.ferrometalscanner.irq(trigger=Pin.IRQ_FALLING, handler=self.IRQ_handler_ferrometal_detected)

        self.latchreset = Pin(22, Pin.OUT)

    def IRQ_handler_door_changeroom_button_press(self, pin):
        if self.state == self.USER_FIELD_A_RESPONSE_STATE:
            if self.door_controller.is_changeroom_door_closed():
                self.door_controller.open_changeroom_door()

    def IRQ_handler_door_mri_room_button_press(self, pin):
        if self.state == self.USER_IN_MR_ROOM_STATE or (ferrometaldetected == "NoMetalDetected" and self.user_returned_from_mri) or self.user_in_mri:
            if self.door_controller.is_mri_room_door_closed():
                self.door_controller.open_mri_room_door()

    def IRQ_handler_emergencybutton_press(self, pin):
        self.communication.send_message("Emergency button")
        self.communication.send_message("showimage 7")
        self.logger.log_message("Emergency button pressed")
        self.emergency_state_triggerd = True
        global running
        running = False

    def IRQ_handler_button_system_reset(self, pin):
        self.communication.send_message("System reset button")
        self.logger.log_message("System reset button pressed")
        self.system_initialised = False
        self.system_override_state_triggerd = False
        self.emergency_state_triggerd = False
        self.state = self.INITIALISATION_STATE
        global running
        running = True

    def IRQ_handler_bypassbutton_press(self, pin):
        self.communication.send_message("Override button pressed")
        self.communication.send_message("showimage 8")
        self.logger.log_message("System override button pressed")
        self.emergency_state_triggerd = False
        self.system_override_state_triggerd = not self.system_override_state_triggerd
        global running
        running = False

    def IRQ_handler_ferrometal_detected(self, pin):
        global ferrometaldetected
        self.latchreset.value(1)
        self.communication.send_message("Ferrometalscanner detected metal")
        self.logger.log_message("Ferrometalscanner detected metal")
        ferrometaldetected = True
        self.latchreset.value(0)

    def person_detected_in_field(self, field):
        return self.sensor_controller.person_detected(field, self.sensor_to_object_distance_threshold)

    def systemset(self):
        self.led_controller.turn_off_all()
        self.door_controller.close_mri_room_door()
        self.door_controller.open_changeroom_door()
        self.system_initialised = True
        self.communication.send_message("System initialised")
        self.communication.send_message("playaudio 1")

    def run(self):
        global ferrometaldetected
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
            else:
                self.freeze()

    def handle_initialisation_state(self):
        if not self.system_initialised:
            self.systemset()
        elif not self.image_opened:
            self.communication.send_message("showimage 0")
            self.image_opened = True
        elif not self.audio_played:
            self.communication.send_message("playaudio 4")
            self.audio_played = True
        elif not self.person_detected_in_field('A') and not self.person_detected_in_field('B'):
            self.reset_state()
            self.state = self.USER_FIELD_A_RESPONSE_STATE
            self.communication.send_message("showimage 1")

    def handle_user_field_a_response_state(self):
        if not self.audio_played:
            self.communication.send_message("playaudio 5")
            self.audio_played = True
            self.led_controller.start_pulsing("fieldALeds", "white", 3)  # Start pulsing fieldA LEDs
        if self.person_detected_in_field('A') and not self.person_detected_in_field('B'):
            self.audio_played = False
            self.door_controller.close_changeroom_door()
            self.communication.send_message("showimage 2")
            self.communication.send_message("playaudio 6")
            if ferrometaldetected:
                self.handle_metal_detected()
            else:
                self.led_controller.stop_pulsing("fieldALeds", "white", 3)  # Stop pulsing fieldA LEDs
                self.led_controller.start_pulsing("fieldBLeds", "white", 3)  # Start pulsing fieldB LEDs
                self.state = self.USER_FIELD_B_RESPONSE_STATE
        elif not self.person_detected_in_field('A') and self.person_detected_in_field('B'):
            return

    def handle_user_field_b_response_state(self):
        if self.person_detected_in_field('B') and not self.person_detected_in_field('A') and not ferrometaldetected:
            self.communication.send_message("showimage 3")
            self.communication.send_message("playaudio 8")
            self.door_controller.open_mri_room_door()
            self.led_controller.stop_pulsing("fieldBLeds", "white", 3)  # Stop pulsing fieldB LEDs
            self.state = self.USER_IN_MR_ROOM_STATE
        elif ferrometaldetected:
            self.handle_metal_detected()
        else:
            self.led_controller.set_color("FerrometalDetectorLeds", "yellow")

    def handle_user_in_mr_room_state(self):
        if not self.person_detected_in_field('B') and not self.person_detected_in_field('A'):
            self.communication.send_message("showimage 5")
            self.led_controller.turn_off_all()  # Stop pulsing LEDs
            self.state = self.USER_RETURNS_FROM_MR_ROOM_STATE

    def handle_user_returns_from_mr_room_state(self):
        if self.person_detected_in_field('B') or self.person_detected_in_field('A'):
            self.communication.send_message("showimage 6")
            self.communication.send_message("playaudio 10")
            self.door_controller.close_mri_room_door()
            self.state = self.USER_EXITS_FDS_STATE

    def handle_user_exits_fds_state(self):
        if not self.person_detected_in_field('B') and self.person_detected_in_field('A'):
            self.door_controller.open_changeroom_door()
            self.state = self.INITIALISATION_STATE

    def handle_metal_detected(self):
        systemlog.log_message("Metal detected")
        if not self.image_opened:
            self.communication.send_message("showimage 4")
            self.image_opened = True
        if not self.audio_played:
            self.communication.send_message("playaudio 9")
            self.audio_played = True
        self.door_controller.open_changeroom_door()

    def reset_state(self):
        self.communication.send_message("closeimage")
        self.audio_played = False
        self.led_controller.stop_pulsing("fieldALeds")
        self.led_controller.stop_pulsing("fieldBLeds")
        self.image_opened = False
        self.door_controller.open_changeroom_door()
        global ferrometaldetected
        ferrometaldetected = False
        systemlog.log_message("System reset")

    def freeze(self):
        global running
        if not running and self.system_override_state_triggerd:
            self.led_controller.stop_pulsing("fieldALeds")
            self.led_controller.stop_pulsing("fieldBLeds")
            self.led_controller.set_color_all("white")
            self.door_controller.open_all_doors()
            self.emergency_state_triggerd = False
        elif not running and self.emergency_state_triggerd and not self.system_override_state_triggerd:
            self.led_controller.set_color_all("yellow")
            self.door_controller.open_all_doors()

class LEDController:
    def __init__(self):
        self.leds = {
            "fieldALeds": WS2812(pin_number=2, num_leds=2, brightness=50),
            "fieldBLeds": WS2812(pin_number=3, num_leds=2, brightness=50),
            "FerrometalDetectorLeds": WS2812(pin_number=6, num_leds=2, brightness=50)
        }

    def set_color(self, led, color):
        if led in self.leds:
            self.leds[led].set_color(color)

    def start_pulsing(self, led, color, interval_ms):
        if led in self.leds:
            self.leds[led].start_pulsing(color, interval_ms)

    def stop_pulsing(self, led, color, interval_ms):
        if led in self.leds:
            self.leds[led].stop_pulsing()

    def turn_off_all(self):
        for led in self.leds.values():
            led.off()

    def set_color_all(self, color):
        for led in self.leds.values():
            led.set_color(color)


class DoorController:
    def __init__(self):
        self.door_changeroom = Door(pin_number=14, angle_closed=90, angle_open=0, position_sensor_pin=19)
        self.door_mri_room = Door(pin_number=15, angle_closed=90, angle_open=185, position_sensor_pin=20)

    def open_changeroom_door(self):
        self.door_changeroom.open_door()

    def close_changeroom_door(self):
        self.door_changeroom.close_door()

    def open_mri_room_door(self):
        self.door_mri_room.open_door()

    def close_mri_room_door(self):
        self.door_mri_room.close_door()

    def open_all_doors(self):
        self.door_changeroom.open_door()
        self.door_mri_room.open_door()

    def is_changeroom_door_closed(self):
        return self.door_changeroom.door_state == "closed"

    def is_mri_room_door_closed(self):
        return self.door_mri_room.door_state == "closed"

class SensorController:
    def __init__(self):
        self.sensors = {
            "B": LD2410PersonDetector(uart_number=0, baudrate=256000, tx_pin=0, rx_pin=1),
            "A": LD2410PersonDetector(uart_number=1, baudrate=256000, tx_pin=4, rx_pin=5)
        }

    def person_detected(self, field, distance_threshold):
        try:
            sensor = self.sensors[field]
            if sensor.scan_for_people() and sensor.get_detection_distance() < distance_threshold:
                return True
            else:
                return False
        except KeyError:
            print(f"Field {field} not found in sensors.")
            return False
        except Exception as e:
            print(f"Error in person_detected for field {field}: {e}")
            return False


if __name__ == "__main__":
    running = True
    systemlog = Log()
    systemlog.open_log()
    led_controller = LEDController()
    door_controller = DoorController()
    sensor_controller = SensorController()
    communication = USBCommunication()
    timer = Timer()
    FDS = StateMachine(led_controller, door_controller, sensor_controller, communication, systemlog, timer)
    try:
        SystemInitCheck().systemcheck()
        systemlog.log_message("Systemcheck passed. Starting FDS...")
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