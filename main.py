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
        self.current_state = InitialState(self.display, self.Switch1, self.Switch2, self.Switch3, self.Switch4)
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
    def __init__(self, display, switch1, switch2, switch3, switch4):
        self.display = display
        self.switch1 = switch1
        self.switch2 = switch2
        self.switch3 = switch3
        self.switch4 = switch4
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
        self.display.text("Door 1: Unlocked", 0, 0, 1)  # Display door status
        self.display.text("Door 2: Closed", 0, 10, 1)
        self.display.text("Area: A", 0, 20, 1)
        self.display.show()

    def check_transition(self):
        if self.switch3.is_pressed():
            return DoorClosingState(self.display, self.switch1, self.switch2, self.switch3, self.switch4)


class DoorClosingState(State):
    def enter_state(self):
        self.display.fill(0)  # Clear the display
        self.display.text("Closing Door 1", 0, 0, 1)  # Display door closing message
        self.display.show()

    def check_transition(self):
        if not self.switch1.is_pressed():
            return FerrometalDetectionState(self.display, self.switch1, self.switch2, self.switch3, self.switch4)


class FerrometalDetectionState(State):
 
    def enter_state(self):
        self.display.fill(0)  # Clear the display
        self.display.show()
        self.display.text("Start Detect", 0, 0, 1)  # Display detection message
        self.display.show()
        time.sleep(1)
        self.display.fill(0)  # Clear the display
        self.display.show()
        pot_value = self.Pot1.read_value()
        
        if 0 <= pot_value < 100:
            ledScanner.set_color(0, 6000, 0)  # Green color
        elif 10000 >= pot_value < 30000:
            ledScanner.set_color(6000, 6000, 0)  # Yellow color
        elif 30000 >= pot_value <= 66000:
            ledScanner.set_color(6000, 0, 0)  # Red color
        self.display.text("Ferrometal Detection", 0, 0, 1)  # Display detection message
        self.display.show()

    def check_transition(self):
        if not self.switch3.is_pressed() and self.switch4.is_pressed():
            pot_value = self.Pot1.read_value()
            if 0 <= pot_value < 1000:
                return Door2UnlockState(self.display, self.switch1, self.switch2, self.switch3, self.switch4)


class Door2UnlockState(State):
    def enter_state(self):
        self.display.fill(0)  # Clear the display
        self.display.text("Unlocking Door 2", 0, 0, 1)  # Display door unlocking message
        self.display.show()

    def check_transition(self):
        if not self.switch2.is_pressed():
            return Door2WaitingState(self.display, self.switch1, self.switch2, self.switch3, self.switch4)


class Door2WaitingState(State):
    def enter_state(self):
        self.display.fill(0)  # Clear the display
        self.display.text("Waiting for Door 2", 0, 0, 1)  # Display waiting message
        self.display.show()

    def check_transition(self):
        if self.switch2.is_pressed() and self.switch4.is_pressed():
            return Door2LockingState(self.display, self.switch1, self.switch2, self.switch3, self.switch4)
 


class Door2LockingState(State):
    def enter_state(self):
        self.display.fill(0)  # Clear the display
        self.display.text("Locking Door 2", 0, 0, 1)  # Display door locking message
        self.display.show()

    def check_transition(self):
        if not self.switch2.is_pressed():
            return Door1UnlockState(self.display, self.switch1, self.switch2, self.switch3, self.switch4)


class Door1UnlockState(State):
    def enter_state(self):
        self.display.fill(0)  # Clear the display
        self.display.text("Unlocking Door 1", 0, 0, 1)  # Display door unlocking message
        self.display.show()

    def check_transition(self):
        if not self.switch1.is_pressed():
            return InitialState(self.display, self.switch1, self.switch2, self.switch3, self.switch4)


if __name__ == "__main__":
    machine = StateMachine()
    machine.start()
    while True:
        machine.update()
        time.sleep(0.1)
