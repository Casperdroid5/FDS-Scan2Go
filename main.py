from machine import ADC, UART, Pin, PWM
import uasyncio
from hardwares2g import RGB, DOOR


        
async def _PERIODIC(millisecond_interval: int, func, *args, **kwargs):
    """Run func every interval seconds.
    If func has not finished before *interval*, will run again
    immediately when the previous iteration finished.
    *args and **kwargs are passed as the arguments to func.
    """
    try:
        while True:
            uasyncio.create_task(
                func(*args, **kwargs)
            )
            await uasyncio.sleep_ms(millisecond_interval)
    except uasyncio.CancelledError:
        print("_PERIODIC cancellled.")

class MetalDetectorController:
    def __init__(self, on_metal_detected: Callable, on_metal_not_detected: Callable) -> None:
        _POTENTIOMETER_PIN: int = 27
        _POTENTIOMETER_POLLING_INTERVAL_MS: int = 1000
        
        self._pot = ADC(_POTENTIOMETER_PIN)
        self._on_metal_detected = on_metal_detected
        self._on_metal_not_detected = on_metal_not_detected
        self._task_check_pot = uasyncio.create_task(
            _PERIODIC(_POTENTIOMETER_POLLING_INTERVAL_MS, self._check_pot)
        )
        

    def __del__(self) -> None:
        self._task_check_pot.cancel()

    async def _check_pot(self) -> None:
        pot_value = self._pot.read_u16()
        if pot_value < 40000:
            # geen metaal
            self._on_metal_not_detected()
        else:
            # wel metaal
            self._on_metal_detected()

class PersonDetector:
    def __init__(self, on_person_detected, on_person_not_detected):
        self._uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
        self._on_person_detected = on_person_detected
        self._on_person_not_detected = on_person_not_detected
        self._task_receiver = uasyncio.create_task(self._receiver())

    async def _receiver(self):
        sreader = uasyncio.StreamReader(self._uart)
        while True:
            data = await sreader.readline()
            if data:
                # Check if somebody moved
                if b'\x02' in data:
                    self._on_person_detected("Somebody moved")
                # Check if somebody stopped moving
                elif b'\x01' in data:
                    self._on_person_detected("Somebody stopped moving")
                # Check if somebody is close
                elif b'\x01' in data:
                    self._on_person_detected("Somebody is close")
                # Check if somebody is away
                elif b'\x02' in data:
                    self._on_person_detected("Somebody is away")
                else:
                    self._on_person_not_detected("No human activity detected")

class ButtonHandler:
    def __init__(self, on_request_doorunlock: Callable) -> None:
        self._button = Pin(14, Pin.IN, Pin.PULL_UP)
        self._button.irq(trigger=Pin.IRQ_FALLING, handler=self._on_button_pressed)
        self._on_request_doorunlock = on_request_doorunlock

    def _on_button_pressed(self, pin) -> None:
        self._on_request_doorunlock()  

class LedController:
    def __init__(self, ) -> None:
        self._RGB = RGB(2, 3, 4)

    def set_color(self, color) -> None:
        # Set the color of the LED
        print(color)
        self._RGB.set_color(color)
        

class DoorMotorController:
    def __init__(self) -> None:
        self._door = DOOR(26, 0, 90)  
        self._task_close = None

    async def _open_door(self) -> None:
        self._door._open_door()  # Open the door
        await uasyncio.sleep_ms(1000)  # Assuming it takes 1 seconds to open the door

    async def _close_door(self) -> None:
        self._door._close_door()
        await uasyncio.sleep_ms(1000)  # Assuming it takes 1 seconds to close the door

class SystemController:
    def __init__(self) -> None:
        self._metal_detector_controller = MetalDetectorController(self._on_metal_detected, self._on_metal_not_detected)
        self._person_detector = PersonDetector(self._on_person_detected, self._on_person_not_detected)
        self._button_handler = ButtonHandler(self._on_request_doorunlock)
        self._FerroDetectLED = RGB(6, 7, 8)
        self._door1_motor_controller = DOOR(14, 90, 0)
        self._door2_motor_controller = DOOR(15, 90, 0)


    def _on_metal_detected(self)  -> None:
        print("Metal detected right now.")
        self._FerroDetectLED.set_color("red")
        self._door2_motor_controller._close_door()

    def _on_metal_not_detected(self)  -> None:
        print("Metal NOT detected right now.")
        self._FerroDetectLED.set_color("green")
        self._door2_motor_controller._open_door()
        
        
    def _on_person_detected(self, message: str) -> None:
        print("PersonDetector:", message)

    def _on_person_not_detected(self, message: str) -> None:
        print("PersonDetector:", message)

    def _on_request_doorunlock(self) -> None:
        print("Door unlock request received.")

        

if __name__ == "__main__":
    systemController = SystemController()
    # init complete now run the loop of uasyncio from now on
    uasyncio.get_event_loop().run_forever()


#vragen: hoe en waar declareer ik mijn componenten pinnen enzo? 
# wat doet self nou eigenlijk en hoe zie ik waar wat wordt meegegeven makkelijk? ik ben dat overzicht kwijt
# Hoe maak ik dit systeem deterministisch? Zouden er niet een soort states moeten zijn? hoe laat ik anders het systeem verlopen volgens protocol?
