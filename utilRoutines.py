import os
import gpiozero

VERSION  = ' Version:  1.9'
RELEASED = ' Released: 28-Oct-2024'
#############################################################################

def getTemp(prnEn = True):

    cpu = gpiozero.CPUTemperature()

    if prnEn:
        print(' CPU  Temp = {}'.format( cpu.temperature ))
        print(' Over Temp = {}'.format( cpu.is_active   ))

        print()
        os.system('vcgencmd get_throttled')
        print('  0: under-voltage')
        print('  1: arm frequency capped')
        print('  2: currently throttled ')
        print(' 16: under-voltage has occurred')
        print(' 17: arm frequency capped has occurred')
        print(' 18: throttling has occurred')

    return cpu
#############################################################################

def getVer():
    print(VERSION)
    print(RELEASED)
    return VERSION, RELEASED
#############################################################################

def verifyRelayArgs( optArgsStr ):

    # Make sure all the optArgs are ints. If not a prompt (in relayOCTR) will
    # occur.  1 2 3 works, 1 2 X will prompt.
    try:
        optArgs1 = [ int(x) for x in optArgsStr ]
    except ValueError:
        optArgs1 = []

    # Split any integers > 10 into digits. 123 works, becomes 1 2 3.
    optArgs2 = []
    for el in optArgs1:
        if el > 10:
            digits = [int(d) for d in str(el)]
            optArgs2.extend(digits)
        else:
            optArgs2.append(el)

    # Remove dups and nums out of range
    optArgsNoDups = list(set(optArgs2))
    optArgsNoGT8LE0  = [ x for x in optArgsNoDups if 0 < x < 9 ]

    return sorted(optArgsNoGT8LE0)
#############################################################################
