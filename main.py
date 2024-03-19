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

class SystemInitCheck:
    def __init__(self):
        print("System is starting up, running system check")
        failing_components = self.systemcheck()
        if failing_components:
            print("failed system check, reporting error(s):")
            ErrorHandler().report_error(failing_components)
            print("System check failed, exiting.")
            raise SystemExit
        else:
            print("System check passed, continuing with startup.")

    def systemcheck(self):
        failing_components = [] # List to store failing components
        # Check sensors
        if not check_sensors():
            failing_components.append("Sensors")

        # Check motors
        if not check_motors():
            failing_components.append("Motors")

        # Check LEDs
        if not check_leds():
            failing_components.append("LEDs")

        # Check buttons
        if not check_buttons():
            failing_components.append("Buttons")

        return failing_components # Return the list of failing components

def check_sensors():
    # Check if sensors are connected and working
    _SensorFunctional = True  # for testing purposes this is set to...
    return _SensorFunctional

def check_motors():
    # Check if motors are connected and working
    _MotorFunctional = True  # for testing purposes this is set to...
    return _MotorFunctional

def check_leds():
    # Check if LEDs are connected and working
    _LedsFunctional = True  # for testing purposes this is set to...
    return _LedsFunctional

def check_buttons():
    # Check if buttons are connected and working
    _ButtonsFunctional = True  # for testing purposes this is set to...
    return _ButtonsFunctional

class ErrorHandler:
    def report_error(self, components):
        for component in components:
            self.display_error(component)
            # log error potentioal to a file or send it to a server

    def display_error(self, component):
        print(f"Error in component: {component}")

class StartUp():
    def __init__(self):
        super().__init__()
        self._system_controller = SystemController()  # Initialize the system controller
        self._system_controller._door2_motor_controller._close_door()  # Close door 2
        self._system_controller._door1_motor_controller._open_door()  # Open door 1
        # close door 1 etcetera, starting state?

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
    StartUp()
    # startup complete now run the loop of uasyncio from now on
    uasyncio.get_event_loop().run_forever()