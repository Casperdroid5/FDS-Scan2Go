#Todo:
    # altijd iets returnen bij een functie
    # functies zo klein mogelijk houden 1 functie = 1 taak
    # geen print statements in de functies
    # geen while True gebruiken
    # time sleep vermijden
    # Alles functioneel, dus liever geen waardes in de code

from machine import Pin, ADC
from hardwares2g import RGB, DOOR
import time

class StateMachine:
    def __init__(self):

        # Variables 
        self.AngleOpen = 0 
        self.AngleClosed = 90
        self.ferrometal_detected = False
        self.user_returned_from_mri = False
        
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
        self.Door2LockState = RGB(10, 11, 12)
        self.Door1LockState = RGB(2, 3, 4)
        self.FerroDetectLED = RGB(6, 7, 8)
        self.Door1 = DOOR(14, self.AngleClosed, self.AngleOpen)
        self.Door2 = DOOR(15, self.AngleClosed, self.AngleOpen)
        self.Pot1 = ADC(27)
        self.field_a = Pin(18, Pin.IN, Pin.PULL_UP)
        self.field_b = Pin(17, Pin.IN, Pin.PULL_UP)
        self.emergencybutton = Pin(5, Pin.IN, Pin.PULL_UP)
        self.emergencybutton.irq(trigger=Pin.IRQ_FALLING, handler=self.on_press_emergency_button)

    def delayed_print(self, message, delay):
        print(message)
        time.sleep(delay)

# State Functions
    def initialisation_state(self):
        self.Door1LockState.off() # Turn indicator off
        self.Door2LockState.off() # Turn indicator off
        self.FerroDetectLED.off() # Turn indicator off
        self.delayed_print("Initialisation state", 1)
        self.Door2._close_door() # _close_door DOOR 2
        self.Door2LockState.set_color("red") # DOOR Locked
        self.Door1._open_door() # _open_door DOOR 1
        self.Door1LockState.set_color("green")  # DOOR Unlocked
        return self.WAIT_FOR_USER_FIELD_A_STATE

    def user_field_a_response_state(self):
        self.delayed_print("Waiting for user field A state",1)
        if self.field_a.value() == 0 and self.field_b.value() == 1: 
            if self.user_returned_from_mri == False and self.ferrometal_detected == False:
                return self.LOCK_AND_CLOSE_DOOR1_STATE 
            elif self.user_returned_from_mri: 
                return self.UNLOCK_AND_OPEN_DOOR1_STATE
        else: 
            return self.WAIT_FOR_USER_FIELD_A_STATE

    def user_field_b_response_state(self):
        self.delayed_print("Waiting for user field B state",1)
        if self.field_a.value() == 1 and self.field_b.value() == 0:
            if self.user_returned_from_mri == False and self.ferrometal_detected == False:
                print("1")
                return self.FERROMETAL_DETECTION_STATE
            elif self.user_returned_from_mri == True and self.ferrometal_detected == True:
                print("2")
                return self.UNLOCK_AND_OPEN_DOOR2_STATE
            elif self.user_returned_from_mri == True:
                print("3")
                self.Door2._close_door()
                self.Door2LockState.set_color("red")
                return self.WAIT_FOR_USER_FIELD_A_STATE
        else:
            print("4")
            return self.WAIT_FOR_USER_FIELD_B_STATE

    def ferrometal_detection_state(self):
        self.delayed_print("Ferrometal detection state",1)
        pot_value = self.Pot1.read_u16()
        if 0 <= pot_value < 40000:
            self.FerroDetectLED.set_color("green")  # Green
            self.ferrometal_detected = True
            return self.UNLOCK_AND_OPEN_DOOR2_STATE
        elif 40000 <= pot_value <= 66000:
            self.ferrometal_detected = False
            self.FerroDetectLED.set_color("red")  # Red
            return self.UNLOCK_AND_OPEN_DOOR1_STATE

    def unlock_and_open_door1_state(self):
        self.delayed_print("Unlock and _open_door DOOR 1 state",1)
        self.Door1._open_door()
        self.Door1LockState.set_color("green") 
        self.user_returned_from_mri = False
        return self.WAIT_FOR_USER_FIELD_A_STATE

    def lock_and_close_door1_state(self):
        self.delayed_print("Lock and _close_door DOOR 1 state",1)
        self.Door1._close_door() # _close_door DOOR 1
        self.Door1LockState.set_color("red")  # Set the color to red
        return self.LOCK_AND_CLOSE_DOOR2_STATE

    def unlock_and_open_door2_state(self):
        self.delayed_print("Unlock and _open_door DOOR 2 state",1)
        self.Door2._open_door() # _open_door DOOR 2
        self.Door2LockState.set_color("green") # Set the color to green
        self.user_returned_from_mri = True
        return self.WAIT_FOR_USER_FIELD_B_STATE

    def lock_and_close_door2_state(self):
        self.delayed_print("Lock and _close_door DOOR 2 state",1)
        self.Door2._close_door() # _close_door DOOR 2 
        self.Door2LockState.set_color("red") # Set the color to red
        return self.WAIT_FOR_USER_FIELD_B_STATE

    def on_press_emergency_button(self):
        self.delayed_print("Emergency state",1)
        self.Door1._open_door() # _open_door DOOR 1
        self.Door2._open_door() # _open_door DOOR 2
        self.Door1LockState.set_color("blue")
        self.Door2LockState.set_color("blue")
        self.FerroDetectLED.set_color("blue")
        return self.EMERGENCY_STATE

    def user_returned_from_mri_state(self):
        self.user_returned_from_mri = True
        return 0
    
    def ferrometal_detected_state(self):
        self.ferrometal_detected = True
        return 0            

# state machine
    def run(self):
        state = self.initialisation_state()

        while True:
            if state == self.WAIT_FOR_USER_FIELD_A_STATE:
                state = self.user_field_a_response_state()

            elif state == self.WAIT_FOR_USER_FIELD_B_STATE:
                state = self.user_field_b_response_state()

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
                print("Emergency state triggerd")
                break  # Exit the loop

            else:
                print("Invalid state")
                break

if __name__ == "__main__":
    FDS = StateMachine()
    FDS.run()