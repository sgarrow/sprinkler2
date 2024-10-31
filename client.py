import socket
import time
import select
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

    while True:

        time.sleep(.1)

        try:
            message = input("Enter something: ")
            clientSocket.send(message.encode())
        except BlockingIOError:
            pass

        readyToRead, _, _ = select.select([clientSocket], [], [], 1)
        if readyToRead:
            rspStr = ''
            while readyToRead:
                response = clientSocket.recv(1024)
                rspStr += response.decode()
                readyToRead, _, _ = select.select([clientSocket],[],[], .25)
            print('{}'.format(rspStr))

        if message == 'close':
            break

    clientSocket.close()
