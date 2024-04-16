
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

def check_mmWave():
    # Check if mmWave sensors are connected and working
    _mmWaveFunctional = True  # for testing purposes this is set to...
    return _mmWaveFunctional

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

        return failing_components # Return the list of failing components
