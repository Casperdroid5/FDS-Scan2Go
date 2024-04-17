import serial

def main():
    # Open de seriele poort
    s = serial.Serial(port="/dev/ttyACM0", baudrate=115200, timeout=1) 

    while True:
        # Typ een bericht om te verzenden
        message = input("Typ een bericht om naar de Raspberry Pi Pico te sturen: ")
        
        # Stuur het bericht naar de Raspberry Pi Pico
        s.write(message.encode() + b'\r')

        # Wacht op het antwoord van de Pico
        response = s.readline().strip().decode()
        print("Antwoord van de Pico:", response)

if __name__ == "__main__":
    main()

