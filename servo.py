from machine import Pin, PWM

class Servo(PWM):
    
    get_current_angle = lambda self: self.current_angle
    def __init__(self, pin_number):
        super().__init__(Pin(pin_number, Pin.OUT))
        self.freq(50)  # Set PWM frequency to 50 Hz for servo control
        self.min_us = 600  # Minimum pulse width in microseconds for 0 degrees
        self.max_us = 2400  # Maximum pulse width in microseconds for 180 degrees
        self.current_angle = 0  # Initialize current angle to 0

    def set_angle(self, angle):
        # Convert angle to pulse width
        pulse_width_us = self.min_us + (self.max_us - self.min_us) * angle / 180
        # Convert pulse width from microseconds to duty cycle (0-65535)
        duty_cycle = int(pulse_width_us / 20000 * 65535)  # 20000 microseconds = 20 milliseconds (period)
        self.duty_u16(duty_cycle)  # Set duty cycle to control servo position
        self.current_angle = angle  # Update current angle
        return self.get_current_angle()
