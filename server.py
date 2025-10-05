import sys                   # For getting command line args.
import socket                # For creating and managing sockets.
import threading             # For handling multiple clients concurrently.
import queue                 # For Killing Server.
import time                  # For Killing Server and listThreads.
import datetime        as dt # For logging server start/stop times.
import cmdVectors      as cv # Contains vectors to "worker" functions.
import cfg                   # For port, pwd.
import utils           as ut # For access to openSocketsLst[].
import multiprocessing as mp
#############################################################################

def getMultiProcSharedDict():
    manager = mp.Manager()
    styleDict = manager.dict({
        'tbd1' : 'tbd1',
        'tbd2' : 'tbd2',
        'tbd3' : 'tbd3',
        'tbd4' : 'tbd4',
        'tbd5' : 'tbd5',
        'tbd6' : 'tbd6',
    })
    styleDictLock = mp.Lock()
    return styleDict, styleDictLock
#############################################################################

def ksCleanup(styleDict, styleDictLock):
    rspStr  = ''
### START KS CODE REMOVE ###
    rspStr += cv.vector('sp',  styleDict, styleDictLock) + '\n' 
    rspStr += '\n\n' + cv.vector('or 12345678', styleDict, styleDictLock) + '\n' 
### END KS CODE REMOVE ###
    return rspStr
#############################################################################

def processCloseCmd(clientSocket, clientAddress):
    rspStr = ' handleClient {} set loop break RE: close \n'.format(clientAddress)
    clientSocket.send(rspStr.encode()) # sends all even if >1024.
    time.sleep(1) # Required so .send happens before socket closed.
    # Breaks the loop, connection closes and thread stops.
    ut.openSocketsLst.remove({'cs':clientSocket,'ca':clientAddress})
    return rspStr
#############################################################################

def processKsCmd( clientSocket, clientAddress, client2ServerCmdQ,
                  styleDict, styleDictLock ):
    rspStr = ''
    # Client sending ks has to be terminated first, I don't know why.
    rspStr += ksCleanup(styleDict, styleDictLock)
    rspStr += '\n handleClient {} set loop break for self RE: ks \n'.\
              format(clientAddress)
    clientSocket.send(rspStr.encode()) # sends all even if > 1024.
    time.sleep(1.5) # Required so .send happens before socket closed.

    # Breaks the ALL loops, ALL connections close and ALL thread stops.
    for el in ut.openSocketsLst:
        if el['ca'] != clientAddress:
            rspStr += ' handleClient {} set loop break for {} RE: ks \n'.\
                format(clientAddress, el['ca'])
            el['cs'].send(rspStr.encode()) # sends all even if > 1024.
            time.sleep(1) # Required so .send happens before socket closed.

    ut.openSocketsLst.clear()
    client2ServerCmdQ.put('ks')
    rspStrNew = rspStr.replace('ks','KS') # Keep client from breaking RE: rsl

    return rspStrNew
#############################################################################

def handleClient( clientSocket, clientAddress, client2ServerCmdQ,
                  styleDict, styleDictLock, uut ):

    rspStr = ''
    # Validate password
    cfgDict = cfg.getCfgDict(uut)
    data = clientSocket.recv(1024)
    if data.decode() == cfgDict['myPwd']:
        passwordIsOk = True
        rspStr += ' Accepted connection from: {}\n'.format(clientAddress)
    else:
        passwordIsOk = False
        rspStr += ' Rejected connection from: {}\n'.format(clientAddress)

    ut.writeFile('serverLog.txt', rspStr)
    #print(rspStr)
    clientSocket.send(rspStr.encode()) # sends all even if >1024.

    if passwordIsOk:
        clientSocket.settimeout(3.0)   # Set .recv timeout - ks processing.
        ut.openSocketsLst.append({'cs':clientSocket,'ca':clientAddress})

    # The while condition is made false by the close and ks command.
    while {'cs':clientSocket,'ca':clientAddress} in ut.openSocketsLst:

        logStr = ''
        # Recieve msg from the client (and look (try) for UNEXPECTED EVENT).
        try: # In case user closed client window (x) instead of by close cmd.
            data = clientSocket.recv(1024) # Broke if any msg from client > 1024.
        except ConnectionResetError: # Windows throws this on (x).
            logStr += ' handleClient {} ConnectRstErr except in s.recv\n'.format(clientAddress)
            # Breaks the loop. handler/thread stops. Connection closed.
            ut.openSocketsLst.remove({'cs':clientSocket,'ca':clientAddress})
            break
        except ConnectionAbortedError: # Test-NetConnection xxx.xxx.x.xxx -p xxxx throws this
            logStr += ' handleClient {} ConnectAbtErr except in s.recv\n'.format(clientAddress)
            ut.openSocketsLst.remove({'cs':clientSocket,'ca':clientAddress})
            break
        except socket.timeout: # Can't block on recv - won't be able to break
            continue           # loop if another client has issued a ks cmd.

        # Getting here means a command has been received.
        logStr = ' handleClient {} received: {}\n'.format(clientAddress, data.decode())

        # Process a "close" message and send response back to the local client.
        if data.decode() == 'close':
            logStr += processCloseCmd(clientSocket, clientAddress)

        # Process a "ks" message and send response back to other client(s).
        elif data.decode() == 'ks':
            logStr += processKsCmd( clientSocket, clientAddress,
                                    client2ServerCmdQ, styleDict, styleDictLock )

        # Process a "standard" msg and send response back to the client,
        # (and look (try) for UNEXPECTED EVENT).
        else:
            response = cv.vector(data.decode(),styleDict, styleDictLock)
            try: # In case user closed client window (x) instead of by close cmd.
                clientSocket.send(response.encode())
            except BrokenPipeError:      # RPi throws this on (x).
                logStr += ' handleClient {} BrokePipeErr except in s.send\n'.format(clientAddress)
                # Breaks the loop. handler/thread stops. Connection closed.
                ut.openSocketsLst.remove({'cs':clientSocket,'ca':clientAddress})

        if logStr != '':
            ut.writeFile('serverLog.txt', logStr)
            #print(logStr)

    logStr = ' handleClient {} closing socket and breaking loop\n'.format(clientAddress)
    ut.writeFile('serverLog.txt', logStr)
    #print(logStr)
    clientSocket.close()
#############################################################################

def printSocketInfo(sSocket):
    sndBufSize = sSocket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
    rcvBufSize = sSocket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    rspStr = ' sndBufSize = {} \n rcvBufSize = {}\n'.format(sndBufSize,rcvBufSize)
    return rspStr # 64K
#############################################################################

def startServer(uut):
    now = dt.datetime.now()
    cDT = '{}'.format(now.isoformat( timespec = 'seconds' ))
    logStr =  'Server started at {} \n'.format(cDT)
    ut.writeFile('serverLog.txt', logStr)
    #print(logStr)

    styleDict, styleDictLock = ut.getMultiProcSharedDict()
    #print('startServer', styleDict, styleDictLock)

    host = '0.0.0.0'  # Listen on all available interfaces
    cfgDict = cfg.getCfgDict(uut)
    port = int(cfgDict['myPort'])

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # This line makes it so you can kill the server and then restart it right
    # away.  Without this you get an error until the socket eventually is
    # complete closed by th os. Here's the error you get without this:
    #
    #  File "/home/pi/python/spiClock/server.py", line 204, in <module>
    #  startServer()
    #  File "/home/pi/python/spiClock/server.py", line 145, in startServer
    #  serverSocket.bind((host, port))
    #  OSError: [Errno 98] Address already in use
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    serverSocket.bind((host, port))
    serverSocket.listen(5)
    serverSocket.settimeout(3.0) # Sets the .accept timeout - ks processing.

    clientToServerCmdQ = queue.Queue() # So client can tell server to stop.

    logStr  = 'Server listening on: {} {}\n'.format(host, port)
    logStr += printSocketInfo(serverSocket)
    ut.writeFile('serverLog.txt', logStr)
    #print(logStr)

    while True:
        logStr = ''
        # See if any client has requested the server to halt (ks command).
        try:
            cmd = clientToServerCmdQ.get(timeout=.1)
        except queue.Empty:
            pass
        else:
            if cmd == 'ks':
                threadLst = [ t.name for t in threading.enumerate() ]
                while any(el.startswith('handleClient-') for el in threadLst):
                    threadLst = [ t.name for t in threading.enumerate() ]
                    time.sleep(.1)
                break

        # See if any new clients are trying to connect.
        try:
            clientSocket, clientAddress = serverSocket.accept()
        except socket.timeout: # Can't block on accept - won't be able to
            continue           # break loop if a client has issued a ks cmd.
        else:
            # Yes, create a new thread to handle the new client.
            logStr += 'Starting a new client handler thread.\n'

            cThrd = threading.Thread( target=handleClient,

                                      args = ( clientSocket,
                                               clientAddress,
                                               clientToServerCmdQ,
                                               styleDict,
                                               styleDictLock,
                                               uut ),

                                      name =   'handleClient-{}'.\
                                               format(clientAddress) )
            cThrd.start()

        if logStr != '':
            ut.writeFile('serverLog.txt', logStr)
            #print(logStr)

    logStr = 'Server breaking.\n'
    serverSocket.close()

    now = dt.datetime.now()
    cDT = '{}'.format(now.isoformat( timespec = 'seconds' ))
    logStr += 'Server stopped at {} \n'.format(cDT)
    ut.writeFile('serverLog.txt', logStr)
    #print(logStr)
#############################################################################

if __name__ == '__main__':

    #import spiRoutines as sr
    arguments  = sys.argv
    scriptName = arguments[0]
    uut        = None
    if len(arguments) >= 2:
        userArgs   = arguments[1:]
        uut        = userArgs[0]
        cfgDict    = cfg.getCfgDict(uut)

    if uut is None or cfgDict is None:
        print('  Server not started.')
        print('  Missing or (malformed) cfg file or')
        print('  Missing or (malformed) cmd line arg')
        print('  usage1: python server.py uut (uut = spr, clk, clk2).')
        sys.exit()
    else:
        pass
### START MN CODE REMOVE ###
### END MN CODE REMOVE ###

    startServer(uut)
