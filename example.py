
import machine
from machine import ADC, UART, Pin, PWM
import uasyncio


async def _PERIODIC(millisecond_interval: int, func, *args, **kwargs):
    """Run func every interval seconds.

    If func has not finished before *interval*, will run again
    immediately when the previous iteration finished.

    *args and **kwargs are passed as the arguments to func.
    """
    while True:
        func(*args, **kwargs)
        await uasyncio.sleep_ms(millisecond_interval)
        
        # await uasyncio.gather(
        #     func(*args, **kwargs),
        #     uasyncio.sleep_ms(millisecond_interval)    
        # )

class MetalDetectorController:
    def __init__(self, on_metal_detected: Callable) -> None:
        _POTENTIOMETER_PIN: int = 27
        _POTENTIOMETER_POLLING_INTERVAL_MS: int = 100
        
        self._pot = ADC(_POTENTIOMETER_PIN)
        self._on_metal_detected = on_metal_detected
        self._task_check_pot = uasyncio.create_task( # Maybe this won't work. If it doesn't, try using uasyncio.get_running_loop().create_task(...) instead
            _PERIODIC(_POTENTIOMETER_POLLING_INTERVAL_MS, self._check_pot)
        )
    
    def __del__(self) -> None:
        self._task_check_pot.cancel()
    
    def _check_pot(self) -> None:
        pot_value = self._pot.read_u16()
        print("check_potmeter: ")
        print(pot_value)
        if pot_value < 40000:
            
            # geen metaal
            pass
        else:
            # wel metaal
            self._on_metal_detected()

class PersonDetector:
    def __init__(self, on_person_detected: Callable) -> None:
        self._uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
        self._on_person_detected = on_person_detected
        self._task_receiver = uasyncio.create_task(
            self._receiver()
        )

    async def _receiver(self):
        sreader = uasyncio.StreamReader(self._uart)
        while True:
            print("await sreader.readline()")
            data = await sreader.readline() # wacht tot heel bericht binnen is gekomen zonder blokken
            print(data)
            print("recieved some data from uart stream:")	
            if data == b"1\r\n": # als er een persoon is gedetecteerd volgens de sensor uart stream data
                print("Person detected")
                self._on_person_detected()



class SystemController:
    def __init__(self) -> None:
        # self._metal_detector_controller = MetalDetectorController(self._on_metal_detected)
        self._person_detector = PersonDetector(self._on_person_detected)
    
    # def _on_metal_detected(self) -> None:
    #     print("Metal detected right now.")
        
    def _on_person_detected(self) -> None:
        print("Person detected right now.")

        
if __name__ == "__main__":
    systemController = SystemController()
    uasyncio.get_event_loop().run_forever()