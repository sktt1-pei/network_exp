"""
This code initializes the server.
Enable the server to receive TCP package from the client.
"""
# 需要修改的地方:
# 1> 编码方式
# 2> 补充了退出的消息
# 3> recv数据需要重新编码？
# 4> 没有这个用户的时候怎么办
import socket
import _thread
import json
import _socket

log_in_file = 'usr.json'


class Server:
    HOST = ''
    PORT = '50007'  # remain to be set
    conn = []
    addr = []
    online_user = {}    #在线用户
    buffer_data = {}    #未登录用户缓存消息的地方
    user_dictionary = {}
    def __init__(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.HOST, self.PORT))
        s.listen(20)
        connect_number = 0
        while True:
            self.conn[connect_number], self.addr[connect_number] = s.accept()
            # 需要在这里创立聊天线程
            connect_number += 1

    def log_in(self, threadName, conn: socket.socket, addr, connect_number, ):
        # 管理登录和注册
        f = open(log_in_file, 'r')
        self.user_dictionary = json.load(f)
        while(1):           #登录成功后结束循环
            log_in_data = conn.receive(512)
            if log_in_data[:4] == 'usr:':  # 用户登录
                i = 4  # 格式：usr:knight password:123456*
                user_name = ''
                while log_in_data[i] != ' ':
                    user_name += log_in_data[i]
                    i = i + 1
                i = i + 1
                if log_in_data[i:i + 9] == 'password:':
                    i += 9
                    password = ''
                    while log_in_data[i] != '*':
                        password += log_in_data[i]
                        i = i + 1
                    if self.user_dictionary[user_name] == password: #验证成功，创建聊天线程
                        conn.sendall(b'0')  # log in
                        self.online_user[user_name] = conn
                        chatting_thread(conn)
                    else:
                        conn.sendall(b'1')  # wrong password
            elif log_in_data[:7] == 'signin:': #注册
                i = 7
                user_name = ''
                while log_in_data[i] !=' ':
                    user_name += log_in_data[i]
                    i = i + 1
                i = i + 1
                if log_in_data[i:i+9] == 'password:':
                    i += 9
                    password = ''
                    while log_in_data[i] != '*':
                        password += log_in_data[i]
                        i = i + 1
                if user_name in self.user_dictionary.keys():
                    conn.sendall(b'3')
                else:
                    self.user_dictionary[user_name] = password
                    self.buffer_data[user_name] = []
                    conn.sendall(b'2')

    def chatting_data(self,recv_data:str,user_name : str,conn : socket.socket):
        # 处理聊天信息
        if recv_data:
            if recv_data[0:4] == '<To:':
                msg_to = ''
                i = 4
                while recv_data[i] != ' ':
                    msg_to += recv_data[i]
                    i += 1
                i += 1
                if recv_data[i:i+4] == 'Msg:':
                    msg_receive = ''
                    i += 4
                    while recv_data[i] != '>':
                        msg_receive += recv_data[i]
                    if msg_to in self.online_user.keys():
                        self.online_user[msg_to].sendall("<From:" + user_name
                                                         +" Msg:" +msg_receive+
                                                         '>')
                    elif msg_to in self.user_dictionary.keys():
                        self.buffer_data[msg_to].append("<From:" + user_name
                                                         +" Msg:" +msg_receive+
                                                         '>')


                    else: #没有这个用户
            if recv_data[0:4] == 'quit':
                self.online_user.pop(user_name)
                conn.shutdown(_socket.SHUT_RDWR)
                return 0

