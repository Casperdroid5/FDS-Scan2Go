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
    def __init__(self, hardware):
        super().__init__(hardware, States.INITIAL)

    def enter_state(self):
        print("Entering InitialState")
        super().enter_state()
        self.update_door_status()

    def update_door_status(self):
        display = self.hardware.initialize_display()
        door1_status = "Unlocked" if self.hardware.Switch1.is_pressed() else "Locked"
        self.hardware.ledDoor1Lock.set_color(0, 6000, 0)  # Green
        door2_status = "Locked" if self.hardware.Switch2.is_pressed() else "Unlocked"
        self.hardware.ledDoor2Lock.set_color(6000, 0, 0)  # Red
        display.text("Door 1: {}".format(door1_status), 0, 10, 1)
        display.text("Door 2: {}".format(door2_status), 0, 20, 1)
        display.text("Area: A", 0, 30, 1)
        display.show()

    def check_transition(self):
        if self.hardware.Switch3.is_pressed():
            return DoorClosingState(self.hardware)

class DoorClosingState(State):
    def __init__(self, hardware):
        super().__init__(hardware, States.DOOR_CLOSING)

    def enter_state(self):
        print("Entering DoorClosingState")
        super().enter_state()
        self.update_door_status()

    def update_door_status(self):
        display = self.hardware.initialize_display()
        door1_status = "Closing"
        self.hardware.ledDoor1Lock.set_color(6000, 5000, 0)  # Yellow
        door2_status = "Locked" if self.hardware.Switch2.is_pressed() else "Unlocked"
        self.hardware.ledDoor2Lock.set_color(6000, 0, 0)  # Red        
        display.text("Door 1: {}".format(door1_status), 0, 10, 1)
        display.text("Door 2: {}".format(door2_status), 0, 20, 1)
        display.text("Area: A", 0, 30, 1)
        display.show()

    def check_transition(self):
        if not self.hardware.Switch1.is_pressed():
            return FerrometalDetectionState(self.hardware)

class FerrometalDetectionState(State):
    def __init__(self, hardware):
        super().__init__(hardware, States.FERROMETAL_DETECTION)

    def enter_state(self):
        print("Entering FerrometalDetectionState")
        super().enter_state()
        self.update_door_status()

    def update_door_status(self):
        display = self.hardware.initialize_display()
        door1_status = "Locked"
        self.hardware.ledDoor1Lock.set_color(6000, 0, 0)  # Red
        door2_status = "Locked" if self.hardware.Switch2.is_pressed() else "Open"
        self.hardware.ledDoor2Lock.set_color(6000, 0, 0)  # Red
        display.text("Door 1: {}".format(door1_status), 0, 10, 1)
        display.text("Door 2: {}".format(door2_status), 0, 20, 1)
        display.text("Area: A", 0, 30, 1)
        display.show()

    def check_transition(self):
        print("Checking transition in FerrometalDetectionState")
        pot_value = self.hardware.Pot1.read_value()
        print("Potentiometer value:", pot_value)
        if 0 <= pot_value < 10000:
            self.hardware.ledScanner.set_color(0, 6000, 0)  # Green   
            print("Transitioning to Door2UnlockState")             
            return Door2UnlockState(self.hardware)

        elif 10000 <= pot_value < 30000:
            self.hardware.ledScanner.set_color(6000, 5000, 0)  # Yellow            
            print("YellowState")
        elif 30000 <= pot_value <= 70000:
            self.hardware.ledScanner.set_color(6000, 0, 0)  # Red           
            print("RedState")
        print("No transition in FerrometalDetectionState")
        return None  # Blijf in dezelfde state totdat aan de voorwaarden is voldaan
        

class Door2UnlockState(State):
  
    print("Entering Door2UnlockState")
    def __init__(self, hardware):
        super().__init__(hardware, States.DOOR2_UNLOCK)
        time.sleep(2)
        self.hardware.ledScanner.set_color(0, 0, 0)  # RGB Led off    
    def enter_state(self):
        print("Entering Door2UnlockState")
        super().enter_state()
        # Voeg code toe voor deur 2 ontgrendelen
        self.hardware.ledDoor2Lock.set_color(0, 6000, 0)  # Green
        self.update_door_status()

    def update_door_status(self):
        display = self.hardware.initialize_display()
        door1_status = "Locked"
        door2_status = "Unlocked"
        display.text("Door 1: {}".format(door1_status), 0, 10, 1)
        display.text("Door 2: {}".format(door2_status), 0, 20, 1)
        display.text("Area: A", 0, 30, 1)
        display.show()

    def check_transition(self):
        if not self.hardware.Switch2.is_pressed():
            return Door2WaitingState(self.hardware)

class Door2WaitingState(State):
    def __init__(self, hardware):
        super().__init__(hardware, States.DOOR2_WAITING)

    def enter_state(self):
        print("Entering Door2WaitingState")
        super().enter_state()

    def check_transition(self):
        if self.hardware.Switch2.is_pressed() and not self.hardware.Switch4.is_pressed():
            return Door2LockingState(self.hardware)

class Door2LockingState(State):
    def __init__(self, hardware):
        super().__init__(hardware, States.DOOR2_LOCKING)

    def enter_state(self):
        print("Entering Door2LockingState")
        super().enter_state()
        # Voeg code toe voor deur 2 vergrendelen
        self.hardware.ledDoor2Lock.set_color(6000, 0, 0)  # Rood
        self.update_door_status()

    def update_door_status(self):
        display = self.hardware.initialize_display()
        door1_status = "Unlocked"
        door2_status = "Closed"
        display.text("Door 1: {}".format(door1_status), 0, 10, 1)
        display.text("Door 2: {}".format(door2_status), 0, 20, 1)
        display.text("Area: A", 0, 30, 1)
        display.show()

    def check_transition(self):
        if not self.hardware.Switch2.is_pressed() and self.hardware.Switch4.is_pressed():
            return Door1UnlockState(self.hardware)

class Door1UnlockState(State):
    def __init__(self, hardware):
        super().__init__(hardware, States.DOOR1_UNLOCK)

    def enter_state(self):
        print("Entering Door1UnlockState")
        super().enter_state()
        # Voeg code toe voor deur 1 ontgrendelen
        self.hardware.ledDoor1Lock.set_color(0, 6000, 0)  # Groen
        self.update_door_status()

    def update_door_status(self):
        display = self.hardware.initialize_display()
        door1_status = "Unlocked"
        door2_status = "Closed"
        display.text("Door 1: {}".format(door1_status), 0, 10, 1)
        display.text("Door 2: {}".format(door2_status), 0, 20, 1)
        display.text("Area: A", 0, 30, 1)
        display.show()

    def check_transition(self):
        if not self.hardware.Switch1.is_pressed():
            return InitialState(self.hardware)

# Voeg andere states toe zoals hierboven beschreven...

if __name__ == "__main__":
    hardware = Hardware()
    machine = StateMachine(hardware)
    machine.start()
    while True:
        machine.update()
        time.sleep(0.1) 
        