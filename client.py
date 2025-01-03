import socket
import math
import time

from server import last_ack


def start_client():
    host = '127.0.0.1'
    port = 9998

    massage, win_size,timout=client_reader() #accepting the input

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates socket with tcp protocol
    client_socket.connect((host, port)) #make the connection
    print(f"Connected to server at {host}:{port}")


    client_socket.send("GET_MAX_MSG_SIZE".encode())  #send a request to max message size
    max_msg_size =int(client_socket.recv(1024).decode()) # get the size

    print(f"Maximum message size is: {max_msg_size} bytes")
    print(f"String len is {len(massage)}")
    seg_part =math.ceil(len(massage)/max_msg_size)  #get the maximum message size
    seg_count = 0
    start = 0
    end = max_msg_size
    full_msg=[]

    print("Building segment chunks")
    for i in range(seg_part):       #builds the array by message size
        if massage[start:end] != "\n":
            full_msg.append(massage[start:end])
            start=end
            end=start+max_msg_size

    start = 1
    end = 0
    unacknowledged = []
    recived_ack = []
    #last_ack=-1
    print(seg_part)
    print(f"Full massage in parts: size:{len(full_msg)} {full_msg}")


    while start<=(len(full_msg)): #run on the packets number
        #sanding the messages
        while end < len(full_msg) and len(unacknowledged) < win_size  : #make sure that the function not steps out from window size
            if len(unacknowledged)>0:
                if unacknowledged[0]+win_size<end:
                    break
            # if end ==0: #bug1        #bug check if  packets not arrived to the server
            #     unacknowledged.append(end)
            #     print(f"Sent: {end}:{full_msg[end]}")
            #     end +=1
            #     continue


            unacknowledged =sorted(set(unacknowledged))
               # set(list(unacknowledged).sort())
            header = "0"* (8-len(str(end))) + str(end)
            client_socket.sendall(f"M{header}:{full_msg[end]}\n".encode()) #sand all massages that available in window
            time.sleep(0.05)
            print(f"Sent: M{header}: {full_msg[end]}")
            unacknowledged.append(end) #add the segment number to the unacknowledged
            end += 1
        try:
            client_socket.settimeout(float(timout)) #set a timer
        except Exception as e:
            print("No need a timer anymore")


        #accepting the ack's
        retry=2
        i=0
        while i < retry: #trying few times to receive
            try:



                i+=1
                ack= client_socket.recv(1024).decode()  #getting the ACK
                co=ack.count("\n")  #somtimes two ACKs comes together in the same buffer so we divided them with \n
                if co==1:   # if single ACK
                    print(f"Received acknowledgment: {ack}")
                    ack_num = int(ack.split(":")[1]) #split the ack for getting the seg number

                   # if ack_num in unacknowledged:   # remove this ack from the unacknowledged ack list
                    counter=0
                    for i in unacknowledged:
                        if i <= ack_num:
                            counter+=1
                           # unacknowledged.remove(i)
                            recived_ack.append(i) # add the ack to the received list
                            start += 1
                            #last_ack=i

                    #print(f"unacknowledged: {unacknowledged}")
                    unacknowledged = unacknowledged[counter:]
                    print(f"unacknowledged: {unacknowledged}")


                elif co>1:  #if few ACKs the same as single just in for loop

                    for i in range(co - 1): #the same as single ack just with another separate by \n
                        mod_ack=ack.split("\n")
                        this_ack , ack_num = mod_ack[i].split(":")
                        ack_num = int(ack_num)
                        print(f"Received acknowledgment: {mod_ack[i]}")
                        counter=0
                        for j in unacknowledged:
                            if j <= ack_num:
                                #unacknowledged.remove(j)
                                counter += 1
                                recived_ack.append(j)  # add the ack to the received list
                                start += 1
                                #last_ack=j
                        print(f"unacknowledged: {unacknowledged}")
                        unacknowledged = unacknowledged[counter:]
                        print(f"unacknowledged: {unacknowledged}")
                        # if ack_num in unacknowledged:
                        #     unacknowledged.remove(ack_num)
                        #     recived_ack.append(ack_num)
                        #     start += 1


            except socket.timeout:  #catch the timer exception

                print("Timout!\n Sending again all package that waiting for acknowledgement")
                for i in unacknowledged : #send again all unacknowledged massages
                    #if last_ack<i:
                        header = "0" * (8 - len(str(i))) + str(i)   #creating the header as fix size with 8 chars
                        client_socket.sendall(f"M{header}:{full_msg[i]}\n".encode())
                        print(f"resand M{header}: {full_msg[i]} ")

        if len(recived_ack) == len(full_msg):
            print("done!!")
            break

    print("Connection closed from the client side.")
    client_socket.close()


def client_reader(): #this function read from file the following arguments: massage, timer and window size
    flag = 0
    while (flag == 0):
        print(f"Choose: \n1. Enter details from file\n2. Enter detail as input")
        choice = input()
        if choice == '1':
            file = input("Enter file name and path: ")
            f = open(file, "r")
            tmp = f.readline()
            massage=tmp[8:len(tmp)]
            f.readline()
            tmp = f.readline()
            win_size = tmp[12:len(tmp)]
            tmp=f.readline()
            timout=tmp[8:len(tmp)]
            f.close()
            flag = 1
        elif choice == '2':
            massage= input("Enter the massage: ")
            win_size= input("Enter the win_size: ")
            timout= input("Enter the timout: ")
            flag = 1

        else:
            print(f"Invalid choice")
    print(f"The massage is: {massage}")
    print(f"The sliding window size is: {win_size}")
    print(f"The timout number is: {timout}")
    return massage, int(win_size),timout

if __name__ == "__main__":
    start_client()
