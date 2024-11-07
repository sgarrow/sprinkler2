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

def updateSapStateMachineInfo(sapStateMachineInfo, **kwargs):
    sapStateMachineInfo.update(kwargs)
    with open('pickle/sapStateMachineInfo.pickle', 'wb') as handle:
        pickle.dump(sapStateMachineInfo, handle)
    return sapStateMachineInfo
#############################################################################

def getUserInput(q,aLock):
    userInput = None
    while True:

        with open('pickle/sapStateMachineInfo.pickle', 'rb') as handle:
            stateMachInfo = pickle.load(handle)
        if stateMachInfo['sapState'] == 1:
            prompt = stateMachInfo['prompt']
        else:
            prompt = '\n Choice (m=menu, q=quit) -> '

        with aLock:

            if stateMachInfo['sapState'] in [0,1]:
                userInput = input( prompt )

            if stateMachInfo['sapState'] == 1:
                updateSapStateMachineInfo(stateMachInfo,dsrdProfIdx=userInput)

            if stateMachInfo['sapState'] != 0:
                q.put('sap')
            else:
                q.put(userInput)

        time.sleep(.01) # Gives 'main' a chance to run.
        if userInput == 'close':
            break
#############################################################################

if __name__ == '__main__':

    # Each client will connect to the server with a new address.
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Replace with the server's address if needed.
    clientSocket.connect(('localhost', 5000))
    printSocketInfo(clientSocket)
    threadLock  = threading.Lock()
    theQ        = queue.Queue()
    inputThread = threading.Thread( target = getUserInput, args = (theQ,threadLock) )
    inputThread.start()

    while True:

        try:
            message = theQ.get()
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

        if message == 'close':
            break

    clientSocket.close()
