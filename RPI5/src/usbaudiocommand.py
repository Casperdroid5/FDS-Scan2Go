import serial
import os

def play_audio(audio_path):
    if os.path.exists(audio_path):
        print(f"Playing audio: {audio_path}")
        os.system(f"vlc {audio_path} &")  # Play the audio using VLC in the background
    else:
        print("Audio file not found:", audio_path)

def stop_audio():
    os.system("pkill vlc")  # Stop all instances of VLC

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
                # Extract the audio number from the message
                audio_number = received_message.split(" ")[-1]
                # Construct the audio file path
                audio_path = f"{audio_number}.m4a"
                # Play the audio
                play_audio(audio_path)
            elif received_message == "[USBCommunication] stopaudio":
                # Stop the audio
                stop_audio()
                print("Stopped audio playback")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
