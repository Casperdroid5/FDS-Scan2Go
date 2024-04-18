import serial
import os

def show_image(image_path):
    if os.path.exists(image_path):
        print(f"Opening image fullscreen: {image_path}")
        os.system(f"feh -F {image_path} &")  # Open de afbeelding fullscreen met feh
    else:
        print("Afbeeldingsbestand niet gevonden:", image_path)

def close_image():
    os.system("pkill feh")  # Close all instances of feh

def main():
    # Open the serial port
    s = serial.Serial(port="/dev/ttyACM0", baudrate=115200, timeout=1) 

    try:
        while True:
            # Read a message from the serial port
            received_message = s.readline().decode().strip()
            print(received_message)
            
            # Clear serial buffer
            s.reset_input_buffer()

            # Check if the received message is for showing an image
            if received_message.startswith("[USBCommunication] showimage"):
                # Extract the image number from the message
                image_number = received_message.split(" ")[-1]
                # Construct the image file path
                image_path = f"{image_number}.png"
                # Show the image
                show_image(image_path)
            elif received_message == "[USBCommunication] closeimage":
                # Close the image
                close_image()
                print("Closed the image")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
