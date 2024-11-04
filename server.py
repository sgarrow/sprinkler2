import socket     # For creating and managing sockets.
import threading  # For handling multiple clients concurrently.
import time
import sprinkler as sp
#############################################################################

def listThreads():
    while True:
        time.sleep(30)
        for thread in threading.enumerate():
            print(thread.name)
#############################################################################


def handleClient(clientSocket, clientAddress):
    ''' Each client handler is it's own thread.  Multiple instantiations of
        client handler threads may be active simultaneously.  These threads
        are started by the thread running "startServer". Each thread handles
        com with a single client.  Receives data from the client, processes
        it, and sends a response back.
    '''

    print('Accepted connection from: {}'.format(clientAddress))

    while True:
        data = clientSocket.recv(1024)

        # Below if not needed.  clientSocket.recv blocks by default.
        #if not data: break

        print('Received from: {} {}'.format(clientAddress, data.decode()))

        # Process data and send response back to the client
        if data.decode() == 'close':
            response = 'Closing connection'
            clientSocket.send(response.encode())
            print('Closing: {}'.format(clientAddress))
            time.sleep(1)
            break # Causes the handler to stop and the thread end. 
        else:
            response = sp.sprinkler(data.decode())
            print('response len = ', len(response.encode()))
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
        thread = threading.Thread( target=handleClient,
                                   args=( clientSocket,
                                          clientAddress)
                                  )
        thread.start()
#############################################################################

if __name__ == '__main__':
    thread = threading.Thread(target=listThreads)
    thread.start()
    #thread = threading.Thread(target=sprinkler)
    #thread.start()
    startServer()
