from machine import Pin, PWM, UART


class RGB:
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

class DOOR:
    def __init__(self, pin_number, angle_closed, angle_open):
        self.servo = SERVOMOTOR(Pin(pin_number)) 
        self.pin_number = pin_number 
        self.angle_open = angle_open # maximum opening angle
        self.angle_closed = angle_closed # maximum closing angle
        self.door_state = "closed" # initial state of the door

    def open_door(self):
        print(f"unlock_and_open_{self}")
        self.servo.set_angle(self.angle_open)
        self.door_state = "open"
        return self.door_state

    def close_door(self):
        print(f"close_and_lock_{self}")
        self.servo.set_angle(self.angle_closed)
        self.door_state = "closed"
        return self.door_state

class PERSONDETECTOR:
    def __init__(self, uart_configs, on_person_detected, on_person_not_detected):
        self._uart_sensors = []
        self._on_person_detected = on_person_detected
        self._on_person_not_detected = on_person_not_detected
        for uart_config in uart_configs:
            uart_number, baudrate, (tx_pin, rx_pin) = uart_config
            uart = UART(uart_number, baudrate=baudrate, tx=tx_pin, rx=rx_pin)
            self._uart_sensors.append(uart)
    
    def poll_uart_data(self):
        for uart in self._uart_sensors:
            data = uart.read(10)  # Read up to 10 bytes from UART
            if data:
                # Check data from UART and call appropriate callbacks
                if b'\x02' in data:
                    self._on_person_detected(f"Sensor {self._uart_sensors.index(uart) + 1}: Somebody moved")
                elif b'\x01' in data:
                    self._on_person_detected(f"Sensor {self._uart_sensors.index(uart) + 1}: Somebody stopped moving")
                elif b'\x01' in data:
                    self._on_person_detected(f"Sensor {self._uart_sensors.index(uart) + 1}: Somebody is close")
                elif b'\x02' in data:
                    self._on_person_detected(f"Sensor {self._uart_sensors.index(uart) + 1}: Somebody is away")
                else:
                    self._on_person_not_detected(f"Sensor {self._uart_sensors.index(uart) + 1}: No human activity detected")

class SERVOMOTOR:
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