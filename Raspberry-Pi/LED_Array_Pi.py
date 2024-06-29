import time
import board
import digitalio
import busio
import adafruit_pca9685

def board_connect(driver_contents, LED_contents, freq=60):
    '''
    Imports the Raspberry Pi, connects with any attached drivers by establishing a driver dictionary,
    and establishes an LED dictionary for the array connected to the microcontroller.

    Parameters:
        driver_contents (dict) - key: value is count: data;
                                 count (int) is the number corresponding to a given driver,
                                 which will become its key in the output dictionary for drivers.
                                 value (list) is [SCL_GP, SDA_GP, add].
                                 SCL_GP is an int corresponding to the Raspberry Pi's GP used
                                 for this driver's SCL connection.
                                 SDA_GP is an int corresponding to the Raspberry Pi's GP used
                                 for this driver's SDA connection.
                                 add is an int (generally given in hexadecimal) which is this
                                 driver's address, used in forming the i2c connection.

        LED_contents    (dict) - key: value is count: data;
                                 count (int) is the number corresponding to a given set
                                 of data describing one of the non-i2c pins being used.
                                 value (list) is [pin, row, col, driver].
                                 For a cathode, pin is an int corresponding to the Raspberry
                                 Pi's GP used for this pin.
                                 For an anode, pin is an int corresponding to the driver's
                                 channel used for this pin.
                                 row is an int corresponding to the LED array's row which this
                                 pin controls. If this pin controls a column, not a row, then row=0.
                                 col is an int corresponding to the LED array's column which this
                                 pin controls. If this pin controls a row, not a column, then col=0.
                                 If this pin is a cathode, then driver=0.
                                 If this pin is an anode, then driver is an int corresponding to
                                 the driver this pin is on. Specifically, driver is the key (count)
                                 which is subscripted in the output dictionary of drivers to find
                                 the driver corresponding to this pin.

        freq            (int)  - the frequency established for the pca connections to drivers.
                                 default value 60.

    Returns:
        drivers         (dict) - key: value is count: data;
                                 count (int) is the number corresponding to a given driver and
                                 is the same as the key count for parameter driver_contents.
                                 data (list) is [i2c, pca].
                                 i2c is the i2c object corresponding to this driver connection.
                                 pca is the pca object corresponding to this driver connection.

        LEDs            (dict) - key: value is count: data;
                                 count (int) is the number corresponding to a given LED.
                                 data (list) is [anode, cathode].
                                 anode is the driver channel object corresponding to to this
                                 LED's anode.
                                 cathode is the GP object corresponding to this LED's cathode.
    '''

    # Initializing drivers
    drivers = {}
    for key in driver_contents:
        SCL, SDA, add = driver_contents[key]
        SCL = eval('board.GP{}'.format(SCL))
        SDA = eval('board.GP{}'.format(SDA))
        i2c = busio.I2C(SCL, SDA)
        pca = adafruit_pca9685.PCA9685(i2c, address=add)
        pca.frequency = freq
        drivers[key] = [i2c, pca]

    # Unpacking cathodes and anodes
    cathodes, anodes = {}, {}
    for key in LED_contents:
        vals = LED_contents[key]
        if vals[-1] == 0:
            # No associated driver, must be cathode
            cathodes[key] = vals[:-1]
        else:
            # Associated driver exists, must be anode
            anodes[key] = vals

    # Determining rows/cols
    a_temp, c_temp = [], []
    keys = []
    for key in anodes:
        keys.append(key)
    if anodes[keys[0]][1] == 0:
        acol = True # Anodes are columns
    else:
        acol = False # Anodes are rows
    for key in anodes:
        vals = anodes[key]
        if acol:
            a_temp.append([key, vals[0], vals[2], vals[3]])
        else:
            a_temp.append([key, vals[0], vals[1], vals[3]])
    for key in cathodes:
        vals = cathodes[key]
        if acol:
            c_temp.append([key, vals[0], vals[1]])
        else:
            c_temp.append([key, vals[0], vals[2]])

    # Sorting by ascending rows/cols
    anodes, cathodes = [], []
    a_count, c_count = len(a_temp), len(c_temp)
    while len(a_temp) > 0:
        minim = a_count + 5
        min_ind = minim
        for i in range(len(a_temp)):
            if a_temp[i][2] < minim:
                minim = a_temp[i][2]
                min_ind = i
        anodes.append(a_temp[min_ind])
        a_temp.pop(min_ind)
    while len(c_temp) > 0:
        minim = c_count + 5
        min_ind = minim
        for i in range(len(c_temp)):
            if c_temp[i][2] < minim:
                minim = c_temp[i][2]
                min_ind = i
        cathodes.append(c_temp[min_ind])
        c_temp.pop(min_ind)

    # Creating anode and cathode pin objects
    a_final, c_final = [], []
    for anode in anodes:
        channel_num = anode[1]
        driver_key = anode[3]
        pca_connect = drivers[driver_key][1]
        a = pca_connect.channels[channel_num]
        a.duty_cycle = 0
        a_final.append(a)
    for cathode in cathodes:
        GP_num = cathode[1]
        c = eval('digitalio.DigitalInOut(board.GP{})'.format(GP_num))
        c.direction = digitalio.Direction.INPUT
        c_final.append(c)

    # Populating the LED output dictionary
    LEDs = {}; num = 1
    if acol:
        for cathode in c_final:
            # Loop over cathodes first to stay within a row
            for anode in a_final:
                LEDs[num] = [anode, cathode]
                num += 1
    else:
        for anode in a_final:
            # Loop over anodes first to stay within a row
            for cathode in c_final:
                LEDs[num] = [anode, cathode]
                num += 1

    return drivers, LEDs

def global_off(LEDs):
    '''
    Turns off all LEDs by turning off their pins. Cycles through all LEDs to set all anode
    duty cycles to 0 and all cathode directions to INPUT with a False value stored for the
    OUTPUT direction.

    Parameters:
        LEDs (dict) - dictionary returned by board_connect function to describe the LED array.

    Returns:
        None
    '''

    anodes, cathodes = [], []
    for key in LEDs:
        a, c = LEDs[key]
        anodes.append(a); cathodes.append(c)

    for anode in anodes:
        anode.duty_cycle = 0
    for cathode in cathodes:
        cathode.direction = digitalio.Direction.OUTPUT
        cathode.value = False
        cathode.direction = digitalio.Direction.INPUT

def global_on(LEDs, bright=1.):
    '''
    Turns on all LEDs by turning on their pins. Cycles through all LEDs to set all anode
    duty cycles to a given value and all cathode directions to OUTPUT with a False value.

    Parameters:
        LEDs   (dict)   - dictionary returned by board_connect function to describe the LED array.

        bright (float)  - the brightness factor to which the anodes should be turned on.
                          Modular from 0 to 1, non-inclusive of 0.
                          Possible duty cycles range from 0x0000 to 0xffff; the anodes are
                          turned on to duty cycle bright*0xffff.
                          Default value 1. corresponds to duty cycle 0xffff for max brightness.

    Returns:
        None
    '''

    # Setting the duty cycle
    if bright > 1:
        bright %= 1
    if bright == 0:
        bright = 1
    duty = int(bright * 0xffff)

    # Turning on LEDs
    anodes, cathodes = [], []
    for key in LEDs:
        a, c = LEDs[key]
        anodes.append(a); cathodes.append(c)

    for anode in anodes:
        anode.duty_cycle = duty
    for cathode in cathodes:
        cathode.direction = digitalio.Direction.OUTPUT
        cathode.value = False

def pwm(LEDs, LED_num, bright=1., duration=1):
    '''
    Does pulse width modulation on a given LED with a given duty cycle for a given duration in time.

    Parameters:
        LEDs     (dict)  - dictionary returned by board_connect function to describe the LED array.

        LED_num  (int)   - key corresponding to the given LED in LEDs which should do pulse width
                           modulation.

        bright   (float) - the brightness factor to which the anodes should be turned on.
                           Modular from 0 to 1, non-inclusive of 0, unless bright=0.
                           Possible duty cycles range from 0x0000 to 0xffff; the anodes are
                           turned on to duty cycle bright*0xffff.
                           Default value 1. corresponds to duty cycle 0xffff for max brightness.

        duration (float) - time (in seconds) for which the LED should remain on and continue doing
                           pulse width modulation.

    Returns:
        None
    '''

    # Setting the duty cycle
    if bright == 0:
        flag = False # Stops setting of bright=0 to bright=1
    else:
        flag = True
    if bright > 1:
        bright %= 1
    if bright == 0 and flag:
        bright = 1
    duty = int(bright * 0xffff)

    # Retrieving anode and cathode
    anode, cathode = LEDs[LED_num]

    # Turning on
    cathode.direction = digitalio.Direction.OUTPUT
    cathode.value = False
    anode.duty_cycle = duty
    time.sleep(duration)

    # Turning off
    anode.duty_cycle = 0
    cathode.direction = digitalio.Direction.INPUT
    time.sleep(0.0075) # Prevents visual glitches caused by quickly changing cathodes
