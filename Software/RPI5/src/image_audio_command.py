import serial
import os
import subprocess

# Paths for audio and image files. Comment out to use current folder.
audio_path = "/home/PIons3/FDS-Scan2GO/Software/FDS media/Soundfiles FDS"
image_path = "/home/PIons3/FDS-Scan2GO/Software/FDS media/Displayimages FDS"

# Variable to keep track of the current audio process
current_audio_process = None

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
            
            # Check if the received message is for playing audio
            if received_message.startswith("[USBCommunication] playaudio"):
                # Extract the audio file number from the message
                audio_number = received_message.split(" ")[-1]
                # Construct the audio file path
                audio_path = f"{audio_number}.m4a"
                # Play the audio
                play_audio(audio_path)
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

