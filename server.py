import socket     # For creating and managing sockets.
import threading  # For handling multiple clients concurrently.
import queue
import time
import sprinkler as sp
import profileRoutines as pr
#############################################################################

def getListOfThreads():
    threadLst = []
    for t in threading.enumerate():
        threadLst.append(t.name)
    print(' list of threads = ', threadLst)
    return threadLst
#############################################################################

def listThreads():
    while True:
        time.sleep(10)
        print(' Active Threads: ')
        for t in threading.enumerate():
            print('   {}'.format(t.name))
        print(' ##################')
#############################################################################

def handleClient(clientSocket, clientAddress, rapCQ, rapRQ):
    ''' Each client handler is it's own thread.  Multiple instantiations of
        client handler threads may be active simultaneously.  These threads
        are started by the thread running "startServer". Each thread handles
        com with a single client.  Receives data from the client, processes
        it, and sends a response back.
    '''

    print('Accepted connection from: {}'.format(clientAddress))

    while True:
        data    = clientSocket.recv(1024)

        # Below if not needed.  clientSocket.recv blocks by default.
        #if not data: break

        print('*********************************')
        print('Received from: {} {}'.format(clientAddress, data.decode()))

        # Process data and send response back to the client
        if data.decode() == 'close':
            response = 'Closing connection'
            clientSocket.send(response.encode()) # sends all even if >1024.
            print('Closing: {}'.format(clientAddress))
            time.sleep(1)
            break # Causes the handler to stop and the thread end.

        elif data.decode() == 'rp':
            tList = getListOfThreads()
            if 'runAP' in tList:
                startRsp = ' runAP thread alread started'
                print(' {}'.format(startRsp))
            else:
                rapThrd = threading.Thread( target = pr.runAP,
                                            name   = 'runAP',
                                            args   = (rapCQ,rapRQ)
                                          )
                rapThrd.start()
                startRsp = ' runAP thread started'
            print(' {}'.format(startRsp))
            clientSocket.send(startRsp.encode()) # sends all even if >1024.


        elif data.decode() == 'qp':
            tList = getListOfThreads()
            if 'runAP' in tList:
                ###################
                rapCQ.put('qp')
                time.sleep(.001)
                if not rapRQ.empty():
                    cmdQsiz  = rapCQ.qsize()
                    rspQsiz  = rapRQ.qsize()
                    queryRsp = ''
                    #queryRsp = 'RQ Not Empty. sizes = {},{} \n'.format(cmdQsiz,rspQsiz)
                    while not rapRQ.empty():
                        queryRsp += rapRQ.get(block=False)
                    print(' Read = {}'.format(queryRsp))
                else:
                    cmdQsiz  = rapCQ.qsize()
                    rspQsiz  = rapRQ.qsize()
                    queryRsp = 'RQ Empty. Sizes = {},{}'.format(cmdQsiz,rspQsiz)
                    ###################
            else:
                queryRsp = ' runAP thread not running, so can\'t be queried'
            clientSocket.send(queryRsp.encode()) # sends all even if >1024.
            print(' {}'.format(queryRsp))

        elif data.decode() == 'sp':
            tList = getListOfThreads()
            if 'runAP' not in tList:
                stopRsp = ' runAP thread not running, so can\'t be stopped.'
            else:
                rapCQ.put('sp')
                stopRsp = ' runAP thread stopped'
            clientSocket.send(stopRsp.encode()) # sends all even if >1024.
            print(' {}'.format(stopRsp))

        else:
            response = sp.sprinkler(data.decode())
            clientSocket.send(response.encode())

    clientSocket.close()
#############################################################################

def startServer():
    ''' Starts the server and listens for incoming connections.
        Creates a socket object and binds it to a specified host and port.
        When a client connects, it creates a new thread to handle that client
        using the handleClient function. This thread is started by 'main'.
    '''

    host = '0.0.0.0'  # Listen on all available interfaces
    port = 5000

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((host, port))
    serverSocket.listen(5)

    # Putting these here will make all clients use the same rap queues.
    rapCmdQ = queue.Queue()
    rapRspQ = queue.Queue()

    sndBufSize = serverSocket.getsockopt(\
        socket.SOL_SOCKET, socket.SO_SNDBUF)
    rcvBufSize = serverSocket.getsockopt(\
        socket.SOL_SOCKET, socket.SO_RCVBUF)
    print('sndBufSize',sndBufSize) # 64K
    print('rcvBufSize',rcvBufSize) # 64K

    print('Server listening on: {} {}'.format(host, port))

    while True:
        clientSocket, clientAddress = serverSocket.accept()
        # Create a new thread to handle the client
        print('Starting a new client handler thread.')
        cThrd = threading.Thread( target=handleClient,
                                  args=( clientSocket,
                                         clientAddress,
                                         rapCmdQ,rapRspQ),
                                  name = 'handleClient'
                                )
        cThrd.start()
#############################################################################

if __name__ == '__main__':
    thread = threading.Thread(target=listThreads, name = 'listThreads')
    thread.start()
    startServer()
