import serial
import os
import subprocess

# Paths for audio and image files. Comment out to use current folder.
audio_path = "/home/PIons3/FDS-Scan2GO/Software/FDS_media/Soundfiles_FDS/"  # change to the path of the audio files
image_path = "/home/PIons3/FDS-Scan2GO/Software/FDS_media/Displayimages_FDS/"  # change to the path of the image files

# Variable to keep track of the current audio process
current_audio_process = None

def play_audio(audio_path):
    """
    Play audio file using VLC.

    Args:
        audio_path (str): The path to the audio file.

    Returns:
        None
    """
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
    """
    Stop the audio playback.

    Returns:
        None
    """
    global current_audio_process

    # Stop the current audio process if there is one
    if current_audio_process:
        current_audio_process.terminate()
        current_audio_process.wait()
        current_audio_process = None

def show_image(image_path):
    """
    Show image using feh.

    Args:
        image_path (str): The path to the image file.

    Returns:
        None
    """
    if os.path.exists(image_path):
        print(f"Opening image: {image_path}")
        os.system(f"feh -ZF {image_path} &")  # Open the image using feh
    else:
        print("Image file not found:", image_path)

def close_image():
    """
    Close all instances of feh.

    Returns:
        None
    """
    os.system("pkill feh")  # Close all instances of feh

def main():
    """
    Main function to handle serial communication and actions based on received messages.

    Returns:
        None
    """
    global image_path

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
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()

