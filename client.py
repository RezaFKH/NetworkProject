# Client side
import socket
import threading
import tkinter
from tkinter import DISABLED, END, VERTICAL, NORMAL


# Define socket constant
ENCODER = 'utf-8'
BYTESIZE = 1024
TCP = socket.SOCK_STREAM
IPV4 = socket.AF_INET
global client_socket
global index_listbox 
index_listbox = 0
# Define fonts and colors
my_font = ("SimSun", 12)
black = "#010101"
light_green = "#1fc742"


# Define window
root = tkinter.Tk()
root.title("Chat Client")
root.geometry("500x500")
root.resizable(0, 0)
root.config(bg=black)

# Define functions

def insert_listbox(message):
    global index_listbox
    my_listbox.insert(index_listbox , message)
    index_listbox = index_listbox + 1

def clear_listbox():
    global index_listbox
    my_listbox.delete(0 , END)
    index_listbox = 0


def str_2_utf(message):
    return message.encode(ENCODER)


def utf_2_str(messege):
    return messege.decode(ENCODER)


def connect():
    """ connect to a server at a given  ip/port address """
    global client_socket

    # clear all previous chat
    clear_listbox()

    # get required connection information
    name = name_entry.get()
    ip = ip_entry.get()
    port = port_entry.get()

    # connect if all three are filled in
    if name and ip and port:
        # create tcp socket
        client_socket = socket.socket(IPV4, TCP)
        client_socket.connect((ip, int(port)))

        # verify connection is valid
        verify_connection(name)
    else:
        insert_listbox("insufficiant information for connection ...")


def verify_connection(name):
    """verify that a server connection is valid and pass required information"""
    global client_socket
    # The server will send a NAME flag if a valid connection is made
    flag = utf_2_str(client_socket.recv(BYTESIZE))
    if flag == "NAME":
        # check server requested NAME
        client_socket.send(str_2_utf(name))
        message = utf_2_str(client_socket.recv(BYTESIZE))

        if message:
            # server sent a message you have joint so connection is valid
            insert_listbox(message)

            # change button connect state
            connect_button.config(state=DISABLED)
            disconnect_button.config(state=NORMAL)
            send_button.config(state=NORMAL)

            name_entry.config(state=DISABLED)
            ip_entry.config(state=DISABLED)
            port_entry.config(state=DISABLED)

            # create thread to continiously recieve messages from server so with thread many client can run
            recieve_thread = threading.Thread(target=recieve_message)
            recieve_thread.start()
        else:
            # no vertification message recieved
            insert_listbox("connection not verified\n")
            client_socket.close()
    else:
        # no vertification message recieved
        insert_listbox("connection refused bye ...\n")
        client_socket.close()


def disconnect():
    """ disconnect from server"""
    global client_socket

    client_socket.close()

    # change button connect state
    connect_button.config(state=NORMAL)
    disconnect_button.config(state=DISABLED)
    send_button.config(state=DISABLED)

    name_entry.config(state=NORMAL)
    ip_entry.config(state=NORMAL)
    port_entry.config(state=NORMAL)


def send_message():
    """ send a message to server to be broadcast"""
    global client_socket

    # send message to the server
    message = input_entry.get()
    client_socket.send(str_2_utf(message))
    input_entry.delete(0, END)


def recieve_message():
    """ recieve an incoming message from server """
    global client_socket

    # handle client thread messages
    while True:
        try:
            message = utf_2_str(client_socket.recv(BYTESIZE))
            insert_listbox(f"{message}")
        except:
            # an error occured disconnect from server
            insert_listbox("closing the connection goodbye")
            disconnect()
            break


# Define GUI layout
info_frame = tkinter.Frame(root, bg=black)
output_frame = tkinter.Frame(root, bg=black)
input_frame = tkinter.Frame(root, bg=black)
info_frame.pack()
output_frame.pack(pady=10)
input_frame.pack()


# Info frame Layout
name_lable = tkinter.Label(
    info_frame, text="Hello :", font=my_font, fg=light_green, bg=black)
name_entry = tkinter.Entry(info_frame, borderwidth=3, font=my_font)

ip_lable = tkinter.Label(info_frame, text="Host Ip:",
                         font=my_font, fg=light_green, bg=black)
ip_entry = tkinter.Entry(info_frame, borderwidth=3, font=my_font)

port_lable = tkinter.Label(info_frame, text="Port Num:",
                           font=my_font, fg=light_green, bg=black)
port_entry = tkinter.Entry(info_frame, borderwidth=3, font=my_font, width=10)

connect_button = tkinter.Button(
    info_frame, text="Connect", font=my_font, bg=light_green, borderwidth=5, width=10, command=connect)
disconnect_button = tkinter.Button(
    info_frame, text="Bye", font=my_font, bg=light_green, borderwidth=5, width=10, state=DISABLED, command=disconnect)

name_lable.grid(row=0, column=0, padx=2, pady=10)
name_entry.grid(row=0, column=1, padx=2, pady=10)
name_entry.insert(1, string="bob")

port_lable.grid(row=0, column=2, padx=2, pady=10)
port_entry.grid(row=0, column=3, padx=2, pady=10)
port_entry.insert(1, 15000)   # server port

ip_lable.grid(row=1, column=0, padx=2, pady=10)
ip_entry.grid(row=1, column=1, padx=2, pady=10)
ip_entry.insert(1, string=socket.gethostbyname(socket.gethostname()))  # default my local ip

connect_button.grid(row=1, column=2, padx=4, pady=5)
disconnect_button.grid(row=1, column=3, padx=4, pady=5)

# output frame Layout
my_scrollbar = tkinter.Scrollbar(output_frame, orient=VERTICAL)
my_listbox = tkinter.Listbox(output_frame, height=20, width=55,
                             borderwidth=3, bg=black, fg=light_green, font=my_font, yscrollcommand=my_scrollbar.set)
my_scrollbar.config(command=my_listbox.yview)
my_listbox.grid(row=0, column=0)
my_scrollbar.grid(row=0, column=1, sticky="NS")

# input frame layout
input_entry = tkinter.Entry(input_frame, width=45, borderwidth=3, font=my_font)
send_button = tkinter.Button(input_frame, text="Send", borderwidth=5,
                             width=10, font=my_font, bg=light_green, state=DISABLED, command=send_message)
input_entry.grid(row=0, column=0, padx=5, pady=3)
send_button.grid(row=0, column=1, padx=5, pady=3)

# start window
root.mainloop()
