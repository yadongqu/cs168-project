import sys
import socket
import select

HOST = '' 
SOCKET_LIST = []
RECV_BUFFER = 4096
CHANNELS = {}
NAMES = {}

def chat_server(port):

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, port))
    server_socket.listen(10)
 
    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)

 
    print "Chat server started on port " + str(port)
 
    while 1:

        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
      
        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket: 
                sockfd, addr = server_socket.accept()

                SOCKET_LIST.append(sockfd)

                # Get client Name
                name = sockfd.recv(1024)
                NAMES[sockfd] = name
                print "Client %s connected" % NAMES[sockfd]
                 
                broadcast(server_socket, sockfd, "%s entered our chatting room\n" % NAMES[sockfd])
             
            # a message from a client, not a new connection
            else:
                # process data recieved from client, 
                try:
                    # receiving data from the socket.
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        # there is something in the socket
                        message = ''
                        if data.split(' ')[0] == '/create':
                            
                            if len(data.split(' ')[1].rstrip()) > 5:

                                message += NAMES[sock] + 'created a channel ' + data.split(' ')[1]
                                CHANNELS[data.split(' ')[1].rstrip()] = []
                            else:
                                sock.send("wrong command\n")
                        elif data.split(' ')[0] == '/join':
                            if data.split(' ')[1].rstrip() in CHANNELS:
                                message += NAMES[sock] + 'joined channel ' + data.split(' ')[1]
                                for c in CHANNELS:
                                    if sock in CHANNELS[c]:
                                        if c == data.split(' ')[1].rstrip():
                                            sock.send("You already in this channel\n")
                                        else:
                                            CHANNELS[c].remove(sock)
                                CHANNELS[data.split(' ')[1].rstrip()].append(sock)
                            else:
                                sock.send("channel does not exist\n")
                        elif data.rstrip() == '/list':
                            if len(CHANNELS) == 0:
                                message += "there is no channel right now, you can create one with /create [channelname]"
                            else:
                                message += '\n'
                                for c in CHANNELS:
                                    message += c + '\n'
                            sock.send(message)
                        else:
                            message += '\r[' + NAMES[sock] + '] ' + data
                            channel_sockets = []
                            for c in CHANNELS:
                                if sock in CHANNELS[c]:
                                    channel_sockets = CHANNELS[c]
                            if len(channel_sockets) > 0:
                                broadcast(server_socket, sock, message, channel_sockets)
                            else:
                                broadcast(server_socket, sock, message)
                        

                          
                    else:
                        # remove the socket that's broken    
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)

                        # at this stage, no data means probably the connection has been broken
                        broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr) 

                # exception 
                except:
                    broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)
                    continue

    server_socket.close()
    
# broadcast chat messages to all connected clients
def broadcast (server_socket, sock, message, socket_list=SOCKET_LIST):
    for socket in socket_list:
        # send the message only to peer
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)



if __name__ == "__main__":

    sys.exit(chat_server(int(sys.argv[1])))   