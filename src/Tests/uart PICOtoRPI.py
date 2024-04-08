import serial

def receive_messages():
    ser = serial.Serial('/dev/ttyAMA10', baudrate=115200, timeout=1)  # Open serial port
    while True:
        if ser.in_waiting > 0:
            message = ser.readline().decode('utf-8').strip()  # Read the message from serial port
            print("Message received:", message )  # Print the received message
            if  message == "System initialised":
                print("yes recieved specific message")
if __name__ == "__main__":
    receive_messages()

