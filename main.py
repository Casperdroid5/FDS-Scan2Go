#Todo:
    # altijd iets returnen bij een functie
    # functies zo klein mogelijk houden 1 functie = 1 taak
    # geen print statements in de functies
    # geen while True gebruiken
    # time sleep vermijden
    # Alles functioneel, dus liever geen waardes in de code

from machine import *
from hardware import rgb, Door, Display

# Variables 
AngleOpen = 90 
AngleClosed = 0
ferro_free = False
patient_returned_from_mri = False

class StateMachine:
    def __init__(self):
        # Initialize I2C bus
        scl_pin, sda_pin = Pin(1), Pin(0)
        self.i2c = I2C(0, scl=scl_pin, sda=sda_pin, freq=400000)

        # Create SH1106 display object
        self.display = Display(128, 64, self.i2c, Pin(16), 0x3c, 180)

        # Define integer constants for states
        self.INITIALISATION_STATE = 0
        self.WAIT_FOR_USER_FIELD_A_STATE = 1
        self.WAIT_FOR_USER_FIELD_B_STATE = 2
        self.FERROMETAL_DETECTION_STATE = 3
        self.UNLOCK_AND_OPEN_DOOR1_STATE = 4
        self.LOCK_AND_CLOSE_DOOR1_STATE = 5
        self.UNLOCK_AND_OPEN_DOOR2_STATE = 6
        self.LOCK_AND_CLOSE_DOOR2_STATE = 7
        self.EMERGENCY_STATE = 8

        # Initialize hardware components
        self.Door2State = rgb(10, 11, 12)
        self.Door1State = rgb(2, 3, 4)
        self.FerroDetectLED = rgb(6, 7, 8)
        self.Door1 = Door(14, AngleClosed, AngleOpen)
        self.Door2 = Door(15, AngleClosed, AngleOpen)
        self.Pot1 = ADC(27)
        self.field_a = Pin(18, Pin.IN, Pin.PULL_UP)
        self.field_b = Pin(17, Pin.IN, Pin.PULL_UP)
        
# Functions
    def display_state_info(self, state_info):
        self.display.DisplayStateInfo("-State: " + state_info + "-")

# State Functions
    def initialisation_state(self):
        self.display_state_info("Init")
        self.Door2.Open()
        self.Door1.Open()
        return self.WAIT_FOR_USER_FIELD_A_STATE

    def wait_for_user_field_a_state(self):
        self.display_state_info("WFieldA")
        if self.field_a.value() == 0 and self.field_b.value() == 1:
            return self.LOCK_AND_CLOSE_DOOR1_STATE if not self.patient_returned_from_mri else self.WAIT_FOR_USER_FIELD_B_STATE
        return self.WAIT_FOR_USER_FIELD_A_STATE

    def wait_for_user_field_b_state(self):
        self.display_state_info("WFieldB")
        if self.field_a.value() == 1 and self.field_b.value() == 0:
            if not self.patient_returned_from_mri and self.ferro_free:
                return self.UNLOCK_AND_OPEN_DOOR2_STATE
            elif not self.patient_returned_from_mri and not self.ferro_free:
                return self.FERROMETAL_DETECTION_STATE
            elif self.patient_returned_from_mri:
                return self.WAIT_FOR_USER_FIELD_A_STATE

    def ferrometal_detection_state(self):
        self.display_state_info("FerroD")
        pot_value = self.Pot1.read_u16()
        if 0 <= pot_value < 40000:
            self.FerroDetectLED.Setcolor("green")  # Green
            self.ferro_free = True
            return self.UNLOCK_AND_OPEN_DOOR2_STATE
        elif 40000 <= pot_value <= 66000:
            self.FerroDetectLED.Setcolor("red")  # Red
            return self.UNLOCK_AND_OPEN_DOOR1_STATE

    def unlock_and_open_door1_state(self):
        self.display_state_info("Open1")
        self.Door1.Open()
        self.Door1State.Setcolor("green")
        return self.WAIT_FOR_USER_FIELD_A_STATE

    def lock_and_close_door1_state(self):
        self.display_state_info("Lock1")
        self.Door1.Open()
        self.Door1State.Setcolor("red")  # Set the color to red
        return self.LOCK_AND_CLOSE_DOOR2_STATE

    def unlock_and_open_door2_state(self):
        self.display_state_info("Open2")
        self.Door2.Open()
        self.Door2State.Setcolor("green")
        return self.WAIT_FOR_USER_FIELD_B_STATE

    def lock_and_close_door2_state(self):
        self.display_state_info("Lock2")
        self.Door2.Open()
        self.Door2State.Setcolor("red")
        if self.patient_returned_from_mri:
            self.patient_returned_from_mri = False
            self.ferro_free = False
            return self.UNLOCK_AND_OPEN_DOOR1_STATE
        else:
            return self.WAIT_FOR_USER_FIELD_B_STATE

    def emergency_state(self):
        self.display_state_info("Emergency")
        self.Door1.Open()
        self.Door2.Open()
        self.Door1State.Setcolor("blue")
        self.Door2State.Setcolor("blue")
        self.FerroDetectLED.Setcolor("blue")

    def run(self):
        state = self.initialisation_state()

        while True:
            if state == self.WAIT_FOR_USER_FIELD_A_STATE:
                state = self.wait_for_user_field_a_state()

            elif state == self.WAIT_FOR_USER_FIELD_B_STATE:
                state = self.wait_for_user_field_b_state()

            elif state == self.FERROMETAL_DETECTION_STATE:
                state = self.ferrometal_detection_state()

            elif state == self.UNLOCK_AND_OPEN_DOOR1_STATE:
                state = self.unlock_and_open_door1_state()

            elif state == self.LOCK_AND_CLOSE_DOOR1_STATE:
                state = self.lock_and_close_door1_state()

            elif state == self.UNLOCK_AND_OPEN_DOOR2_STATE:
                state = self.unlock_and_open_door2_state()

            elif state == self.LOCK_AND_CLOSE_DOOR2_STATE:
                state = self.lock_and_close_door2_state()

            elif state == self.EMERGENCY_STATE:
                self.emergency_state()
                break  # Exit the loop

            else:
                print("Invalid state")
                state = self.INITIALISATION_STATE

if __name__ == "__main__":
    FDS = StateMachine()
    FDS.run()
