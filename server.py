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
import time
import sprinkler as sp
#############################################################################
def listThreads():
    while True:
        time.sleep(60)
        print(' Active Threads: ')
        for t in threading.enumerate():
            print('   {}'.format(t.name))
        print(' ##################')
#############################################################################

def handleClient(clientSocket, clientAddress):
    print('Accepted connection from: {}'.format(clientAddress))

    while True:
        try: # In case user closes client by (x) instead if by close cmd.
            data = clientSocket.recv(1024)
        except ConnectionResetError: # Whereas Windows throws this.
            print(' ConnectionResetError exception in clientSocket.send')
            print(' Closing associated client socket.')
            break

        print('*********************************')
        print('Received from: {} {}'.format(clientAddress, data.decode()))

        # Process data and send response back to the client
        if data.decode() == 'close':
            response = 'Closing connection'
            clientSocket.send(response.encode()) # sends all even if >1024.
            print('Closing: {}'.format(clientAddress))
            time.sleep(1)
            break # Causes the handler to stop and the thread end.

        response = sp.sprinkler(data.decode())
        try: # In case user closes client by (x) instead if by close cmd.
            clientSocket.send(response.encode())
        except BrokenPipeError: # RPi throws this.
            print(' BrokenPipeError exception in clientSocket.send')
            print(' Closing associated client socket.')
            break

    clientSocket.close()
#############################################################################

def startServer():
    host = '0.0.0.0'  # Listen on all available interfaces
    port = 

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((host, port))
    serverSocket.listen(5)

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
                                  args = ( clientSocket,
                                           clientAddress ),
                                  name =   'handleClient-{}'.\
                                           format(clientAddress) )
        cThrd.start()
#############################################################################

if __name__ == '__main__':
    thread = threading.Thread(target=listThreads, name = 'listThreads')
    thread.start()
    #sp.sprinkler('rp')
    startServer()
