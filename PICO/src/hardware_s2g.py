from machine import Pin, PWM, UART
import neopixel
from system_utils import Timer
import time

class WS2812:
    def __init__(self, pin_number, num_leds, brightness):
        self._np = neopixel.NeoPixel(Pin(pin_number), num_leds, bpp=3, timing=1)
        self._num_leds = num_leds
        self._brightness = brightness

        # Kleuren dictionary
        self._COLORS = {
            "red": (65535, 0, 0),
            "green": (0, 65535, 0),
            "blue": (0, 0, 65535),
            "yellow": (65535, 65535, 0),
            "cyan": (0, 65535, 65535),
            "magenta": (65535, 0, 65535),
            "white": (65535, 65535, 65535),
        }

    def set_color(self, color):
        color_values = self._COLORS.get(color.lower())
        if color_values:
            for i in range(self._num_leds):
                # Pas helderheid toe op kleuren
                adjusted_color = tuple(int(val * self._brightness) for val in color_values)
                self._np[i] = adjusted_color
            self._np.write()
            return color
        else:
            return "Color not found"

    def set_brightness(self, brightness):
        self._brightness = brightness # Update de helderheid

    def on(self):
        return self.set_color("white")

    def off(self):
        for i in range(self._num_leds):
            self._np[i] = (0, 0, 0)
        self._np.write()
        return "off"

class SERVOMOTOR: # Servo motor 
    def __init__(self, pin_number):
        self.pwm = PWM(pin_number)
        self.pwm.freq(50)  # Set PWM frequency to 50 Hz for servo control
        self.min_us = 600  # Minimum pulse width in microseconds for 0 degrees
        self.max_us = 2400  # Maximum pulse width in microseconds for 180 degrees
        self.current_angle = 0  # Initialize current angle to 0

    def set_angle(self, angle):
        pulse_width_us = self.min_us + (self.max_us - self.min_us) * angle / 180  # Convert angle to pulse width
        duty_cycle = int(pulse_width_us / 20000 * 65535) # Convert pulse width from microseconds to duty cycle (0-65535) # 20000 microseconds = 20 milliseconds (period)
        self.pwm.duty_u16(duty_cycle)  # Set duty cycle to control servo position
        self.current_angle = angle  # Update current angle
        self.wait_for_completion()  # Wait for servo to reach target position

    def get_current_angle(self): 
        return self.current_angle

    def wait_for_completion(self):
        # Wait until servo reaches target position
        while True:
            # Check if current angle matches target angle within a tolerance
            if abs(self.current_angle - self.get_current_angle()) < 1:
                break

class DOOR: # Door motor and positionsensor
    def __init__(self, pin_number, angle_closed, angle_open, position_sensor_pin):
        self.servo = SERVOMOTOR(pin_number) 
        self.pin_number = pin_number 
        self.angle_open = angle_open # maximum opening angle
        self.angle_closed = angle_closed # maximum closing angle
        self.door_sensor = Pin(position_sensor_pin, Pin.IN, Pin.PULL_UP)
        self.door_state = "closed"  # Initialize door state

    def __repr__(self):
        return f"DOOR at Pin {self.pin_number}, State: {self.door_state}"

    def open_door(self):
        #print(f"open_{self}")
        self.servo.set_angle(self.angle_open)
        if self.servo.get_current_angle() == self.angle_open and self.door_sensor.value() == 0:
            #print("New state: dooropened")
            self.door_state = "open"
            return self.door_state

    def close_door(self):
        #print(f"close_{self}")
        self.servo.set_angle(self.angle_closed)
        if self.servo.get_current_angle() == self.angle_closed and self.door_sensor.value() == 1:
            #print("New state: doorclosed")
            self.door_state = "closed"
            return self.door_state

class DOORWITHLED(DOOR, WS2812):
    def __init__(self, door_pin_number, door_angle_closed, door_angle_open, door_position_sensor_pin, led_pin_number, num_leds, brightness):
        DOOR.__init__(self, door_pin_number, door_angle_closed, door_angle_open, door_position_sensor_pin)
        WS2812.__init__(self, led_pin_number, num_leds, brightness)

    def open_door(self):
        super().open_door()
        self.set_color("green")  # Set LED color to green when the door is opened

    def close_door(self):
        super().close_door()
        self.set_color("red")  # Set LED color to red when the door is closed

class SEEEDPERSONDETECTOR: # mmWave sensor
    def __init__(self, uart_number, baudrate, tx_pin, rx_pin):
        self.uart_number = uart_number
        self.baudrate = baudrate
        self.tx_pin = tx_pin  
        self.rx_pin = rx_pin 
        self._uart_sensor = UART(uart_number, baudrate, tx_pin, rx_pin)
        self.humanpresence = "unknown"

    def check_humanpresence(self):
        data = self._uart_sensor.read()
        if data:
            if b'\x02' in data:
                #self.humanpresence = "Somebodymoved"
                self.humanpresence = True
            elif b'\x01' in data:
                #self.humanpresence = "Somebodystoppedmoving"
                self.humanpresence = False
            elif b'\x03' in data:
                #self.humanpresence = "Somebodyisclose"
                self.humanpresence = True
            elif b'\x04' in data:
                #self.humanpresence = "Somebodyisaway"
                self.humanpresence = False
        return self.humanpresence 

class LD2410PERSONDETECTOR: # mmWave sensor
    HEADER = bytes([0xfd, 0xfc, 0xfb, 0xfa])
    TERMINATOR = bytes([0x04, 0x03, 0x02, 0x01])
    NULLDATA = bytes([])
    REPORT_HEADER = bytes([0xf4, 0xf3, 0xf2, 0xf1])
    REPORT_TERMINATOR = bytes([0xf8, 0xf7, 0xf6, 0xf5])

    STATE_NO_TARGET = 0
    STATE_MOVING_TARGET = 1
    STATE_STATIONARY_TARGET = 2
    STATE_COMBINED_TARGET = 3
    TARGET_NAME = ["no_target", "moving_target", "stationary_target", "combined_target"]
    
    standing_threshold = 15  # Threshold for determining if someone has been standing for too long (40 = 4 seconds somehow)
    moving_threshold = 30  # Threshold for determining if someone has been moving for too long

    def __init__(self, uart_number, baudrate, tx_pin, rx_pin):

        self.ser = UART(uart_number, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin), timeout=1)
        self.meas = {
            "state": self.STATE_NO_TARGET,
            "moving_distance": 0,
            "moving_energy": 0,
            "stationary_distance": 0,
            "stationary_energy": 0,
            "detection_distance": 0 }

        self.mmWaveTimer = Timer()  # Initialize the Timer for mmWave sensor
        self.person_detected = False  # Variable to track person detection status
        self.standing_timer = 0  # Timer to track how long someone has been standing
        self.moving_timer = 0  # Timer to track how long someone has been moving

    def print_bytes(self, data):
        if len(data) == 0:
            print("<no data>")
            return
        text = f"hex: {data[0]:02x}"
        for i in range(1, len(data)):
            text = text + f" {data[i]:02x}"
        print(text)

    def send_command(self, cmd, data=NULLDATA, response_expected=True):
        cmd_data_len = bytes([len(cmd) + len(data), 0x00])
        frame = self.HEADER + cmd_data_len + cmd + data + self.TERMINATOR
        self.ser.write(frame)
        if response_expected:
            response = self.ser.read()
        else:
            response = self.NULLDATA
        return response

    def enable_config(self):
        response = self.send_command(bytes([0xff, 0x00]), bytes([0x01, 0x00]))
        self.print_bytes(response)

    def end_config(self):
        response = self.send_command(bytes([0xfe, 0x00]), response_expected=False)

    def read_firmware_version(self):
        response = self.ser.read()
        if response is None:
            print("Error: No response from serial.")
            return
        self.print_bytes(response)

    def enable_engineering(self):
        response = self.send_command(bytes([0x62, 0x00]))
        self.print_bytes(response)

    def end_engineering(self):
        response = self.send_command(bytes([0x63, 0x00]))
        self.print_bytes(response)

    def read_serial_buffer(self):
        response = self.ser.read()
        self.print_bytes(response)
        return response

    def print_meas(self):
        print(f"state: {self.TARGET_NAME[self.meas['state']]}")
        print(f"moving distance: {self.meas['moving_distance']}")
        print(f"moving energy: {self.meas['moving_energy']}")
        print(f"stationary distance: {self.meas['stationary_distance']}")
        print(f"stationary energy: {self.meas['stationary_energy']}")
        print(f"detection distance: {self.meas['detection_distance']}")

    def parse_report(self, data):
        # sanity checks
        if len(data) < 23:
            print(f"error, frame length {data} is too short")
            return
        if data[0:4] != self.REPORT_HEADER:
            print(f"error, frame header is incorrect")
            return
        # Check if data[4] (frame length) is valid. It must be 0x0d or 0x23
        # depending on if we are in basic mode or engineering mode
        if data[4] != 0x0d and data[4] != 0x23:
            print(f"error, frame length is incorrect")
            return
        # data[7] must be report 'head' value 0xaa
        if data[7] != 0xaa:
            print(f"error, frame report head value is incorrect")
            return
        # sanity checks passed. Store the sensor data in meas
        self.meas["state"] = data[8]
        self.meas["moving_distance"] = data[9] + (data[10] << 8)
        self.meas["moving_energy"] = data[11]
        self.meas["stationary_distance"] = data[12] + (data[13] << 8)
        self.meas["stationary_energy"] = data[14]
        self.meas["detection_distance"] = data[15] + (data[16] << 8)
        # print the data
        # self.print_meas()

    def read_serial_until(self, identifier):
        content = bytes([])
        while len(identifier) > 0:
            v = self.ser.read(1)
            if v == None:
                # timeout
                return None
                break
            if v[0] == identifier[0]:
                content = content + v[0:1]
                identifier = identifier[1:len(identifier)]
            else:
                content = bytes([])
        return content

    def serial_flush(self):
        dummy = self.ser.read()
        return dummy

    def read_serial_frame(self):
        # dummy read to flush out the read buffer:
        self.serial_flush()
        time.sleep(0.05)
        # keep reading to see a header arrive:
        header = self.read_serial_until(self.REPORT_HEADER)
        if header == None:
            # print("error, frame header not found")
            return None
        # read the rest of the frame:
        response = self.ser.read(23-4)
        if response == None:
            # print("error, frame length is too short")
            return None
        response = header + response
        if response[-4:] != self.REPORT_TERMINATOR:
            # error, packet seems incorrect
            # print("error, frame terminator is incorrect")
            return None
        # self.print_bytes(response)
        self.parse_report(response)
        return response

    def get_detection_distance(self):
        return self.meas["detection_distance"]
                
    def scan_for_people(self):
        # Check for the presence of people using the sensor
        self.read_serial_frame()

        if self.meas['state'] == self.STATE_MOVING_TARGET or self.meas['state'] == self.STATE_COMBINED_TARGET:
            # print("Detected moving target")
            self.standing_timer = 0

            if self.moving_timer < self.moving_threshold:
                self.moving_timer += 1
                # print(f"Moving timer: {self.moving_timer} seconds")

            elif self.moving_timer >= self.moving_threshold:
                # print("Threshold exceeded: resetting moving timer")
                self.person_detected = True
                self.moving_timer = 0
                self.mmWaveTimer.reset()  # Reset the timer
                return self.person_detected

        elif self.meas['state'] == self.STATE_STATIONARY_TARGET:
            self.standing_timer += 1
            # print(f"Standing timer: {self.standing_timer} seconds")

            # Check if a person has been standing still for too long
            if self.standing_timer >= self.standing_threshold:
                # print("Threshold exceeded: resetting standing timer")
                self.moving_timer = 0
                self.standing_timer = 0
                self.person_detected = False
                self.mmWaveTimer.reset()  # Reset the timer
                return self.person_detected
        return self.person_detected


