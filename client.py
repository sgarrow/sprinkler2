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

def makeSapStateMachineInfo(inDict, idx):
    inDict['dsrdProfIdx'] = idx
    with open('sapStateMachineInfo.pickle', 'wb') as handle:
        pickle.dump(inDict, handle)
    return inDict
#############################################################################

def getUserInput(q,l):
    while True:

        prompt = '\n Choice (m=menu, q=quit) -> '
        with open('sapStateMachineInfo.pickle', 'rb') as handle:
            stateMachInfo = pickle.load(handle)
        if stateMachInfo['sapState'] == 1:
            prompt = stateMachInfo['prompt']

        l.acquire()
        userInput = input( prompt )
        q.put(userInput)
        l.release()
        time.sleep(.01)
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

        threadLock.acquire()
        readyToRead, _, _ = select.select([clientSocket], [], [], .6)
        if readyToRead:
            rspStr = ''
            while readyToRead:
                response = clientSocket.recv(1024)
                rspStr += response.decode()
                readyToRead, _, _ = select.select([clientSocket],[],[], .25)
            print('{}'.format(rspStr))
        threadLock.release()

        if message == 'close':
            break

    clientSocket.close()
