import socket
import time
import select
import pickle
#############################################################################

if __name__ == '__main__':

    # Each client will connect to the server with a new address.
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Replace with the server's address if needed.
    clientSocket.connect(('localhost', 5000))

    sndBufSize = clientSocket.getsockopt(\
        socket.SOL_SOCKET, socket.SO_SNDBUF)
    rcvBufSize = clientSocket.getsockopt(\
        socket.SOL_SOCKET, socket.SO_RCVBUF)
    print('sndBufSize',sndBufSize) # 64K
    print('rcvBufSize',rcvBufSize) # 64K 

    mainPrompt   = '\n Choice (m=menu, q=quit) -> '  
    sap_1_prompt = ' Enter number of desired Active Profile (or \'q\') -> '
    prompt = mainPrompt
    while True:

        time.sleep(.1)

        try:
            message = input( prompt )
            clientSocket.send(message.encode())
        except BlockingIOError:
            pass

        readyToRead, _, _ = select.select([clientSocket], [], [], .5)
        if readyToRead:
            rspStr = ''
            while readyToRead:
                response = clientSocket.recv(1024)
                rspStr += response.decode()
                readyToRead, _, _ = select.select([clientSocket],[],[], .25)
            print('{}'.format(rspStr))

        if message == 'sap':
            with open('sapStateMachineInfo.pickle', 'rb') as handle:
                stateMachInfo = pickle.load(handle)
            sapState    = stateMachInfo[ 'sapState'    ]
            dsrdProfIdx = stateMachInfo[ 'dsrdProfIdx' ]
            if sapState == 1:
                prompt = sap_1_prompt
        else:
            prompt = mainPrompt

        if message == 'close':
            break

    clientSocket.close()
