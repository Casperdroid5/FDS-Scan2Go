from machine import Pin, PWM, UART
import neopixel

class RGB: # regeular RGB LED
    def __init__(self, pin_blue, pin_green, pin_red):
        self._pin_red = PWM(Pin(pin_red, Pin.OUT), freq=1000)
        self._pin_green = PWM(Pin(pin_green, Pin.OUT), freq=1000)
        self._pin_blue = PWM(Pin(pin_blue, Pin.OUT), freq=1000)
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
        red, green, blue = self._COLORS[color.lower()]
        #print(f"{red}, {green}, {blue}")
        self._pin_red.duty_u16(red)
        self._pin_green.duty_u16(green)
        self._pin_blue.duty_u16(blue)
        return color

    def on(self):
        self.set_color("white")
        return "on"

    def off(self):
        self._pin_red.duty_u16(0)
        self._pin_green.duty_u16(0)
        self._pin_blue.duty_u16(0)
        return "off"

class WS2812: # WS2812 RGB LED strip
    def __init__(self, pin_number, num_leds):
        self._np = neopixel.NeoPixel(Pin(pin_number), num_leds)
        self._num_leds = num_leds
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
                self._np[i] = color_values
            self._np.write()
            return color
        else:
            return "Color not found"

    def on(self):
        self.set_color("white")
        return "on"

    def off(self):
        for i in range(self._num_leds):
            self._np[i] = (0, 0, 0)
        self._np.write()
        return "off"


class DOOR: # Servo motor door
    def __init__(self, pin_number, angle_closed, angle_open, door_sensor_pin):
        self.servo = SERVOMOTOR(Pin(pin_number)) 
        self.pin_number = pin_number 
        self.angle_open = angle_open # maximum opening angle
        self.angle_closed = angle_closed # maximum closing angle
        self.door_position = "closed" # initial state of the door
        self.door_sensor = Pin(door_sensor_pin, Pin.IN, Pin.PULL_UP)

    def open_door(self):
        print(f"unlock_and_open_{self}")
        self.servo.set_angle(self.angle_open)
        if self.door_position == "open":
            self.door_position = "open"
        else:
            self.door_position = "error" # failed to open door
        return self.door_position

    def close_door(self):
        print(f"close_and_lock_{self}")
        self.servo.set_angle(self.angle_closed)
        if self.door_position == "closed":
            self.door_position = "closed"
        else:
            self.door_position = "error" # failed to close door
        return self.door_position

    def check_door_position(self):
        return self.door_sensor.value()  # Return the value of the door sensor


class PERSONDETECTOR: # mmWave sensor
    def __init__(self, uart_config):
        uart_number, baudrate, (tx_pin, rx_pin) = uart_config
        self._uart_sensor = UART(uart_number, baudrate=baudrate, tx=tx_pin, rx=rx_pin)

        
    def poll_uart_data(self):
        data = self._uart_sensor.read()
        self.humanpresence = "unknown"
        if data:
            if b'\x02' in data:
                self.humanpresence = "Somebodymoved"
            elif b'\x01' in data:
                self.humanpresence = "Somebodystoppedmoving"
            elif b'\x03' in data:
                self.humanpresence = "Somebodyisclose"
            elif b'\x04' in data:
                self.humanpresence = "Somebodyisaway"
        return self.humanpresence 


class SERVOMOTOR: # Servo motor 
    def __init__(self, pin_number):
        self.pwm = PWM(pin_number)
        self.pwm.freq(50)  # Set PWM frequency to 50 Hz for servo control
        self.min_us = 600  # Minimum pulse width in microseconds for 0 degrees
        self.max_us = 2400  # Maximum pulse width in microseconds for 180 degrees
        self.current_angle = 0  # Initialize current angle to 0

    def set_angle(self, angle):
        # Convert angle to pulse width
        pulse_width_us = self.min_us + (self.max_us - self.min_us) * angle / 180
        # Convert pulse width from microseconds to duty cycle (0-65535)
        duty_cycle = int(pulse_width_us / 20000 * 65535)  # 20000 microseconds = 20 milliseconds (period)
        self.pwm.duty_u16(duty_cycle)  # Set duty cycle to control servo position
        self.current_angle = angle  # Update current angle

    def get_current_angle(self): 
        return self.current_angle
