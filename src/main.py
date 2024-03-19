
import logging
from machine import Pin, ADC
from hardwares2g import RGB, DOOR

class StateMachine:
    def __init__(self):
        # Logger initialiseren
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Variabelen
        self.AngleOpen = 0 
        self.AngleClosed = 90
        self.ferrometal_detected = False
        self.user_returned_from_mri = False
        self.EmergencyState = False
        
        # Definieer gehele getallen constanten voor de toestanden
        self.INITIALISATION_STATE = 0
        self.WAIT_FOR_USER_FIELD_A_STATE = 1
        self.WAIT_FOR_USER_FIELD_B_STATE = 2
        self.FERROMETAL_DETECTION_STATE = 3
        self.UNLOCK_AND_OPEN_DOOR1_STATE = 4
        self.LOCK_AND_CLOSE_DOOR1_STATE = 5
        self.UNLOCK_AND_OPEN_DOOR2_STATE = 6
        self.LOCK_AND_CLOSE_DOOR2_STATE = 7
        self.EMERGENCY_STATE = 8

        # Hardwarecomponenten initialiseren
        self.Door2LockState = RGB(10, 11, 12)
        self.Door1LockState = RGB(2, 3, 4)
        self.FerroDetectLED = RGB(6, 7, 8)
        self.Door1 = DOOR(14, self.AngleClosed, self.AngleOpen)
        self.Door2 = DOOR(15, self.AngleClosed, self.AngleOpen)
        self.Pot1 = ADC(27)
        self.field_a = Pin(18, Pin.IN, Pin.PULL_UP)
        self.field_b = Pin(17, Pin.IN, Pin.PULL_UP)
        
        self.emergencybutton = Pin(9, Pin.IN, Pin.PULL_UP)
        self.emergencybutton.irq(trigger=Pin.IRQ_FALLING, handler=self.on_press_emergency_button)

    # Functies voor de toestanden
    def initialisation_state(self):
        self.user_returned_from_mri = False
        self.ferrometal_detected = False
        self.Door1LockState.off()
        self.Door2LockState.off()
        self.FerroDetectLED.off()
        self.logger.info("Initialisation state")
        self.Door2._close_door()
        self.Door2LockState.set_color("red")
        self.Door1._open_door()
        self.Door1LockState.set_color("green")
        return self.WAIT_FOR_USER_FIELD_A_STATE

    def user_field_a_response_state(self):
        print("Waiting for user field A state")
        if self.field_a.value() == True and self.field_b.value() == False: 
            if self.user_returned_from_mri == False and self.ferrometal_detected == False:
                return self.LOCK_AND_CLOSE_DOOR1_STATE 
            elif self.user_returned_from_mri: 
                return self.UNLOCK_AND_OPEN_DOOR1_STATE
        else: 
            return self.WAIT_FOR_USER_FIELD_A_STATE

    def user_field_b_response_state(self):
        print("Waiting for user field B state")
        if self.field_a.value() == False and self.field_b.value() == True:
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
            return self.WAIT_FOR_USER_FIELD_B_STATE

    def ferrometal_detection_state(self):
        print("Ferrometal detection state")
        pot_value = self.Pot1.read_u16()
        if 0 <= pot_value < 40000:
            self.FerroDetectLED.set_color("green")  # Green
            self.ferrometal_detected = False
            return self.UNLOCK_AND_OPEN_DOOR2_STATE
        elif 40000 <= pot_value <= 66000:
            self.ferrometal_detected = True
            self.FerroDetectLED.set_color("red")  # Red
            return self.UNLOCK_AND_OPEN_DOOR1_STATE

    def unlock_and_open_door1_state(self):
        print("Unlock and _open_door DOOR 1 state")
        self.Door1._open_door()
        self.Door1LockState.set_color("green") 
        return self.INITIALISATION_STATE

    def lock_and_close_door1_state(self):
        print("Lock and _close_door DOOR 1 state")
        self.Door1._close_door() # _close_door DOOR 1
        self.Door1LockState.set_color("red")  # Set the color to red
        return self.LOCK_AND_CLOSE_DOOR2_STATE

    def unlock_and_open_door2_state(self):
        print("Unlock and _open_door DOOR 2 state")
        self.Door2._open_door() # _open_door DOOR 2
        self.Door2LockState.set_color("green") # Set the color to green
        self.user_returned_from_mri = True
        return self.WAIT_FOR_USER_FIELD_B_STATE

    def lock_and_close_door2_state(self):
        print("Lock and _close_door DOOR 2 state")
        self.Door2._close_door() # _close_door DOOR 2 
        self.Door2LockState.set_color("red") # Set the color to red
        return self.WAIT_FOR_USER_FIELD_B_STATE

    def on_press_emergency_button(self, pin):
        self.logger.info("Emergency state")
        self.Door1LockState.set_color("blue")
        self.Door2LockState.set_color("blue")
        self.FerroDetectLED.set_color("blue")
        self.Door1._open_door()
        self.Door2._open_door()
        self.EmergencyState = True
        return self.EmergencyState

    # State machine uitvoeren
    def run(self):
        state = self.initialisation_state()

        while True:
            if self.EmergencyState:
                self.logger.info("Emergency state triggered, stopping state machine")
                break

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

            else:
                self.logger.error("Invalid state")
                break

if __name__ == "__main__":
    FDS = StateMachine()
    FDS.run()