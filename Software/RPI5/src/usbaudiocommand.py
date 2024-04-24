import serial
import os
import subprocess
import signal

# Variable to keep track of the current audio process
current_audio_process = None

def play_audio(audio_path):
    global current_audio_process

    if os.path.exists(audio_path):
        print(f"Playing audio: {audio_path}")  # Print command
        # Stop the current audio process if there is one
        if current_audio_process:
            current_audio_process.terminate()  # Terminate command
            current_audio_process.wait()  # Wait command
        
        # Start the new audio process with VLC in the background
        current_audio_process = subprocess.Popen(["cvlc", audio_path])  # Subprocess command
    else:
        print("Audio file not found:", audio_path)  # Print command

def stop_audio():
    global current_audio_process

    # Stop the current audio process if there is one
    if current_audio_process:
        current_audio_process.terminate()  # Terminate command
        current_audio_process.wait()  # Wait command
        current_audio_process = None

def main():
    # Open the serial port
    s = serial.Serial(port="/dev/ttyACM0", baudrate=115200, timeout=1)  # Serial command

    try:
        while True:
            # Read a message from the serial port
            received_message = s.readline().decode().strip()  # Readline command, Decode command, Strip command
            print(received_message)  # Print command

            # Check if the received message is for playing audio
            if received_message.startswith("[USBCommunication] playaudio"):
                # Extract the audio file number from the message
                audio_number = received_message.split(" ")[-1]  # Split command
                # Construct the audio file path
                audio_path = f"{audio_number}.m4a"  # Format command
                # Play the audio
                play_audio(audio_path)  # Play_audio function call
            elif received_message == "[USBCommunication] stopaudio":
                # Stop the audio
                stop_audio()  # Stop_audio function call
                print("Stopped audio playback")  # Print command
    except Exception as e:
        print(f"An error occurred: {e}")  # Print command

if __name__ == "__main__":
    main()  # Main function call
