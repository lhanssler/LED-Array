# import LED_Array
import numpy as np
import LED_Array

board = LED_Array.board_initializer('/dev/cu.usbserial-1420')
file = np.loadtxt('/Users/logan-hanssler/Documents/Python Code for Arduino/PCB Data', skiprows=5)
LEDs = LED_Array.LED_setup(board, file)
LED_Array.global_off(LEDs)

while True:
    # Flashes LED corresponding to number given for variable LED num_flashes_input times for time_delay_input delays
    LED_num_input = int(input('Which LED would you like to turn on?'))
    V_multiplier_input = float(input('At what voltage multiplier? (Must be 0 - 1.)'))
    duration_input = float(input('How long would you like the LED to stay on for in seconds?'))
    LED_Array.pwm(LEDs, LED_num_input, V_multiplier_input, duration_input)
