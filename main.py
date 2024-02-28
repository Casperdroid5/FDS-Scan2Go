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
        self.Button1 = Button(pin_number=5, callback=self.handle_button1)
        self.Button2 = Button(pin_number=9, callback=self.handle_button2)
        self.Button3 = Button(pin_number=13, callback=self.handle_button3)
        self.Switch1 = Button(pin_number=20, callback=None)
        self.Switch2 = Button(pin_number=19, callback=None)
        self.Switch3 = Button(pin_number=18, callback=None)
        self.Switch4 = Button(pin_number=17, callback=None)
        self.Pot1 = Potentiometer(pin_number=27, callback=None)

    def handle_button1(self):
        pass

    def handle_button2(self):
        pass

    def handle_button3(self):
        pass

    def initialize_display(self):
        scl_pin, sda_pin = Pin(1), Pin(0)
        OLEDi2c = I2C(0, scl=scl_pin, sda=sda_pin, freq=400000)
        display = SH1106_I2C(128, 64, OLEDi2c, Pin(16), 0x3c, 180)
        return display

# Define Constants
class States:
    INITIAL = 1
    DOOR_CLOSING = 2
    FERROMETAL_DETECTION = 3
    DOOR2_UNLOCK = 4
    DOOR2_WAITING = 5
    DOOR2_LOCKING = 6
    DOOR1_UNLOCK = 7

# Define State Machine
class StateMachine:
    def __init__(self, hardware):
        self.hardware = hardware
        self.current_state = None

    def start(self):
        self.current_state = InitialState(self.hardware)
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
    def __init__(self, hardware, state_number):
        self.hardware = hardware
        self.state_number = state_number

    def enter_state(self):
        display = self.hardware.initialize_display()
        self.update_display(display)

    def update_display(self, display):
        display.fill(0)
        display.text("State: {}".format(self.state_number), 0, 0, 1)
        display.show()

    def exit_state(self):
        pass

    def check_transition(self):
        pass

    def execute_action(self):
        pass

class InitialState(State):
    print("Entering InitialState")
    def __init__(self, hardware):
        super().__init__(hardware, States.INITIAL)

    def check_transition(self):
        if self.hardware.Switch3.is_pressed():
            return DoorClosingState(self.hardware)

class DoorClosingState(State):
    print("Entering DoorClosingState")
    def __init__(self, hardware):
        super().__init__(hardware, States.DOOR_CLOSING)

    def check_transition(self):
        if not self.hardware.Switch1.is_pressed():
            return FerrometalDetectionState(self.hardware)

class FerrometalDetectionState(State):
    print("Entering FerrometalDetectionState")
    def __init__(self, hardware):
        super().__init__(hardware, States.FERROMETAL_DETECTION)

    def enter_state(self):
        super().enter_state()
        self.display = self.hardware.initialize_display()

    def check_transition(self):
        if not self.hardware.Switch3.is_pressed() and self.hardware.Switch4.is_pressed():
            pot_value = self.hardware.Pot1.read_value()
            if not (0 <= pot_value < 1000):  # Overgang als de waarde buiten het bereik ligt
                return Door2UnlockState(self.hardware)
        # Geen overgang als de waarde binnen het bereik ligt
        return super().check_transition()

    def update_display(self, display):
        super().update_display(display)
        pot_value = self.hardware.Pot1.read_value()
        display.text("Pot: {}".format(pot_value), 0, 10, 1)
        display.show()


class Door2UnlockState(State):
    print("Entering Door2UnlockState")
    def __init__(self, hardware):
        super().__init__(hardware, States.DOOR2_UNLOCK)

    def enter_state(self):
        print("Entering Door2UnlockState")  # Tijdelijke uitvoer toevoegen
        super().enter_state()

    def check_transition(self):
        if not self.hardware.Switch2.is_pressed():
            return Door2WaitingState(self.hardware)

    def update_display(self, display):
        print("Updating display in Door2UnlockState")  # Tijdelijke uitvoer toevoegen
        super().update_display(display)

class Door2WaitingState(State):
    print("Entering Door2WaitingState")
    def __init__(self, hardware):
        super().__init__(hardware, States.DOOR2_WAITING)

    def check_transition(self):
        if self.hardware.Switch2.is_pressed() and self.hardware.Switch4.is_pressed():
            return Door2LockingState(self.hardware)

class Door2LockingState(State):
    print("Entering Door2LockingState")
    def __init__(self, hardware):
        super().__init__(hardware, States.DOOR2_LOCKING)

    def check_transition(self):
        if not self.hardware.Switch2.is_pressed():
            return Door1UnlockState(self.hardware)

class Door1UnlockState(State):
    print("Entering Door1UnlockState")
    def __init__(self, hardware):
        super().__init__(hardware, States.DOOR1_UNLOCK)

    def check_transition(self):
        if not self.hardware.Switch1.is_pressed():
            return InitialState(self.hardware)

if __name__ == "__main__":
    hardware = Hardware()
    machine = StateMachine(hardware)
    machine.start()
    while True:
        machine.update()
        time.sleep(0.1)
