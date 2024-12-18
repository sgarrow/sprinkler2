'''
This file contains three functions.

Function startServer:
Starts the server and listens for incoming connections. Creates a socket
object and binds it to a specified host and port.  When a client connects,
it creates a new thread to handle that client using the handleClient
function.  It is called automatically when "python3 server.py" is entered
on the RPi command line.  Start server is an infinite loop that waits for
clients to connect to it.  When a client connects startDerver spawns a new
thread to handle that client.

Function handleClient:
Each client handler is it's own thread.  Multiple instantiations of client
handler threads may be active simultaneously.  These threads are started by
the thread running "startServer". Each thread handles com with a single
client.  Receives data from the client, processes it, and sends a response
back to the client.

A given client can be run on the RPi itself or on another machine via an SSH
connection (like on a PC or on your phone via the Terminus App.

Function listThreads:
This function runs in it's own thread and runs every 60 seconds.  It prints
all the currently running threads in the server's terminal window.  It's
basically just a debug function and could be eliminated.  Similar
functionality is available to he client via the gat (Get Active Threads) cmd.
'''

import socket     # For creating and managing sockets.
import threading  # For handling multiple clients concurrently.
import queue      # For Killing Server.
import time
import sprinkler as sp

openSocketsLst = []
#############################################################################

def listThreads():
    while True:
        time.sleep(30)
        print(' Active Threads: ')
        for t in threading.enumerate():
            print('   {}'.format(t.name))
        print(' ##################')
        print(' Open Sockets: ')
        for openS in openSocketsLst:
            print('   {}'.format(openS['ca']))
        print(' ##################')
#############################################################################

def handleClient(clientSocket, clientAddress, client2ServerCmdQ):
    global openSocketsLst
    print(' Accepted connection from: {}'.format(clientAddress))
    openSocketsLst.append({'cs':clientSocket,'ca':clientAddress})
    clientSocket.settimeout(3.0) # Sets the .recv timeout - ks processing.

    while {'cs':clientSocket,'ca':clientAddress} in openSocketsLst:

        # Recieve a message from the client.
        try:     # User closed client window by (x) instead of by close cmd.
            data = clientSocket.recv(1024)
        except ConnectionResetError: # Windows throws this on (x).
            print(' handleClient {} ConnectRstErr except in s.recv'.format(clientAddress))
            # Breaks the loop. handler/thread stops. Connection closed.
            openSocketsLst.remove({'cs':clientSocket,'ca':clientAddress})
            break
        except socket.timeout:
            #print(' handleClient {} s.timeout except in s.recv'.format(clientAddress))
            continue

        print('*********************************')
        print(' handleClient {} received: {}'.format(clientAddress, data.decode()))
        # Process a "close" message and send response back to the local client.
        if data.decode() == 'close':
            rspStr = ' handleClient {} set loop break RE: close'.format(clientAddress)
            clientSocket.send(rspStr.encode()) # sends all even if >1024.
            time.sleep(1) # Required so .send happens before socket closed.
            print(rspStr)
            # Breaks the loop. handler/thread stops. Connection closed.
            openSocketsLst.remove({'cs':clientSocket,'ca':clientAddress})

        # Process a "ks" message and send response back to the remote client(s).
        elif data.decode() == 'ks':
            # Client sending ks has to be terminated first, I don't know why.
            rspStr = ' handleClient {} set loop break for self RE: ks'.format(clientAddress)
            clientSocket.send(rspStr.encode()) # sends all even if >1024.
            time.sleep(1) # Required so .send happens before socket closed.
            print(rspStr)
            # Breaks ALL remaning client loops. ALL handler/thread stops. ALL Connections closed.
            for el in openSocketsLst:
                if el['ca'] != clientAddress:
                    rspStr = ' handleClient {} set loop break for {} RE: ks'.\
                        format(clientAddress, el['ca'])
                    el['cs'].send(rspStr.encode()) # sends all even if >1024.
                    time.sleep(1) # Required so .send happens before socket closed.
                    print(rspStr)
            openSocketsLst = []
            client2ServerCmdQ.put('ks')

        # Process a "standard" message and send response back to the client.
        else:
            response = sp.sprinkler(data.decode())
            try: # User closed client window by (x) instead of by close cmd.
                clientSocket.send(response.encode())
            except BrokenPipeError:      # RPi throws this on (x).
                print(' handleClient {} BrokePipeErr except in s.send'.format(clientAddress))
                # Breaks the loop. handler/thread stops. Connection closed.
                openSocketsLst.remove({'cs':clientSocket,'ca':clientAddress})

    print(' handleClient {} closing socket and breaking loop'.format(clientAddress))
    clientSocket.close()
#############################################################################

def printSocketInfo(sSocket):
    sndBufSize = sSocket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
    rcvBufSize = sSocket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    print('sndBufSize',sndBufSize) # 64K
    print('rcvBufSize',rcvBufSize) # 64K
#############################################################################

def startServer():
    host = '0.0.0.0'  # Listen on all available interfaces
    port = 

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((host, port))
    serverSocket.listen(5)
    serverSocket.settimeout(3.0) # Sets the .accept timeout - ks processing.

    clientToServerCmdQ = queue.Queue() # So client can tell server to stop.

    thread = threading.Thread( target = listThreads,
                               name   = 'listThreads',
                               daemon = True )
    thread.start()

    printSocketInfo(serverSocket)

    print('Server listening on: {} {}'.format(host, port))
    while True:

        # See if any client has requested the server to halt.
        try:
            cmd = clientToServerCmdQ.get(timeout=.1)
        except queue.Empty:
            pass
        else:
            if cmd == 'ks':
                print('Server breaking in 6 sec.')
                time.sleep(6)
                break


        # See if any new clients are trying to connect.
        try:
            clientSocket, clientAddress = serverSocket.accept()
        except socket.timeout:
            continue
        else:
            # Yes, create a new thread to handle the new client.
            print('Starting a new client handler thread.')

            cThrd = threading.Thread( target=handleClient,

                                      args = ( clientSocket,
                                               clientAddress,
                                               clientToServerCmdQ ),

                                      name =   'handleClient-{}'.\
                                               format(clientAddress) )
            cThrd.start()
    print('Server breaking.')
#############################################################################

if __name__ == '__main__':
    #sp.sprinkler('rp')
    startServer()
