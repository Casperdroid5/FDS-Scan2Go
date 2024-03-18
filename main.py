from machine import ADC, UART, Pin 
import uasyncio
from hardwares2g import RGB, DOOR
import time


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
        _POTENTIOMETER_POLLING_INTERVAL_MS: int = 1000 # interfal to check the scanner value
        
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
        if pot_value < 40000: # geen metaal
            self._on_metal_not_detected()
        else: # wel metaal
            self._on_metal_detected()

class MultiPersonDetector:
    def __init__(self, uart_configs, on_person_detected, on_person_not_detected):
        self._uart_sensors = []
        self._on_person_detected = on_person_detected
        self._on_person_not_detected = on_person_not_detected
        for uart_config in uart_configs:
            uart_number, baudrate, (tx_pin, rx_pin) = uart_config
            uart = UART(uart_number, baudrate=baudrate, tx=tx_pin, rx=rx_pin)
            self._uart_sensors.append(uart)
            task = uasyncio.create_task(self._receiver(uart))

    async def _receiver(self, uart):
        sreader = uasyncio.StreamReader(uart)
        while True:
            data = await sreader.readline()
            if data:
                # Check data from UART and call appropriate callbacks
                if b'\x02' in data:
                    self._on_person_detected(f"Sensor {self._uart_sensors.index(uart) + 1}: Somebody moved")
                elif b'\x01' in data:
                    self._on_person_detected(f"Sensor {self._uart_sensors.index(uart) + 1}: Somebody stopped moving")
                elif b'\x01' in data:
                    self._on_person_detected(f"Sensor {self._uart_sensors.index(uart) + 1}: Somebody is close")
                elif b'\x02' in data:
                    self._on_person_detected(f"Sensor {self._uart_sensors.index(uart) + 1}: Somebody is away")
                else:
                    self._on_person_not_detected(f"Sensor {self._uart_sensors.index(uart) + 1}: No human activity detected")

class SystemInitCheck:
    def __init__(self):
        print("System is starting up, running system check")
        self.systemcheck()
        if self.systemcheck() == True:
            print("System check passed, starting the system.")
            return None
        elif self.systemcheck() == False:
            print("System check failed")
            raise SystemError("System check NOT passed, system cannot start.")
        else:
            while True:
                print("System check is in progress")
                time.sleep(1) # sleep till system check is complete


    def systemcheck(self):
        # Check if all the hardware is connected and working
        # Check if the sensors are connected and working
        # Check if the motors are connected and working
        # Check if the LEDs are connected and working
        # Check if the buttons are connected and working
        # Check if the UARTs are connected and working
        # Check if the ADCs are connected and working
        # Check if the PWMs are connected and working
        # Check if the Servos are connected and working
        # Check if the system is ready to start
        systemcheck = True # everything is working
        
        if systemcheck == True:
            return True # everything is working
        else: 
            return False # something is not working

class ErrorHandler:
    def __init__(self):
        self._error = None

class StartUp(SystemInitCheck, ErrorHandler):
    def __init__(self):
        super().__init__()
        self._system_controller = SystemController()  # Initialize the system controller
        # Now, you can call the method to unlock the door
        self._system_controller._on_request_doorunlock(DoorNumber=1)

class ButtonHandler:
    def __init__(self, on_request_doorunlock: Callable) -> None:
        self._button = Pin(14, Pin.IN, Pin.PULL_UP)
        self._button.irq(trigger=Pin.IRQ_FALLING, handler=self._on_button_pressed)
        self._on_request_doorunlock = on_request_doorunlock

    def _on_button_pressed(self) -> None:
        self._on_request_doorunlock()  

class LedController:
    def __init__(self, ) -> None:
        self._RGB = RGB(2, 3, 4)

    def set_color(self, color) -> None:
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
        self._person_detector = MultiPersonDetector([(0, 115200, (0, 1)), (1, 115200, (4, 5))], self._on_person_detected, self._on_person_not_detected)
        self._button_handler = ButtonHandler(self._on_request_doorunlock)
        self._FerroDetectLED = RGB(6, 7, 8)
        self._Door2LockStateLED = RGB(10, 11, 12)
        self._Door1LockStateLED = RGB(2, 3, 6)
        self._door1_motor_controller = DOOR(14, 90, 0)
        self._door2_motor_controller = DOOR(15, 90, 0)

    def _on_metal_detected(self)  -> None:
        print("Metal detected right now.")
        self._FerroDetectLED.set_color("red")
        self._on_request_doorlock(DoorNumber=2)

    def _on_metal_not_detected(self)  -> None:
        print("Metal NOT detected right now.")
        self._FerroDetectLED.set_color("green")
        self._on_request_doorunlock(DoorNumber=2)

    def _on_person_detected(self, message: str) -> None:
        print("PersonDetector:", message)

    def _on_person_not_detected(self, message: str) -> None:
        print("PersonDetector:", message)

    def _on_request_doorunlock(self, DoorNumber) -> None:
        print("Door unlock request received for door", DoorNumber)
        if DoorNumber == 1:
            self._door1_motor_controller._open_door()
        elif DoorNumber == 2:
            self._door2_motor_controller._open_door()

    def _on_request_doorlock(self, DoorNumber) -> None:
        print("Door lock request received for door", DoorNumber)
        if DoorNumber == 1:
            self._door1_motor_controller._close_door()
        elif DoorNumber == 2:
            self._door2_motor_controller._close_door()


if __name__ == "__main__":
    SystemInitCheck()
    systemController = SystemController()
    # init complete now run the loop of uasyncio from now on
    uasyncio.get_event_loop().run_forever()
