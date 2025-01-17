import socket
import select

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP,PORT))
server_socket.listen()

socket_lists = [server_socket]

clients = {}

print(f"Server is running on IP {IP} and listening on {PORT}")

def recieve_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_length = int(message_header.decode('utf-8').strip())

        return {'header': message_header, 'data': client_socket.recv(message_length)}
    
    except:
        return False

while True:
    read_sockets, _, exeption_sockets = select.select(socket_lists, [], socket_lists)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = recieve_message(client_socket)
            if user is False:
                continue

            socket_lists.append(client_socket)
            clients[client_socket] = user
            print("Accepted new connection from {}:{}, username: {}".format(*client_address, user['data'].decode('utf-8')))
        
        else:
            message = recieve_message(notified_socket)

            if message is False:
                print("Closed connection from: {}".format(clients[notified_socket]['data'].decode('utf-8')))

                socket_lists.remove(notified_socket)
                del clients[notified_socket]

                continue

            user = clients[notified_socket]

            print(f"Recieved message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

            for client_socket in clients:

                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])


