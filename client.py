import socket
import time
import select
#############################################################################


if __name__ == '__main__':

    # Each client will connect to the server with a new address.
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Replace with the server's address if needed.
    client_socket.connect(('localhost', 5000))

    while True:

        time.sleep(1)

        try:
            message = input("Enter something: ")
            client_socket.send(message.encode())
        except BlockingIOError:
            pass

        readyToRead, _, _ = select.select([client_socket], [], [], 1)
        if readyToRead:
            response = client_socket.recv(1024)
            print('1 Response from server:\n{}'.format(response.decode()))

        if message == 'close':
            break

    client_socket.close()
