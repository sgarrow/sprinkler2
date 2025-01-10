'''
This is the user interface to the server.  All of the files in this project
must be on the RPi except this one although it may/can also be on the RPi.

If this file can be run on the Rpi, a PC or a phone.
'''

try:
    import readline         # So up arrow will recall last entered command.
    print(readline.backend) # This line just to eliminate a pylint error.
except (ModuleNotFoundError, AttributeError):
    print('\n Exception importing readline. ok to continue.\n')

import sys
import socket
import time
import select
import threading
import queue
#############################################################################

def printSocketInfo(cSocket):
    sndBufSize = cSocket.getsockopt( socket.SOL_SOCKET, socket.SO_SNDBUF )
    rcvBufSize = cSocket.getsockopt( socket.SOL_SOCKET, socket.SO_RCVBUF )
    print( ' sndBufSize', sndBufSize ) # 64K
    print( ' rcvBufSize', rcvBufSize ) # 64K
#############################################################################

def getUserInput( mainToUiQ, uiToMainQ, aLock ):

    userInput = ''
    while True:
        with aLock:
            try:
                sapState = mainToUiQ.get(timeout=.02)
            except queue.Empty:
                sapState = '0'

            if sapState in ['0','1']:
                if sapState == '1':
                    prompt = '\n Enter num of dsrd Act Prof (or \'q\') -> '
                else:
                    prompt = '\n Choice (m=menu, q=quit) -> '
                userInput = input( prompt )

        if sapState != '0':
            uiToMainQ.put('sap {}'.format(userInput))
        else:
            uiToMainQ.put(userInput)

        time.sleep(.01) # Gives 'main' a chance to run.
#############################################################################

if __name__ == '__main__':

    # Each client will connect to the server with a new address.
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    connectType = input(' ssh, lan, internet (s,l,i) -> ')
    #             {'s':'localhost','l':'lanAddr','i':'routerAddr'}
    connectDict = {'s':'localhost','l':'0.0.0.0','i':'00.00.00.00'}
    PORT = 0000
    try:
        clientSocket.connect((connectDict[connectType], PORT ))
    except ConnectionRefusedError:
        print('\n ConnectionRefusedError.  Ensure server is running.\n')
        sys.exit()
    except socket.timeout:
        print('\n TimeoutError.  Ensure server is running.\n')
        sys.exit()

    printSocketInfo(clientSocket)

    threadLock  = threading.Lock()
    main2UiQ    = queue.Queue()
    Ui2MainQ    = queue.Queue()
    inputThread = threading.Thread( target = getUserInput,
                                    args   = (main2UiQ,Ui2MainQ,threadLock),
                                    daemon = True )
    inputThread.start()

    while True:
        try:
            message = Ui2MainQ.get()
        except queue.Empty:
            pass
        else:
            clientSocket.send(message.encode())

        with threadLock:
            readyToRead, _, _ = select.select([clientSocket], [], [], .6)
            if readyToRead:
                rspStr = ''
                while readyToRead:
                    response = clientSocket.recv(1024)
                    rspStr += response.decode()

                    if 'RE: ks' in rspStr:
                        break

                    readyToRead,_, _=select.select([clientSocket],[],[],.25)
                print('\n{}'.format(rspStr))

                SAP_STE = 0
                if 'sapState = ' in rspStr:
                    idxStart = rspStr.index('sapState = ')
                    idxEnd   = idxStart + len('sapState = ')
                    SAP_STE = rspStr[idxEnd]
                    main2UiQ.put(SAP_STE)
                #print(' mn sapState = ', SAP_STE)

        if message == 'close' or 'RE: ks' in rspStr:
            break

    print('\n Client closing Socket')
    clientSocket.close()
