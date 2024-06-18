import serial
import os
import subprocess
import time
from gpiozero import LED
from signal import pause

# Paths for audio and image files. Change path to use different location.
audio_path = "/home/ADMIN/FDS-Scan2Go/Software/FDS_media/Soundfiles_FDS/"  # change to the path of the audio files
image_path = "/home/ADMIN/FDS-Scan2Go/Software/FDS_media/Displayimages_FDS/"  # change to the path of the image files

# Variable to keep track of the current audio process
current_audio_process = None

# Reset pin for Pico
PicoResetSignal = LED(23) 

# Reboot Pico on startup program
PicoResetSignal.off()
time.sleep(0.5)
PicoResetSignal.on()

def play_audio(audio_path):
    global current_audio_process

    if os.path.exists(audio_path):
        print(f"Playing audio: {audio_path}")
        if current_audio_process: # Stop the current audio process if there is one
            current_audio_process.terminate()
            current_audio_process.wait()
        current_audio_process = subprocess.Popen(["cvlc", audio_path]) # Start the new audio process with VLC in the background
    else:
        print("Audio file not found:", audio_path)

def stop_audio():
    global current_audio_process
    if current_audio_process:     # Stop the current audio process if there is one
        current_audio_process.terminate()
        current_audio_process.wait()
        current_audio_process = None

def show_image(image_path):
    if os.path.exists(image_path):
        print(f"Opening image: {image_path}")
        os.system(f"feh -ZF {image_path} &")  # Open the image in full screen and zoomed in using feh (image viewer)
    else:
        print("Image file not found:", image_path)

def close_image():
    os.system("pkill feh")  # Close all images opened by feh

def connect_serial(port="/dev/ttyACM0", baudrate=115200, timeout=1): # Default port is /dev/ttyACM0 for RPI Pico, change if necessary
    attempt = 0
    second_attempt = False
    
    while True:
        try: # Try to connect to the serial port
            return serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        except serial.SerialException as e:
            print(f"Failed to connect to {port}: {e}. Retrying in 1.5 seconds...")
            time.sleep(1.5)
            attempt += 1
            if attempt >= 3 and second_attempt == False:
                print("Failed to connect after 3 attempts. Forcefully rebooting Raspberry Pi Pico")
                PicoResetSignal.off()
                time.sleep(0.5)
                PicoResetSignal.on()
                attempt = 0  
                second_attempt = True 
            if attempt >= 3 and second_attempt:
                print("Failed to connect for the second time. Raising alarms")
                # TODO: Do something here to raise alarms or notify the user	
                # TODO: showimage("error.png") # Show an error image to the user
                exit(1) # terminate the program

def send_message(serial, message): # Send a message to the serial port (RPI Pico)
    try:
        serial.write((message + "\n").encode())
        print(f"Sent message: {message}")
    except serial.SerialException as e:
        print(f"Failed to send message: {e}")

def main():
    global image_path
    dataline = connect_serial()

    try:
        while True:
            try:
                received_message = dataline.readline().decode().strip() # Read a message from the serial port (comming from RPI Pico)
                print(received_message) # Print the received message to the console

                if received_message.startswith("[USBCommunication] stillalivemessage"):
                    send_message(dataline, "[USBCommunication] stillalive")

                if received_message.startswith("[USBCommunication] playaudio"): # Check if the received message is for playing audio
                    audio_number = received_message.split(" ")[-1] # Extract the audio file number from the message
                    audio_file = f"{audio_number}.m4a" # Construct the audio file path
                    play_audio(os.path.join(audio_path, audio_file)) # Play the audio

                elif received_message == "[USBCommunication] stopaudio":
                    stop_audio() # Stop the audio
                    print("Stopped audio playback")

                elif received_message.startswith("[USBCommunication] showimage"): # Check if the received message is for showing an image
                    print("Showing image")
                    image_number = received_message.split(" ")[-1] # Extract the image number from the message
                    image_file = f"{image_number}.png" # Construct the image file path
                    show_image(os.path.join(image_path, image_file)) # Show the image

                elif received_message == "[USBCommunication] closeimage":
                    print(received_message)
                    close_image() # Close the image
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

