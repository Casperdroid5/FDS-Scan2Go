from machine import Pin, PWM, UART
import neopixel

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
        print(f"open_{self}")
        self.servo.set_angle(self.angle_open)
        if self.servo.get_current_angle() == self.angle_open and self.door_sensor.value() == 0:
            print("New state: dooropened")
            self.door_state = "open"
            return self.door_state

    def close_door(self):
        print(f"close_{self}")
        self.servo.set_angle(self.angle_closed)
        if self.servo.get_current_angle() == self.angle_closed and self.door_sensor.value() == 1:
            print("New state: doorclosed")
            self.door_state = "closed"
            return self.door_state

class PERSONDETECTOR: # mmWave sensor
    def __init__(self, uart_number, baudrate, tx_pin, rx_pin):
        self.uart_number = uart_number
        self.baudrate = baudrate
        self.tx_pin = tx_pin  
        self.rx_pin = rx_pin 
        self._uart_sensor = UART(uart_number, baudrate, tx_pin, rx_pin)
        self.humanpresence = "unknown"

    def poll_uart_data(self):
        data = self._uart_sensor.read()
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

