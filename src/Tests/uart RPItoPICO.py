import serial
import time

def send_recieve():
    ser = serial.Serial('/dev/ttyAMA10', baudrate=115200, timeout=1)  # Open serial port

    while True:

        message = ser.readline().decode('utf-8').strip()  # Read the message from serial port
        print("Message received:", message)  # Print the received message
        if message == "RPI, you awake?":
            print("I think I am awake, sending reply")
            ser.write("yes".encode('utf-8'))  # Write back to the serial port
            time.sleep(1)

if __name__ == "__main__":
    send_recieve()

