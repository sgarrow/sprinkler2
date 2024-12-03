'''
The only function in this file is named "init".  It is called automatically
when the main script (sprinkler.py) is started (from the command line).

The init routine creates two things:

   (1) a list of relay-objects, one obj for each relay.  Each object contains
       "methods" for the associated relay, i.e., "on", "off" and "pin".

   (2) a cross reference dictionary of GPIO to board-pin and associated
       relay it is wired to.

These two items are returned to the main scrips who, in turn, passes them to
other functions who need them (those functions are in file relayRoutines.py).

Relay-objs have methods on,off,pin to close,open,get-GPIO-name, respectively.
The dictionary is just used to make the print statements more meaningfull,
other than that there is no real functionality.
'''

# Import a library that comes pre-installed on the RPi. It's nonstandard -
# not part of a standard python installation but already downloaded and
# installed on an RPi. Lots of data on the gpiozero here:
# https://gpiozero.readthedocs.io/en/latest/
import gpiozero

def init():

    # GPIO Number to board pin (and relay num) cross reference dictionary.
    # https://pinout.xyz/ .The data in this dict is only needed/used in
    # print statements. A given relayObj (there ane 8 such objs in the list
    # (variable) rlyGPIoObjLst, created below) has a "method" named "pin".
    # So doing something like x = relay.pin will result in x being assigned a
    # value like "GPIO5". From that one can print the  RPi pin number and
    # associated relay that that pin is controlling.
    gpioDict = { 'GPIO5' : { 'pin': 29, 'relay': 1, 'desc': 'Back Yard Mstr Bed Side' },
                 'GPIO6' : { 'pin': 31, 'relay': 2, 'desc': 'Back Yard Spa Side' },
                 'GPIO13': { 'pin': 33, 'relay': 3, 'desc': 'Hill Below Driveway' },
                 'GPIO16': { 'pin': 36, 'relay': 4, 'desc': 'Hill Above Driveway' },
                 'GPIO19': { 'pin': 35, 'relay': 5, 'desc': 'Front Yard Planter Strip' },
                 'GPIO20': { 'pin': 38, 'relay': 6, 'desc': 'NC - 24V Ready' },
                 'GPIO21': { 'pin': 40, 'relay': 7, 'desc': 'NC' },
                 'GPIO26': { 'pin': 37, 'relay': 8, 'desc': 'NC' }}
    #################################################

    # From the relay board datasheet.
    # https://www.waveshare.com/wiki/RPi_Relay_Board_(B)
    RELAY_1_GPIO = 5
    RELAY_2_GPIO = 6
    RELAY_3_GPIO = 13
    RELAY_4_GPIO = 16
    RELAY_5_GPIO = 19
    RELAY_6_GPIO = 20
    RELAY_7_GPIO = 21
    RELAY_8_GPIO = 26
    #################################################

    # A list of nums used in creating (below) a second list - of relay objs.
    relayGpioNumLst = [RELAY_1_GPIO,RELAY_2_GPIO,RELAY_3_GPIO,RELAY_4_GPIO,
                       RELAY_5_GPIO,RELAY_6_GPIO,RELAY_7_GPIO,RELAY_8_GPIO]

    # Build a list of gpiozero.OutputDevice objects. One obj for each relay.
    # These are the most important lines of code in project. Refer to:
    # https://johnwargo.com/posts/2017/driving-a-relay-board-from-python-using-gpio-zero/
    # All other gpiozero module docs on-line just talks about LED, Buttons,
    # but this one shows how to create your own "class" type ... of type "relay".
    rlyGPIoObjLst  = []
    for relayGpioNum in relayGpioNumLst:
        rlyGPIoObjLst.append( gpiozero.OutputDevice(
            relayGpioNum,
            active_high   = False,
            initial_value = False ))
    #################################################

    # Ok, after all that return the only two things
    # that the rest of the system needs.
    return gpioDict, rlyGPIoObjLst
