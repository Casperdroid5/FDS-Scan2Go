# Import statements should be grouped and placed at the beginning of the file
from machine import Pin, I2C
import time
from button import Button
from potmeter import Potentiometer
from rgbled import RGBLED
from pwm import pwm
from sh1106 import SH1106_I2C

# Define hardware objects
ledDoor2Lock = RGBLED(10, 11, 12) 
ledDoor1Lock = RGBLED(2, 3, 4)     
ledScanner = RGBLED(6, 7, 8)      
ledDoor1Motor = pwm(21) 
ledDoor2Motor = pwm(22) 
Piezo = pwm(16)
Button1 = Button(pin_number=5, callback=None)
Button2 = Button(pin_number=9, callback=None)
Button3 = Button(pin_number=13, callback=None)
Switch1 = Button(pin_number=20, callback=None)
Switch2 = Button(pin_number=19, callback=None)
Switch3 = Button(pin_number=18, callback=None)
Switch4 = Button(pin_number=17, callback=None)
Pot1 = Potentiometer(pin_number=27, callback=None)

# Define I2C communication pins
scl_pin, sda_pin = Pin(1), Pin(0)

# Initialize I2C bus and OLED display
OLEDi2c = I2C(0, scl=scl_pin, sda=sda_pin, freq=400000)
display = SH1106_I2C(128, 64, OLEDi2c, Pin(16), 0x3c, 180)

# Define brightness level for OLED display
OLEDbrightnesslevel = 100  # brightness 0-255

class StateMachine:
    def __init__(self):
        # Initialize hardware objects
        self.ledDoor2Lock = ledDoor2Lock
        self.ledDoor1Lock = ledDoor1Lock
        self.ledScanner = ledScanner
        self.ledDoor1Motor = ledDoor1Motor
        self.ledDoor2Motor = ledDoor2Motor
        self.Piezo = Piezo
        self.Button1 = Button1
        self.Button2 = Button2
        self.Button3 = Button3
        self.Switch1 = Switch1
        self.Switch2 = Switch2
        self.Switch3 = Switch3
        self.Switch4 = Switch4
        self.Pot1 = Pot1
        self.display = display
        self.current_state = None
    
    def start(self):
        # Define initial state and actions
        self.current_state = LockedState()  # Starting state is LockedState
        self.current_state.enter_state()

    def update(self):
        # Check for state transitions and execute actions
        new_state = self.current_state.check_transition()
        if new_state:
            self.current_state.exit_state()
            self.current_state = new_state
            self.current_state.enter_state()
        self.current_state.execute_action()

class State:
    def __init__(self, display, button1, button2, button3):
        self.display = display
        self.button1 = button1
        self.button2 = button2
        self.button3 = button3

    def enter_state(self):
        pass

    def exit_state(self):
        pass

    def check_transition(self):
        pass

    def execute_action(self):
        pass


class InitialState(State):
    def enter_state(self):
        self.display.fill(0)  # Clear the display
        self.display.text("Initial State", 0, 0, 1)  # Display initial state message
        self.display.show()

    def check_transition(self):
        if self.button1.is_pressed():
            return LockedState(self.display, self.button1, self.button2, self.button3)
        return None

    def execute_action(self):
        pass


class LockedState(State):
    def enter_state(self):
        self.display.fill(0)  # Clear the display
        self.display.text("Door is locked", 0, 0, 1)  # Display locked state message
        self.display.show()

    def check_transition(self):
        if self.button2.is_pressed():
            return UnlockingState(self.display, self.button1, self.button2, self.button3)
        return None

    def execute_action(self):
        pass


class UnlockingState(State):
    def enter_state(self):
        self.display.fill(0)  # Clear the display
        self.display.text("Unlocking door", 0, 0, 1)  # Display unlocking state message
        self.display.show()

    def check_transition(self):
        if self.button3.is_pressed():
            return OpenState(self.display, self.button1, self.button2, self.button3)
        return None

    def execute_action(self):
        pass


class OpenState(State):
    def enter_state(self):
        self.display.fill(0)  # Clear the display
        self.display.text("Door is open", 0, 0, 1)  # Display open state message
        self.display.show()

    def check_transition(self):
        if self.button1.is_pressed():
            return ClosingState(self.display, self.button1, self.button2, self.button3)
        return None

    def execute_action(self):
        pass


class ClosingState(State):
    def enter_state(self):
        self.display.fill(0)  # Clear the display
        self.display.text("Closing door", 0, 0, 1)  # Display closing state message
        self.display.show()

    def check_transition(self):
        if self.button2.is_pressed():
            return LockedState(self.display, self.button1, self.button2, self.button3)
        return None

    def execute_action(self):
        pass


class StateMachine:
    def __init__(self):
        self.display = display
        self.button1 = Button1
        self.button2 = Button2
        self.button3 = Button3
        self.current_state = None

    def start(self):
        self.current_state = InitialState(self.display, self.button1, self.button2, self.button3)
        self.current_state.enter_state()

    def update(self):
        new_state = self.current_state.check_transition()
        if new_state:
            self.current_state.exit_state()
            self.current_state = new_state
            self.current_state.enter_state()
        self.current_state.execute_action()


if __name__ == "__main__":
    machine = StateMachine()
    machine.start()
    while True:
        machine.update()
        time.sleep(0.1)
