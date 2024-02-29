import time
from machine import Pin, I2C
from button import Button
from potmeter import Potentiometer
from rgbled import RGBLED
from pwm import pwm
from sh1106 import SH1106_I2C


# Define hardware objects
class Hardware:
    def __init__(self):
        self.ledDoor2Lock = RGBLED(10, 11, 12)
        self.ledDoor1Lock = RGBLED(2, 3, 4)
        self.ledScanner = RGBLED(6, 7, 8)
        self.ledDoor1Motor = pwm(21)
        self.ledDoor2Motor = pwm(22)
        self.Piezo = pwm(16)
        self.Button1 = Button(pin_number=5, callback=None)
        self.Button2 = Button(pin_number=9, callback=None)
        self.Button3 = Button(pin_number=13, callback=None)
        self.Switch1 = Button(pin_number=20, callback=None)
        self.Switch2 = Button(pin_number=19, callback=None)
        self.Switch3 = Button(pin_number=18, callback=None)
        self.Switch4 = Button(pin_number=17, callback=None)
        self.Pot1 = Potentiometer(pin_number=27, callback=None)

    def initialize_display(self):
        scl_pin, sda_pin = Pin(1), Pin(0)
        OLEDi2c = I2C(0, scl=scl_pin, sda=sda_pin, freq=400000)
        display = SH1106_I2C(128, 64, OLEDi2c, Pin(16), 0x3c, 180)
        return display


# Define Constants
class States:
    DOOR1_CLOSED_WITH_PERSON = 1
    FERROMETAL_DETECTION = 2
    DOOR2_CLOSED_WITH_PERSON = 3


# Define State Machine
class StateMachine:
    def __init__(self, hardware):
        self.hardware = hardware
        self.current_state = None

    def start(self):
        self.current_state = Door1ClosedWithPersonState(self.hardware)
        self.current_state.enter_state()

    def update(self):
        while True:
            new_state = self.current_state.check_transition()
            if new_state:
                self.current_state.exit_state()
                self.current_state = new_state
                self.current_state.enter_state()
            self.current_state.execute_action()
            time.sleep(0.1)


# Define States
class State:
    def __init__(self, hardware):
        self.hardware = hardware

    def enter_state(self):
        pass

    def exit_state(self):
        pass

    def check_transition(self):
        pass

    def execute_action(self):
        pass


class Door1ClosedWithPersonState(State):
    def __init__(self, hardware):
        super().__init__(hardware)

    def enter_state(self):
        display = self.hardware.initialize_display()
        display.text("Wacht op persoon in gebied A", 0, 0, 1)
        display.show()

    def check_transition(self):
        if self.hardware.Switch3.is_pressed():
            return FerrometalDetectionState(self.hardware)


class FerrometalDetectionState(State):
    def __init__(self, hardware):
        super().__init__(hardware)

    def enter_state(self):
        display = self.hardware.initialize_display()
        display.text("Ferrometaal detectie", 0, 0, 1)
        display.show()

    def check_transition(self):
        # Pseudo code for checking ferrometal detection
        # You can add conditions based on your actual implementation
        return Door2ClosedWithPersonState(self.hardware)


class Door2ClosedWithPersonState(State):
    def __init__(self, hardware):
        super().__init__(hardware)

    def enter_state(self):
        display = self.hardware.initialize_display()
        display.text("Wacht op sluiten deur 2", 0, 0, 1)
        display.show()

    def check_transition(self):
        if not self.hardware.Switch2.is_pressed():
            return Door1ClosedWithPersonState(self.hardware)


if __name__ == "__main__":
    hardware = Hardware()
    machine = StateMachine(hardware)
    machine.start()
    while True:
        machine.update()
        time.sleep(0.1)
    