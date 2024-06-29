This repository contains my Python code for controlling the LED array using either an Arduino (via PyFirmata) or a Raspberry Pi (via CircuitPython).
The repository contains 2 folders dividing my code by the intended microcontroller: Arduino and Raspberry-Pi.

The Arduino folder contains 4 files:
- LED_Array.py is my module containing functions to control the LED array via PyFirmata. PyFirmata's bootloader should be run on the Arduino via the IDE, and this file can be imported in Python to interact with the bootloader and operate individual LEDs.
- PCB_Data.txt is the configuration text file I have been using to set up the LED array via LED_Array.py. Some configuration text file is needed to set up the LED array dictionary using LED_Array.py; this text file is intended as an example template.
- main_demo.py is an example main script which calls LED_Array.py functions and controls the LED array from PCB_Data.txt. This main script cycles through LEDs on the array and uses PWM to make an LED slowly light up, then slowly turn off before moving to the next LED.
- main_pwm.py is an example main script which calls LED_Array.py functions and controls the LED array from PCB_Data.txt. This main script prompts the user to input parameters for the arguments to the LED_Array.pwm() function, then calls the function accordingly and asks the user to do so again in an infinite loop.

The Raspberry-Pi folder contains 5 items (each of which must be stored on the Raspberry Pi for my CircuitPython code to run correctly):
- lib is a folder containing 4 Python modules made by Adafruit. These files tell CircuitPython how to interact with the Raspberry Pi and PCA9685 chip. The lib folder must contain all libraries used by the CircuitPython code.
- LED_Array_Pi.py is a modified version of my LED_Array.py module. It has been edited to work with the Adafruit modules' syntax to appropriately control the Raspberry Pi and PCA9685.
- boot_out.txt is a file created by CircuitPython to describe the Raspberry Pico H being controlled.
- code.py is an example main script which calls LED_Array_Pi.py functions and controls the LED array which is described in dictionaries at the beginning of the main script. It should be noted that these dictionaries must replace the configuration text file in CircuitPython code, and any script intended to be run as main by CircuitPython must be named code.py and stored on the microcontroller. This main script cycles through LEDs on the array, making each one use PWM to gradually get brighter and then get dimmer until off.
- settings.toml is a file created by CircuiPython as a configuration file for the microcontroller being used.
