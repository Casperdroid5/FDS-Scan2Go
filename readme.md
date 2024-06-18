# FDS-Scan2Go

## Overview
The Ferrous Metal Detection Gate (FDS) is a sophisticated system designed to enhance safety for MRI room access by detecting ferrous metals. This system utilizes a Raspberry Pi Pico and Raspberry Pi 5 to facilitate communication with various sensors, providing both auditory and visual feedback to the user.

## Table of Contents
- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Software Setup](#software-setup)
- [Installation](#installation)
  - [Raspberry Pi Pico](#raspberry-pi-pico)
  - [Raspberry Pi 5](#raspberry-pi-5)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features
- Utilizes a ferrous metal detector for metal detection
- Provides auditory and visual feedback to the user
- Employs both Raspberry Pi Pico and Raspberry Pi 5
- Communicates with multiple sensors for enhanced detection accuracy

## Hardware Requirements
### Raspberry Pi Pico
- All the wanted peripherals (buttons, sensors etc.)
- Micro usb cable (ensure it has data wires)

### Raspberry Pi 5
- Raspberry Pi 25W, power supply
- USB to 3.5mm audio adapter
- Display/monitor for imageoutput
- MicroHDMI to HDMI adapter 

## Software Setup
### Prerequisites
- Python 3.12 or higher
- Required Python libraries (listed in `requirements_rpi5.txt` for Raspberry Pi 5)
- MicroPython libraries for Raspberry Pi Pico (listed in `requirements_pico.txt`)

## Installation
### Raspberry Pi Pico

1. **Install Dependencies**
   Since the Pico runs on MicroPython for this project, you'll need to upload the required libraries manually or use a tool like `mpremote`.

   ```sh
   mpremote mip install micropython-neopixel micropython-machine micropython-time micropython-i2c micropython-uart
   ```

2. **Upload Scripts to Pico**
   Upload the relevant `.py` files to the Pico:
   ```sh
   mpremote fs cp hardware_s2g.py :hardware_s2g.py
   mpremote fs cp system_utils.py :system_utils.py
   mpremote fs cp main.py :main.py
   ```

### Raspberry Pi 5
1. **Prepare MicroSD Card**
   Install Raspbian 64-bit (with desktop) on a 32GB MicroSD card (using Raspberry Pi Imager, for example). Once installed, boot the Raspberry Pi 5, connect it to the internet, and open a terminal with root permissions.

2. **Install Python Dependencies**
   ```sh
   pip install -r requirements_rpi5.txt
   ```

3. **Install System Dependencies**
   ```sh
   sudo apt-get update
   sudo apt-get install feh vlc
   ```

4. **Run the Application**
   Navigate to the project directory and start the main script:
   ```sh
   python main.py
   ```

## Usage
1. **Connect the Raspberry Pi Pico and Raspberry Pi 5 via a MicroUSB cable.**
2. **Start the `main.py` script on the Raspberry Pi 5.**
3. The system will initialize, and the sensors will begin to monitor for ferrous metals. The NeoPixel LEDs and the display will provide feedback based on the detection status.

## Contributing
We welcome contributions to the FDS-Scan2Go project. If you would like to contribute, please fork the repository and submit a pull request. 

If you would like to emplement this code into your own project, ensure to give credit to the original author and mention any significant changes or improvements.

## Disclaimer
This project is licensed under the MIT License. See the [DISCLAIMER](/Software/DISCLAIMER.txt) file for more details.
