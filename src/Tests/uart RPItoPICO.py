import serial
import time

def receive_uart(port):
    ser = serial.Serial(port, baudrate=115200, timeout=1)  
    message = ser.readline().decode('utf-8').strip()  
    print("Message received:", message)  
    ser.close()  # Sluit de seriële poort nadat de boodschap is ontvangen
    return message

def send_uart(port):
    ser = serial.Serial(port, baudrate=115200, timeout=1)  
    print("I think I am awake, sending reply")
    ser.write(b"1")  
    ser.close()  # Sluit de seriële poort nadat het bericht is verzonden

if __name__ == "__main__":
    received_message = receive_uart('COM8')  # Verander 'COM8' naar de juiste poort voor de Raspberry Pi Pico
    send_uart('COM8')  # Verander 'COM8' naar de juiste poort voor de Raspberry Pi Pico