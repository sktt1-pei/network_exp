# Echo client program
import socket
import time
HOST = '192.168.0.107' # server IP address
PORT = 50007 # The same port as used by the server
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send(b'<hello>')
s.send(b'<hello>')
s.send(b'<hello>')
s.send(b'<hello>')
s.send(b'<hello>')
s.send(b'<hello>')
data = s.recv(1024)
print(data)
print('finish')


