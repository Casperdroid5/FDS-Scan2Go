# hardware_s2g.py
import time
import neopixel
from machine import Pin, PWM, I2C, UART
from system_utils import Timer

class WS2812:
    """Class for controlling WS2812 LED strip."""
    def __init__(self, pin_number, num_leds, brightness):
        self._np = neopixel.NeoPixel(Pin(pin_number), num_leds, bpp=3, timing=1)
        self._num_leds = num_leds
        self.set_brightness(brightness)

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
                adjusted_color = tuple(int(val * self._brightness) for val in color_values)
                self._np[i] = adjusted_color
            self._np.write()
            return color
        else:
            return "Color not found"

    def set_brightness(self, brightness):
        self._brightness = brightness / 10000

    def off(self):
        self.set_color("off")

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

class LD2410PersonDetector(PersonDetector):
    """Class for controlling LD2410 mmWave sensor."""
    def __init__(self, uart_number, baudrate, tx_pin, rx_pin):
        super().__init__(uart_number, baudrate, tx_pin, rx_pin)
        self.meas = {
            "state": 0,
            "moving_distance": 0,
            "moving_energy": 0,
            "stationary_distance": 0,
            "stationary_energy": 0,
            "detection_distance": 0 
        }

    def scan_for_people(self):
        data = self.uart.read()
        if data:
            if data[8] == 1 or data[8] == 3:
                self.person_detected = True
            else:
                self.person_detected = False
        return self.person_detected

    def get_detection_distance(self):
        return self.meas["detection_distance"]
