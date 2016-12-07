import sys
import socket
import select


def basic_client():
    if(len(sys.argv) < 4):
        print 'Usage : python chat_client.py username hostname port'
        sys.exit()
    name = sys.argv[1]
    host = sys.argv[2]
    port = int(sys.argv[3])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((host, port))
        s.send(name)
    except:
        print 'Uable to connect'
        sys.exit()
    
    print 'Connected to remote host. You can start sending messages'
    sys.stdout.write('[Me] '); sys.stdout.flush()
    while 1:
        socket_list = [sys.stdin, s]
        ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [])

        for sock in ready_to_read:
            if sock == s:
                data = sock.recv(4096)
                if not data:
                    print '\nDisconnected from chat server.'
                    sys.exit()
                else:
                    sys.stdout.write(data)
                    sys.stdout.write('[Me] '); sys.stdout.flush()
            else:
                msg = sys.stdin.readline()
                s.send(msg)
                sys.stdout.write('[Me] '); sys.stdout.flush() 

if __name__ == "__main__":
    sys.exit(basic_client())
