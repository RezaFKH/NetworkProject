import threading
import socket
import re
HOST_IP = socket.gethostbyname(socket.gethostname())
HOST_PORT = 15000
ENCODER = 'utf-8'
BYTESIZE = 1024
TCP = socket.SOCK_STREAM
IPV4 = socket.AF_INET


def str_2_utf(message):
    return message.encode(ENCODER)


def utf_2_str(messege):
    return messege.decode(ENCODER)


server_socket = socket.socket(IPV4, TCP)
server_socket.bind((HOST_IP, HOST_PORT))
server_socket.listen()

client_socket_list = []
client_name_list = []


def send_private(client_socket, message):
    """ send a message to a specific client connected to server """
    client_socket.send(message)


def broadcast_message(message):
    """ send a message to all clients connected to server """
    for client_socket in client_socket_list:
        client_socket.send(message)


def recieve_message(client_socket):
    """ recieve an incoming message from a specific client and forward the message to be broadcast  """
    while True:
        try:
            index = client_socket_list.index(client_socket)
            name = client_name_list[index]
            # each created thread will wait here to recieve message
            message = utf_2_str(client_socket.recv(BYTESIZE))

            # client request list of online users
            if message == "Please send the list of attendees.":
                message = ""
                send_private(client_socket, str_2_utf(
                    "Here is the list of attendees:\n"))
                for i in client_name_list:
                    message += f"{i} ,"
                send_private(client_socket, str_2_utf(message))

            # client send public message
            if message.split(',')[0] == "Public message":
                length = re.findall(r'\d+', message)[0]
                message = client_socket.recv(BYTESIZE)
                broadcast_message(
                    str_2_utf(f"Public message from {name},length={length}:"))
                broadcast_message(message)

            # client send private message
            elif message.split(',')[0] == "Private message":
                length = re.findall(r'\d+', message)[0]
                selected_clients = message.split("to")[1].replace(":","")
                selected_clients = selected_clients.split(',')
                selected_clients = list(map(lambda a:a.strip() , selected_clients))
                if all(list(map(lambda a : a in client_name_list , selected_clients))):       
                    message = client_socket.recv(BYTESIZE)
                    clients_concat = ""
                    for cc in selected_clients:
                        clients_concat += f"{cc},"
                    for c in selected_clients:
                        index = client_name_list.index(c)
                        client = client_socket_list[index]
                        send_private(
                            client, str_2_utf(f"Public message, length={length} from {name} to {clients_concat}:"))
                        send_private(client, message)
                else:
                    send_private(client_socket,str_2_utf("username didn't match"))



            else:
                message = f"({name}): {message}"
                broadcast_message(str_2_utf(message))

        except:
            index = client_socket_list.index(client_socket)
            name = client_name_list[index]

            client_socket_list.remove(client_socket)
            client_name_list.remove(name)

            client_socket.close()

            broadcast_message(str_2_utf(f'({name}) has left the chat\n'))


def connect_client():
    """ connect an incoming client to server """
    while True:
        # main thread or main program will loop this forever
        client_socket, client_address = server_socket.accept()
        print(f"connected with {client_address}...")
        send_private(client_socket, str_2_utf("NAME"))
        client_name = utf_2_str(client_socket.recv(BYTESIZE))

        if not client_name in client_name_list:
            client_socket_list.append(client_socket)
            client_name_list.append(client_name)

            send_private(client_socket, str_2_utf(
                f"Hi {client_name},welcome to the chat room\n"))

            broadcast_message(
                str_2_utf(f"{client_name} join the chat room.\n"))

            # a thread for every client (with diffrent client_socket as args)
            recieve_thread = threading.Thread(
                target=recieve_message, args=(client_socket, ))
            recieve_thread.start()
        else:
            client_socket.close()


connect_client()
