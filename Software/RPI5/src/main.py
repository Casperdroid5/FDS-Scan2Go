import serial
import os
import subprocess
import time
from gpiozero import LED
from signal import pause

# Paths for audio and image files. Change path to use different location. Comment out to use current folder.
audio_path = "/home/ADMIN/FDS-Scan2Go/Software/FDS_media/Soundfiles_FDS/"  # change to the path of the audio files
image_path = "/home/ADMIN/FDS-Scan2Go/Software/FDS_media/Displayimages_FDS/"  # change to the path of the image files

# Variable to keep track of the current audio process
current_audio_process = None

# Reset pin for Pico
PicoResetSignal = LED(23)


def play_audio(audio_path):
    global current_audio_process

    if os.path.exists(audio_path):
        print(f"Playing audio: {audio_path}")
        # Stop the current audio process if there is one
        if current_audio_process:
            current_audio_process.terminate()
            current_audio_process.wait()
        
        # Start the new audio process with VLC in the background
        current_audio_process = subprocess.Popen(["cvlc", audio_path])
    else:
        print("Audio file not found:", audio_path)

def stop_audio():
    global current_audio_process

    # Stop the current audio process if there is one
    if current_audio_process:
        current_audio_process.terminate()
        current_audio_process.wait()
        current_audio_process = None

def show_image(image_path):
    if os.path.exists(image_path):
        print(f"Opening image: {image_path}")
        os.system(f"feh -ZF {image_path} &")  # Open the image using feh
    else:
        print("Image file not found:", image_path)

def close_image():
    os.system("pkill feh")  # Close all instances of feh

def connect_serial(port="/dev/ttyACM0", baudrate=115200, timeout=1):
    attempt = 0
    second_attempt = False
    
    while True:
        try:
            return serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        except serial.SerialException as e:
            print(f"Failed to connect to {port}: {e}. Retrying in 1.5 seconds...")
            time.sleep(1.5)
            attempt += 1
            if attempt >= 3 and second_attempt == False:
                print("Failed to connect after 3 attempts. Forcefully rebooting Rasperberry Pi Pico")
                PicoResetSignal.off()
                time.sleep(0.5)
                PicoResetSignal.on()
                attempt = 0  
                second_attempt = True 
            if attempt >= 3 and second_attempt:
                print("Failed to connect for the second time. Raising alarms")
                time.sleep(0.5)
                # Do something here to raise alarms or notify the user	
                exit(1) # terminate the program

def send_message(serial, message):
    try:
        serial.write((message + "\n").encode())
    except serial.SerialException as e:
        print(f"Failed to send message: {e}")

def main():
    global image_path
    dataline = connect_serial()

    try:
        while True:
            try:
                # Read a message from the serial port
                received_message = dataline.readline().decode().strip()
                print(received_message)
                if received_message.startswith("[USBCommunication] stillalive"):
                    send_message(dataline, "[USBCommunication] stillalive".encode())        

                if received_message.startswith("[USBCommunication] playaudio"):
                    # Extract the audio file number from the message
                    audio_number = received_message.split(" ")[-1]
                    # Construct the audio file path
                    audio_file = f"{audio_number}.m4a"
                    # Play the audio
                    play_audio(os.path.join(audio_path, audio_file))
                elif received_message == "[USBCommunication] stopaudio":
                    # Stop the audio
                    stop_audio()
                    print("Stopped audio playback")
                # Check if the received message is for showing an image
                elif received_message.startswith("[USBCommunication] showimage"):
                    print("Showing image")
                    # Extract the image number from the message
                    image_number = received_message.split(" ")[-1]
                    # Construct the image file path
                    image_file = f"{image_number}.png"
                    # Show the image
                    show_image(os.path.join(image_path, image_file))
                elif received_message == "[USBCommunication] closeimage":
                    print(received_message)
                    # Close the image
                    close_image()
                    print("Closed the image")
            except serial.SerialException as e:
                print(f"Serial error: {e}")
                dataline.close()
                dataline = connect_serial()
    except Exception as e:
        print(f"An error occurred: {e}")
        if dataline.is_open:
            dataline.close()

if __name__ == "__main__":
    main()


