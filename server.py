import socket
import time


def start_server():
    host = '127.0.0.1'
    port = 9998
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creating the tcp socket
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #available to reused this address and port
    server_socket.bind((host, port))  # bind the socket with the port and ip
    server_socket.listen(5) #allow waiting in line
    print(f"Server listening on {host}:{port}")
    max_msg_size = server_reader() # getting the server massage size from the file

    client_socket, address = server_socket.accept() # the server waiting to connection with the client and creating a new socket
    print(f"Connection from {address} has been established.")
    received = []




    while True:
        data = client_socket.recv(1024).decode()    #the server receiving the data

        if not data:
            break

        if data == "GET_MAX_MSG_SIZE": # if the client asx for max size the server send it back
            client_socket.send(max_msg_size.encode())
            continue    #go back to receive

        co=data.count("\n")     #checkes how many segments there is in the same data (in the buffer)
        if co==1:
             seq_num, msg = data.split(":", 1) #spliting the sequence number from the message
             print(f"Received:{seq_num} : {msg[:-1]}")
             seq_num = int(seq_num[1:])  # without the "M"
             ack_hendler(seq_num, received,client_socket) #sent it to ack handler

        elif co>1:  #if there is more than one message in the same data we need to separate it and ack each one
            mod_msg = data.split("\n")
            for i in range(co-1):
                if ":" in mod_msg[i]:
                    seq_num, msg = mod_msg[i].split(":", 1)
                    print(f"Received:{seq_num} : {msg[:-1]}")
                    seq_num = int(seq_num[1:])
                    ack_hendler(seq_num, received, client_socket)

            mod_msg.clear()


    print("Connection closed from the server side.")
    client_socket.close() #closing the sockets
    server_socket.close()

last_ack=-1
ack_hold=[]#global acks list for messages that received not in order
def ack_hendler(seq_num,received, client_socket):#function that handle all ack performance
    global ack_hold #declare global list
    global last_ack
    if seq_num not in received: #means that this is a new message

        received.append(seq_num)
        received.sort()  # make sure that all seq nums in order

        if seq_num != len(received) - 1:  # in that case we received message not in order
            ack_hold.append(seq_num)
            ack_hold = sorted(set(ack_hold))
            if seq_num != last_ack + 1:
                print(f"ACK:{last_ack}")
                client_socket.send(f"ACK:{last_ack}\n".encode())

        if ack_hold and seq_num == ack_hold[0]:#if the server accept a message that is the first in unacknowledged list
            ack_hold.append(seq_num)
            ack_hold = sorted(set(ack_hold))
            while ack_hold and len(received)>ack_hold[0]: #send all acks that received not in order (until the next disorder ack)
                if ack_hold[0] == received[ack_hold[0]]: #make sur that this is the next in order ack
                    next_ack = ack_hold.pop(0)

                    last_ack = next_ack

                else:
                    break
            print(f"ACK:{last_ack}")
            client_socket.send(f"ACK:{last_ack}\n".encode())

        if seq_num == len(received)-1 :  #when the message arrived in order as excepted
            print(f"ACK:{seq_num}")
            client_socket.send(f"ACK:{seq_num}\n".encode())
            last_ack = seq_num
    elif seq_num >= last_ack:   # handling the case that the ack not arrived to the client and the message been sent again
        print(f"ACK:{seq_num}")
        client_socket.send(f"ACK:{seq_num}\n".encode())

    print(f"received: {received}")
    print(f"ack_hold: {ack_hold}\n")
    return


def server_reader(): #reades server information from text or input

    flag=0
    while(flag==0):
        print(f"Choose: \n1. Enter details from file\n2. Enter detail as input")
        choice = input()
        if choice == '1':
            file = input("Enter file name and path: ")
            f=open(file,"r")
            f.readline()
            str=f.readline()
            max_msg_size=str[17:len(str)-1]
            f.close()
            flag=1
        elif choice == '2':
            max_msg_size = input("Enter the max massage size: ")
            flag=1
        else:print(f"Invalid choice")

    print(f"The server max size massage is {max_msg_size}")
    return max_msg_size



if __name__ == "__main__":
    start_server()
