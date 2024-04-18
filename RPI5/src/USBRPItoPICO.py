import serial

def main():
    # Open de seriele poort
    s = serial.Serial(port="/dev/ttyACM0", baudrate=115200, timeout=1) 

    while True:
        # Lees een bericht van de seriele poort
        received_message = s.readline().decode().strip()

        # Controleer of het bericht afkomstig is van UARTCommunication
        if received_message.startswith("[UARTCommunication]"):
            # Verwijder de prefix en print het bericht
            message = received_message[len("[UARTCommunication] "):]
            print("Ontvangen bericht:", message)

        # Typ een bericht om te verzenden
        message_to_send = input("Typ een bericht om naar de UARTCommunication te sturen: ")
        
        # Stuur het bericht naar de Raspberry Pi Pico
        s.write(("[UARTCommunication] " + message_to_send + "\r").encode())

if __name__ == "__main__":
    main()
