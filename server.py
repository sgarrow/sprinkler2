import socket     # For creating and managing sockets.
import threading  # For handling multiple clients concurrently.
import time
#############################################################################

def listThreads():
    while True:
        time.sleep(3)
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
        print('**********', data.decode())
        if data.decode() == 'close':
            response = 'Closing connection'
            clientSocket.send(response.encode())
            print('Closing: {}'.format(clientAddress))
            time.sleep(1)
            break # Causes the handler to stop and the thread end. 
        else:
            response = sprinkler(data.decode())
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

def sprinkler(choice):
    strToDict = { 'dm' :{ 'parm':[1], 'menu':' Disp Msg  '},
                  'il' :{ 'parm':[2], 'menu':' Inf  Loop '}}
    #strToDict = { 'dm' :{'func':dispMsg, 'parm':[1], 'menu':' Disp Msg  '},
    #              'il' :{'func':infLoop, 'parm':[2], 'menu':' Inf  Loop '}}
    
    while True:

        if choice == 'm':
            rspStr = ''
            for k,v in strToDict.items():
                print(' {:4} - {}'.format(k, v['menu'] ))
                rspStr += ' {:4} - {}\n'.format(k, v['menu'] )
            return rspStr
    
        elif choice == 'q':
            break
    
    print('\n Exiting sprinkler thread. \n')
#############################################################################

if __name__ == '__main__':
    thread = threading.Thread(target=listThreads)
    thread.start()
    #thread = threading.Thread(target=sprinkler)
    #thread.start()
    startServer()
