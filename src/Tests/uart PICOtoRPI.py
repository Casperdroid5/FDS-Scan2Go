from UARTCommunication import UARTCommunication    
import time

if __name__ == "__main__":
    
    # Initialisatie van UART-communicatie
    RPI5_uart_line = UARTCommunication(uart_number=0, baudrate=115200, tx_pin=12, rx_pin=13)


while True:
    RPI5_uart_line.send_message("\nRPI, you awake?")
    RPI5_uart_line.receive_message()
    time.sleep(0.6)
