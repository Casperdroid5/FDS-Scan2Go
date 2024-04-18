import serial
import os

def show_image(image_path):
    if os.path.exists(image_path):
        print(f"Opening image: {image_path}")
        os.system(f"feh {image_path} &")  # Open the image using feh
    else:
        print("Image file not found:", image_path)

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
            
            # Clear the serial buffer
            s.reset_input_buffer()

            # Check if the received message is for showing an image
            if received_message.startswith("[USBCommunication] showimage"):
                print("Showing image")
                # Extract the image number from the message
                image_number = received_message.split(" ")[-1]
                # Construct the image file path
                image_path = f"{image_number}.png"
                # Show the image
                show_image(image_path)
            elif received_message == "[USBCommunication] closeimage":
                print(received_message)
                # Close the image
                close_image()
                print("Closed the image")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
