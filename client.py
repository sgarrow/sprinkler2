'''
This is the user interface to the server.  All of the files in this project
must be on the RPi except this one although it may/can also be on the RPi.

If this file is on the RPi then both the server and the client may both be
run on the RPi.  

If this file is on, for example, a PC, the the client can be rn on a PC.
This is like how, for example, your Web Browser (a client) talks to the 
google server.
'''

try:
    import readline
except ModuleNotFoundError:
    print(' exception importing readline. ok to continue.')

import socket
import time
import select
import pickle
import threading
import queue
#############################################################################

def printSocketInfo(cSocket):
    sndBufSize = cSocket.getsockopt( socket.SOL_SOCKET, socket.SO_SNDBUF )
    rcvBufSize = cSocket.getsockopt( socket.SOL_SOCKET, socket.SO_RCVBUF )
    print( ' sndBufSize', sndBufSize ) # 64K
    print( ' rcvBufSize', rcvBufSize ) # 64K
#############################################################################

def getUserInput( mainToUiQ, UiToMainQ, aLock ):
    userInput = None

    while True:

        with aLock:

            try:
                sapState = main2UiQ.get(timeout=.02)
            except queue.Empty:
                sapState = '0'
            print(' ui sapState = ', sapState)

            if sapState in ['0','1']:
                if sapState == '1':
                    prompt = '\n Enter num of dsrd Act Prof (or \'q\') -> ' 
                else:
                    prompt = '\n Choice (m=menu, q=quit) -> '

                userInput = input( prompt )

        if sapState != '0':
            # Sleep RE: hammering w/ back-to-back sap's causes occasional
            # probs w/ server writing to pickle while client trying to read.
            time.sleep(.015)
            #UiToMainQ.put('sap')
            if sapState == '1':
                UiToMainQ.put('sap {}'.format(userInput))
            else:
                UiToMainQ.put('sap {}'.format(userInput))
        else:
            UiToMainQ.put(userInput)

        time.sleep(.01) # Gives 'main' a chance to run.
        if userInput == 'close':
            break
#############################################################################

if __name__ == '__main__':

    # Each client will connect to the server with a new address.
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # if client running on a different machine and host ip = 192.168.1.5
    # and server and client on same network.
    clientSocket.connect(('192.168.1.5', 5000))

    # if client and host running on same machine.
    #clientSocket.connect(('localhost', 5000))

    printSocketInfo(clientSocket)
    threadLock  = threading.Lock()
    main2UiQ    = queue.Queue()
    Ui2MainQ    = queue.Queue()
    inputThread = threading.Thread( target = getUserInput, 
                                    args   = (main2UiQ,Ui2MainQ,threadLock)
                                  )
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
                    readyToRead, _, _ = select.select([clientSocket],[],[], .25)
                print('\n{}'.format(rspStr))

                sapState = 0
                if 'sapState = ' in rspStr:
                    idxStart = rspStr.index('sapState = ')
                    idxEnd   = idxStart + len('sapState = ')
                    sapState = rspStr[idxEnd]
                    main2UiQ.put(sapState)
                print(' mn sapState = ', sapState)


        if message == 'close':
            break

    clientSocket.close()
