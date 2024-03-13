from machine import ADC, UART, Pin
from typing import Callable
import uasyncio
import hardware_s2g

async def _PERIODIC(millisecond_interval: int, func, *args, **kwargs):
    """Run func every interval seconds.
    If func has not finished before *interval*, will run again
    immediately when the previous iteration finished.
    *args and **kwargs are passed as the arguments to func.
    """
    while True:
        await uasyncio.gather(
            func(*args, **kwargs),
            uasyncio.sleep_ms(millisecond_interval)
        )

class MetalDetectorController:
    def __init__(self, on_metal_detected: Callable) -> None:
        _POTENTIOMETER_PIN: int = 27
        _POTENTIOMETER_POLLING_INTERVAL_MS: int = 100
        
        self._pot = ADC(_POTENTIOMETER_PIN)
        self._on_metal_detected = on_metal_detected
        self._task_check_pot = uasyncio.create_task(
            _PERIODIC(_POTENTIOMETER_POLLING_INTERVAL_MS, self._check_pot)
        )

    def __del__(self) -> None:
        self._task_check_pot.cancel()
    
    async def _check_pot(self) -> None:
        pot_value = self._pot.read_u16()
        if pot_value < 40000:
            # geen metaal
            pass
        else:
            # wel metaal
            self._on_metal_detected()

class PersonDetector:
    def __init__(self, on_person_detected: Callable) -> None:
        self._uart = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
        self._on_person_detected = on_person_detected
        self._task_receiver = uasyncio.create_task(
            self._receiver()
        )

    async def _receiver(self):
        sreader = uasyncio.Stream(self._uart)
        while True:
            data = await sreader.readline()
            print(data)
            if data == b"Person detected\n":
                self._on_person_detected()

class ButtonHandler:
    def __init__(self, on_request_doorunlock: Callable) -> None:
        self._button = Pin(14, Pin.IN, Pin.PULL_UP)
        self._button.irq(trigger=Pin.IRQ_FALLING, handler=self._on_button_pressed)
        self._on_request_doorunlock = on_request_doorunlock

    def _on_button_pressed(self, pin) -> None:
        self._on_request_doorunlock()    

class LedController:
    def __init__(self) -> None:
        self._rgb = hardware_s2g.rgb(2, 3, 4)

    async def _SetColor(self, color) -> None:
        # Set the color of the LED
        self._rgb.Setcolor(color)

class DoorMotorController:
    def __init__(self) -> None:
        self._door = hardware_s2g.Door(26, 0, 90)  
        self._task_close = None

    async def OpenDoor(self) -> None:
        self._door.Open()  # Open the door
        await uasyncio.sleep_ms(1000)  # Assuming it takes 1 seconds to open the door

    async def CloseDoor(self) -> None:
        self._door.Close()
        await uasyncio.sleep_ms(1000)  # Assuming it takes 1 seconds to close the door

class SystemController:
    def __init__(self) -> None:
        self._metal_detector_controller = MetalDetectorController(self._on_metal_detected)
        self._person_detector = PersonDetector(self._on_person_detected)
        self._button_handler = ButtonHandler(self._on_request_doorunlock)
        self._led_controller = LedController()
        self._door_motor_controller = DoorMotorController()

    def _on_metal_detected(self) -> None:
        print("Metal detected right now.")
        
    def _on_person_detected(self) -> None:
        print("Person detected right now.")

    def _on_request_doorunlock(self) -> None:
        print("Door unlock request received.")

if __name__ == "__main__":
    systemController = SystemController()
    uasyncio.get_event_loop().run_forever()
