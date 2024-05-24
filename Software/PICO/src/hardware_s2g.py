import time
import neopixel
from machine import Pin, PWM, I2C, UART
from system_utils import Timer

class WS2812:
    def __init__(self, pin_number, num_leds, brightness):
        self._np = neopixel.NeoPixel(Pin(pin_number), num_leds, bpp=3, timing=1)
        self._num_leds = num_leds
        self.set_brightness(brightness)
        self.timer = Timer()
        self.pulse_state = "increasing"
        self.brightness_step = 0.000005  # Adjust step for smoother pulsing
        self.current_brightness = 0
        self.pulse_max_brightness = brightness 
        self.pulse_min_brightness = 0

    def set_color(self, color):
        colors = {
            "red": (65535, 0, 0),
            "green": (0, 65535, 0),
            "blue": (0, 0, 65535),
            "yellow": (65535, 65535, 0),
            "cyan": (0, 65535, 65535),
            "magenta": (65535, 0, 65535),
            "white": (65535, 65535, 65535),
            "off": (0, 0, 0)
        }
        color_values = colors.get(color.lower())
        if color_values:
            for i in range(self._num_leds):
                adjusted_color = tuple(int(val * self.current_brightness) for val in color_values)
                self._np[i] = adjusted_color
            self._np.write()
            return color
        else:
            return "Color not found"

    def set_brightness(self, brightness):
        self._brightness = brightness

    def off(self):
        self.set_color("off")

    def start_pulsing(self, color, interval_ms):
        self.pulse_color = color
        self.timer.start_timer()
        self.pulse_interval = interval_ms
        self._init_pulse_parameters()
        self._pulse()

    def _init_pulse_parameters(self):
        self.current_brightness = 0
        self.pulse_state = "increasing"

    def _pulse(self):
        while True:
            elapsed_time = self.timer.get_time()
            if elapsed_time >= self.pulse_interval:
                self._update_pulse()
                self.timer.start_timer()  # Reset timer

    def _update_pulse(self):
        if self.pulse_state == "increasing":
            self._increase_pulse()
        else:
            self._decrease_pulse()

    def _increase_pulse(self):
        self.current_brightness += self.brightness_step
        self.set_color(self.pulse_color)
        print(self.current_brightness)
        if self.current_brightness >= self.pulse_max_brightness:
            self.pulse_state = "decreasing"


    def _decrease_pulse(self):
        self.set_color(self.pulse_color)
        print(self.current_brightness)
        self.current_brightness -= self.brightness_step
        if self.current_brightness <= self.pulse_min_brightness:
            self.pulse_state = "increasing"

class ServoMotor:
    """Class for controlling a servo motor."""
    def __init__(self, pin_number):
        self.pwm = PWM(pin_number)
        self.pwm.freq(50)
        self.min_us = 600
        self.max_us = 2400
        self.current_angle = 0

    def set_angle(self, angle):
        pulse_width_us = self.min_us + (self.max_us - self.min_us) * angle / 180
        duty_cycle = int(pulse_width_us / 20000 * 65535)
        self.pwm.duty_u16(duty_cycle)
        self.current_angle = angle

    def get_current_angle(self):
        return self.current_angle

class Door:
    """Class for controlling a door motor and position sensor."""
    def __init__(self, pin_number, angle_closed, angle_open, position_sensor_pin):
        self.servo = ServoMotor(pin_number)
        self.angle_open = angle_open
        self.angle_closed = angle_closed
        self.door_sensor = Pin(position_sensor_pin, Pin.IN, Pin.PULL_UP)
        self.door_state = "closed"

    def open_door(self):
        self.servo.set_angle(self.angle_open)
        if self.servo.get_current_angle() == self.angle_open and self.door_sensor.value() == 0:
            self.door_state = "open"
        return self.door_state

    def close_door(self):
        self.servo.set_angle(self.angle_closed)
        if self.servo.get_current_angle() == self.angle_closed and self.door_sensor.value() == 1:
            self.door_state = "closed"
        return self.door_state

class DoorWithLED(Door, WS2812):
    """Class for controlling a door with an integrated LED strip."""
    def __init__(self, door_pin_number, door_angle_closed, door_angle_open, door_position_sensor_pin, led_pin_number, num_leds, brightness):
        Door.__init__(self, door_pin_number, door_angle_closed, door_angle_open, door_position_sensor_pin)
        WS2812.__init__(self, led_pin_number, num_leds, brightness)

    def open_door(self):
        Door.open_door(self)
        self.set_color("green")

    def close_door(self):
        Door.close_door(self)
        self.set_color("red")

class MAX9744:
    """Class for controlling MAX9744 audio amplifier."""
    def __init__(self, i2c_port, address=0x4B):
        self.i2c = I2C(i2c_port)
        self.address = address
        self.volume = 63

    def set_volume(self, volume):
        self.volume = max(0, min(63, volume))
        try:
            self.i2c.writeto(self.address, bytes([self.volume]))
            return True
        except OSError:
            return False

class PersonDetector:
    """Base class for person detectors."""
    def __init__(self, uart_number, baudrate, tx_pin, rx_pin):
        self.uart = UART(uart_number, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin))
        self.person_detected = False

    def scan_for_people(self):
        raise NotImplementedError

    def get_detection_distance(self):
        raise NotImplementedError

class SeeedPersonDetector(PersonDetector):
    """Class for controlling Seeed Studio mmWave sensor."""
    def scan_for_people(self):
        data = self.uart.read()
        if data:
            self.person_detected = b'\x02' in data or b'\x03' in data
        return self.person_detected

    def get_detection_distance(self):
        return 180


class LD2410PersonDetector:
    """Class for controlling LD2410 mmWave sensor."""
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
    
    standing_threshold = 20  # Threshold for determining if someone has been standing for too long (40 = 4 seconds somehow)
    moving_threshold = 40  # Threshold for determining if someone has been moving for too long

    def __init__(self, uart_number, baudrate, tx_pin, rx_pin):
        """
        Initialize LD2410 mmWave sensor.

        Args:
            uart_number (int): UART number.
            baudrate (int): Baud rate of the UART communication.
            tx_pin (int): Transmit pin number.
            rx_pin (int): Receive pin number.

        Returns:
            None
        """
        self.ser = UART(uart_number, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin), timeout=1)
        self.meas = {
            "state": self.STATE_NO_TARGET,
            "moving_distance": 0,
            "moving_energy": 0,
            "stationary_distance": 0,
            "stationary_energy": 0,
            "detection_distance": 0 
        }
        self.mmWaveTimer = Timer()  # Initialize the Timer for mmWave sensor
        self.person_detected = False  # Variable to track person detection status
        self.standing_timer = 5  # Timer to track how long someone has been standing
        self.moving_timer = 3  # Timer to track how long someone has been moving

    def print_bytes(self, data):
        """
        Print byte data in hexadecimal format.

        Args:
            data (bytes): Byte data to be printed.

        Returns:
            None
        """
        if len(data) == 0:
            print("<no data>")
            return
        text = f"hex: {data[0]:02x}"
        for i in range(1, len(data)):
            text = text + f" {data[i]:02x}"
        print(text)

    def send_command(self, cmd, data=NULLDATA, response_expected=True):
        """
        Send a command to the sensor.

        Args:
            cmd (bytes): Command bytes.
            data (bytes): Data bytes to be sent with the command.
            response_expected (bool): Whether to expect a response from the sensor.

        Returns:
            bytes: Response from the sensor, if expected.
        """
        cmd_data_len = bytes([len(cmd) + len(data), 0x00])
        frame = self.HEADER + cmd_data_len + cmd + data + self.TERMINATOR
        self.ser.write(frame)
        if response_expected:
            response = self.ser.read()
        else:
            response = self.NULLDATA
        return response

    def enable_config(self):
        """
        Enable configuration mode for the sensor.

        Returns:
            None
        """
        response = self.send_command(bytes([0xff, 0x00]), bytes([0x01, 0x00]))
        self.print_bytes(response)

    def end_config(self):
        """
        End configuration mode for the sensor.

        Returns:
            None
        """
        response = self.send_command(bytes([0xfe, 0x00]), response_expected=False)

    def read_firmware_version(self):
        """
        Read the firmware version of the sensor.

        Returns:
            None
        """
        response = self.ser.read()
        if response is None:
            print("Error: No response from serial.")
            return
        self.print_bytes(response)

    def enable_engineering(self):
        """
        Enable engineering mode outputs for the sensor.

        Returns:
            None
        """
        response = self.send_command(bytes([0x62, 0x00]))
        self.print_bytes(response)

    def end_engineering(self):
        """
        End engineering mode outputs for the sensor.

        Returns:
            None
        """
        response = self.send_command(bytes([0x63, 0x00]))
        self.print_bytes(response)

    def read_serial_buffer(self):
        """
        Read the serial buffer.

        Returns:
            bytes: Data read from the serial buffer.
        """
        response = self.ser.read()
        self.print_bytes(response)
        return response

    def print_meas(self):
        """
        Print the sensor measurement data.

        Returns:
            None
        """
        print(f"state: {self.TARGET_NAME[self.meas['state']]}")
        print(f"moving distance: {self.meas['moving_distance']}")
        print(f"moving energy: {self.meas['moving_energy']}")
        print(f"stationary distance: {self.meas['stationary_distance']}")
        print(f"stationary energy: {self.meas['stationary_energy']}")
        print(f"detection distance: {self.meas['detection_distance']}")

    def parse_report(self, data):
        """
        Parse the sensor report data.

        Args:
            data (bytes): Data received from the sensor.

        Returns:
            None
        """
        # Sanity checks
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
        # Data[7] must be report 'head' value 0xaa
        if data[7] != 0xaa:
            print(f"error, frame report head value is incorrect")
            return
        # Sanity checks passed. Store the sensor data in meas
        self.meas["state"] = data[8]
        self.meas["moving_distance"] = data[9] + (data[10] << 8)
        self.meas["moving_energy"] = data[11]
        self.meas["stationary_distance"] = data[12] + (data[13] << 8)
        self.meas["stationary_energy"] = data[14]
        self.meas["detection_distance"] = data[15] + (data[16] << 8)

    def read_serial_until(self, identifier):
        """
        Read serial data until a specific identifier is found.

        Args:
            identifier (bytes): Identifier to search for.

        Returns:
            bytes: Data read until the identifier is found.
        """
        content = bytes([])
        while len(identifier) > 0:
            v = self.ser.read(1)
            if v == None:
                # Timeout
                return None
                break
            if v[0] == identifier[0]:
                content = content + v[0:1]
                identifier = identifier[1:len(identifier)]
            else:
                content = bytes([])
        return content

    def serial_flush(self):
        """
        Flush the serial buffer.

        Returns:
            bytes: Data read from the serial buffer.
        """
        dummy = self.ser.read()
        return dummy

    def read_serial_frame(self):
        """
        Read the serial data frame.

        Returns:
            bytes: Data read from the serial buffer.
        """
        # Dummy read to flush out the read buffer
        self.serial_flush()
        # time.sleep(0.05) 
        # Keep reading to see a header arrive
        header = self.read_serial_until(self.REPORT_HEADER)
        if header == None:
            return None
        # Read the rest of the frame
        response = self.ser.read(23-4)
        if response == None:
            return None
        response = header + response
        if response[-4:] != self.REPORT_TERMINATOR:
            return None
        self.parse_report(response)
        return response

    def get_detection_distance(self):
        """
        Get the detection distance from the sensor.

        Returns:
            int: Detection distance.
        """
        return self.meas["detection_distance"]
                
    def scan_for_people(self):
        """
        Scan for people using the sensor and determine if they are moving or stationary.

        Returns:
            bool: True if person detected, False otherwise.
        """
        # Check for the presence of people using the sensor
        self.read_serial_frame()

        if self.meas['state'] == self.STATE_MOVING_TARGET or self.meas['state'] == self.STATE_COMBINED_TARGET:
            self.standing_timer = 0

            if self.moving_timer < self.moving_threshold:
                self.moving_timer += 1

            elif self.moving_timer >= self.moving_threshold:
                self.person_detected = True
                self.moving_timer = 0
                self.mmWaveTimer.reset()  # Reset the timer
                return self.person_detected

        elif self.meas['state'] == self.STATE_STATIONARY_TARGET:
            self.standing_timer += 1

            # Check if a person has been standing still for too long
            if self.standing_timer >= self.standing_threshold:
                self.moving_timer = 0
                self.standing_timer = 0
                self.person_detected = False
                self.mmWaveTimer.reset()  # Reset the timer
                return self.person_detected
        return self.person_detected

if __name__ == "__main__":
    # Initialize the WS2812 LED strip on pin 2 with 8 LEDs and initial brightness of 50
    led_strip = WS2812(pin_number=2, num_leds=2, brightness=0.001)
    
    # Start pulsing with red color, pulse interval of 500 ms
    led_strip.start_pulsing(color="green", interval_ms=3)

