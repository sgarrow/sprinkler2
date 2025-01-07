'''
STARTING THE SERVER AND THE CLIENT
==================================
To start the server type "python server.py" on the cmd line.
To connect a client to the server type "python client.py" on the cmd line.

A client can be run on the same machine as the server (in a different command
window) or on a different machine entirely.

INTRODUCTION
============
Servers are things that respond to requests.
Clients are things that make requests.

A WEB browser is a type of client that can connect to servers that "serve"
WEB pages - like the Google server.

When a web browser (a client) connects to the Google Server and sends it a
request (e.g., send me a web page containing a bunch of links related to "I'm
searching this") the Google Server will respond to the request by sending
back a web page.

Requests are sent in "packets" over connections called "sockets".  Included
in the request is the IP address of the client making it - that's how the
server knows where to send the response back to.  A given machine has one IP
address, so if more than one instance of a web browser is open on a single
machine how is it that the response ends up in the "right" web browser and
not the other browser?  Port number.  

CLIENT DETAILS
==============
Every client has a unique (ip,port) tuple.  The server tracks every client by
(ip,port).  The server maintains a list of (ip,port) for all active clients.

Each client has has two unique things associated with it - (1) a socket and
(2) an instance (a thread) running the client's handling function

When a client issues a "close" command its (ip,port) is removed from the list
and as a result the handleClient infinite loop is exited thereby causing its
socket to be closed and its thread to terminate.

When a client issues a "ks" (kill server) not only does that client termine
but all other clients terminate as well.  Futhermore the "ks" command causes
the server itself (it's still waiting for other clients to possibly connect)
to terminate.

SERVER DETAILS
==============
Upon receipt of the ks command the server (1) sends a message to all clients
(including the the one sent the cmd) indicating that the server is shutting
down so that the client will exit gracefully, (2) terminates all clients and
then finally (3) the server exits.

UNEXPECTED EVENT HANDLING
=========================
If a user clicks the red X in the client window (closes the window) that
client unexpectedly (from the server's viewpoint) terminates.  This is in
contrast to the client issuing the close or ks command where the server is
explicitly notified of the client's temination.  An unexpected termination
results in a sort of unattached thread and socket that may continue to exist
even when the server exits.  This situation is rectified by two try/except
blocks in function handleClient.  To are needed because it was empirically
determined the Window and Linux systems seem to block (waiting for a command
from the associated client) in different places.
'''

import socket           # For creating and managing sockets.
import threading        # For handling multiple clients concurrently.
import queue            # For Killing Server.
import time             # For Killing Server and listThreads.
import sprinkler as sp  # Contains vectors to "worker" functions.

openSocketsLst = []     # Needed for processing close and ks commands.
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

    # The while condition is made false by the close and ks command.
    while {'cs':clientSocket,'ca':clientAddress} in openSocketsLst:

        # Recieve msg from the client (and look (try) for UNEXPECTED EVENT).
        try: # In case user closed client window (x) instead of by close cmd.
            data = clientSocket.recv(1024)
        except ConnectionResetError: # Windows throws this on (x).
            print(' handleClient {} ConnectRstErr except in s.recv'.format(clientAddress))
            # Breaks the loop. handler/thread stops. Connection closed.
            openSocketsLst.remove({'cs':clientSocket,'ca':clientAddress})
            break
        except socket.timeout: # Can't block on recv - won't be able to break
            continue           # loop if another client has issued a ks cmd.

        # Getting here means a command has been received.
        print('*********************************')
        print(' handleClient {} received: {}'.format(clientAddress, data.decode()))

        # Process a "close" message and send response back to the local client.
        if data.decode() == 'close':
            rspStr = ' handleClient {} set loop break RE: close'.format(clientAddress)
            clientSocket.send(rspStr.encode()) # sends all even if >1024.
            time.sleep(1) # Required so .send happens before socket closed.
            print(rspStr)
            # Breaks the loop, connection closes and thread stops.
            openSocketsLst.remove({'cs':clientSocket,'ca':clientAddress})

        # Process a "ks" message and send response back to other client(s).
        elif data.decode() == 'ks':
            # Client sending ks has to be terminated first, I don't know why.
            rspStr = ' handleClient {} set loop break for self RE: ks'.format(clientAddress)
            clientSocket.send(rspStr.encode()) # sends all even if > 1024.
            time.sleep(1) # Required so .send happens before socket closed.
            print(rspStr)
            # Breaks the ALL loops, ALL connections close and ALL thread stops.
            for el in openSocketsLst:
                if el['ca'] != clientAddress:
                    rspStr = ' handleClient {} set loop break for {} RE: ks'.\
                        format(clientAddress, el['ca'])
                    el['cs'].send(rspStr.encode()) # sends all even if > 1024.
                    time.sleep(1) # Required so .send happens before socket closed.
                    print(rspStr)
            openSocketsLst = []
            client2ServerCmdQ.put('ks')

        # Process a "standard" msg and send response back to the client,
        # (and look (try) for UNEXPECTED EVENT).
        else:
            response = sp.sprinkler(data.decode())
            try: # In case user closed client window (x) instead of by close cmd.
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

        # See if any client has requested the server to halt (ks command).
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
        except socket.timeout: # Can't block on accept - won't be able to
            continue           # break loop if a client has issued a ks cmd.
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
