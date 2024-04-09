import serial
import time

def recieve_uart():
    ser = serial.Serial('COM3', baudrate=115200, timeout=1)  # Open serial port, check if this works    
    message = ser.readline().decode('utf-8').strip()  # Read the message from serial port
    print("Message received:", message)  # Print the received message
    return message

def sent_uart():
    ser = serial.Serial('COM3', baudrate=115200, timeout=1)  # Open serial port, check if this works
    print("I think I am awake, sending reply")
    ser.write(b"1")  # Write back to the serial port


if __name__ == "__main__":
    recieve_uart()
    if recieve_uart.message == b"1":
        sent_uart()

