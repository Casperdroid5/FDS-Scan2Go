class ErrorHandler:
    def report_error(self, components):
        for component in components:
            self.display_error(component)
            # log error potential to a file or send it to a server

    def display_error(self, component):
        print(f"Error in component: {component}")

def check_sensors():
    # Check if sensors are connected and working
    _SensorFunctional = True  # for testing purposes this is set to...
    return _SensorFunctional

def check_motors():
    # Check if motors are connected and working
    _MotorFunctional = False  # for testing purposes this is set to...
    return _MotorFunctional

def check_leds():
    # Check if LEDs are connected and working
    _LedsFunctional = True  # for testing purposes this is set to...
    return _LedsFunctional

def check_buttons():
    # Check if buttons are connected and working
    _ButtonsFunctional = False  # for testing purposes this is set to...
    return _ButtonsFunctional

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
