#Todo:
    # altijd iets returnen bij een functie
    # functies zo klein mogelijk houden 1 functie = 1 taak
    # geen print statements in de functies
    # geen while True gebruiken
    # time sleep vermijden
    # Alles functioneel, dus liever geen waardes in de code

from machine import Pin, ADC
from hardware_s2g import rgb, Door
import time

class StateMachine:
    def __init__(self):

        # Variables 
        self.AngleOpen = 0 
        self.AngleClosed = 90
        self.ferro_free = False
        self.patient_returned_from_mri = False
        
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
        self.Door2LockState = rgb(10, 11, 12)
        self.Door1LockState = rgb(2, 3, 4)
        self.FerroDetectLED = rgb(6, 7, 8)
        self.Door1 = Door(14, self.AngleClosed, self.AngleOpen)
        self.Door2 = Door(15, self.AngleClosed, self.AngleOpen)
        self.Pot1 = ADC(27)
        self.field_a = Pin(18, Pin.IN, Pin.PULL_UP)
        self.field_b = Pin(17, Pin.IN, Pin.PULL_UP)
    
    def delayed_print(self, message, delay):
        print(message)
        time.sleep(delay)
            
# State Functions
    def initialisation_state(self):
        self.Door1LockState.Off() # Turn indicator off
        self.Door2LockState.Off() # Turn indicator off
        self.FerroDetectLED.Off() # Turn indicator off
        self.delayed_print("Initialisation state", 1)
        self.Door2.Close() # Close Door 2
        self.Door2LockState.Setcolor("red") # Door Locked
        self.Door1.Open() # Open Door 1
        self.Door1LockState.Setcolor("green")  # Door Unlocked
        return self.WAIT_FOR_USER_FIELD_A_STATE

    def wait_for_user_field_a_state(self):
        self.delayed_print("Waiting for user field A state",1)
        if self.field_a.value() == 0 and self.field_b.value() == 1: 
            if self.patient_returned_from_mri == False and self.ferro_free == False:
                return self.LOCK_AND_CLOSE_DOOR1_STATE 
            elif self.patient_returned_from_mri: 
                return self.UNLOCK_AND_OPEN_DOOR1_STATE
        else: 
            return self.WAIT_FOR_USER_FIELD_A_STATE

    def wait_for_user_field_b_state(self):
        self.delayed_print("Waiting for user field B state",1)
        if self.field_a.value() == 1 and self.field_b.value() == 0:
            if self.patient_returned_from_mri == False and self.ferro_free == False:
                print("1")
                return self.UNLOCK_AND_OPEN_DOOR2_STATE
            elif self.patient_returned_from_mri == True:
                print("2")
                self.Door2.Close()
                self.Door2LockState.Setcolor("red")
                return self.WAIT_FOR_USER_FIELD_A_STATE
        else:
            print("3")
            return self.WAIT_FOR_USER_FIELD_B_STATE

    def ferrometal_detection_state(self):
        self.delayed_print("Ferrometal detection state",1)
        pot_value = self.Pot1.read_u16()
        if 0 <= pot_value < 40000:
            self.FerroDetectLED.Setcolor("green")  # Green
            self.ferro_free = True
            return self.UNLOCK_AND_OPEN_DOOR2_STATE
        elif 40000 <= pot_value <= 66000:
            self.ferro_free = False
            self.FerroDetectLED.Setcolor("red")  # Red
            return self.UNLOCK_AND_OPEN_DOOR1_STATE

    def unlock_and_open_door1_state(self):
        self.delayed_print("Unlock and open door 1 state",1)
        self.Door1.Open()
        self.Door1LockState.Setcolor("green") 
        self.patient_returned_from_mri = False
        return self.WAIT_FOR_USER_FIELD_A_STATE

    def lock_and_close_door1_state(self):
        self.delayed_print("Lock and close door 1 state",1)
        self.Door1.Close() # Close Door 1
        self.Door1LockState.Setcolor("red")  # Set the color to red
        return self.LOCK_AND_CLOSE_DOOR2_STATE

    def unlock_and_open_door2_state(self):
        self.delayed_print("Unlock and open door 2 state",1)
        self.Door2.Open() # Open Door 2
        self.Door2LockState.Setcolor("green") # Set the color to green
        self.patient_returned_from_mri = True
        return self.WAIT_FOR_USER_FIELD_B_STATE

    def lock_and_close_door2_state(self):
        self.delayed_print("Lock and close door 2 state",1)
        self.Door2.Close() # Close Door 2 
        self.Door2LockState.Setcolor("red")
        if self.patient_returned_from_mri:
            self.patient_returned_from_mri = False
            self.ferro_free = False
            return self.UNLOCK_AND_OPEN_DOOR1_STATE
        else:
            return self.WAIT_FOR_USER_FIELD_B_STATE

    def emergency_state(self):
        self.delayed_print("Emergency state",1)
        self.Door1.Open() # Open Door 1
        self.Door2.Open() # Open Door 2
        self.Door1LockState.Setcolor("blue")
        self.Door2LockState.Setcolor("blue")
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
                break

if __name__ == "__main__":
    FDS = StateMachine()
    FDS.run()