import socket
s = socket.socket()

port = 60001

s.connect(('138.68.71.51', port))
s.send("Hello server!")

with open('received_file', 'wb') as f:
    print 'file opened'
    while True:
        print('receiving data...')
        data = s.recv(1024)
        print('data=%s', (data))
        if not data:
            break
        f.write(data)

f.close()
print('Successfully get the file')
s.close()
print('connection closed')