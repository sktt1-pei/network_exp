import socket
import _thread
import json
import _socket

log_in_file = 'usr.json'  # 储存字典： 用户名对应密码
buffer_file = 'buffer.json'  # 储存字典： 用户名对应离线时接收到的聊天消息

class Server:
    HOST = ''
    PORT = '50007'  # remain to be set
    conn = []
    addr = []
    online_user = {}  # 在线用户和其对应socket类的字典
    buffer_data = {}  # 用户未登录时接收到的消息，字典中key值是用户名，每个用户对应的value
                      # 都是字符串组，每个字符串都是一条消息
    user_dictionary = {}
    quit_signal = 1  # 服务器退出时，该变量被置为0，用于多个线程间的协调

    def __init__(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.HOST, self.PORT))
        s.listen(20)
        connect_number = 0
        try:  # 读取用户名密码信息
            f = open(log_in_file, 'r')
            self.user_dictionary = json.load(f)
        except FileNotFoundError:
            f = open(log_in_file, 'w')  # 若未找到该文件，则创建该文件
        try:  # 读取用户缓存的未接收到的消息信息
            buffer_f = open(buffer_file, 'r')
            self.buffer_data = json.load(buffer_f)
        except FileNotFoundError:
            buffer_f = open(buffer_file, 'w')  # 若未找到该文件，则创建该文件
        f.close()
        buffer_f.close()
        _thread.start_new_thread(self.get_quit_signal, ('control_thread',))
        # 此线程用于在用户输入q时,将self.quit_signal置为0，使下方循环退出
        while self.quit_signal:
            self.conn[connect_number], self.addr[connect_number] = s.accept()
            print('用户{}建立连接'.format(str(connect_number)))
            try:
                _thread.start_new_thread(self.log_in, (str(connect_number),
                                                       self.conn[
                                                           connect_number],
                                                       self.addr[
                                                           connect_number]))
            except:
                print("创建用户线程出错!")
            connect_number += 1
        try:  # 存储用户名密码信息
            f = open(log_in_file, 'w')
            json.dump(self.user_dictionary,f)
            f.close()
        except:
            print('用户信息存储失败！')
        try:  # 存储用户缓存的未接收到的消息信息
            buffer_f = open(buffer_file, 'w')
            json.dump(self.buffer_data,buffer_f)
            buffer_f.close()
        except:
            print('聊天缓存存储失败！')
        print('服务器已经退出')

    def log_in(self, threadName: str, conn: socket.socket, addr):
        """
        处理登录和注册信息，登录成功后进入chatting_thread函数，否则一直循环
        """
        fail_times = 0  # 用户输入错误密码的次数
        while self.quit_signal:
            log_in_data = conn.recv(512).decode('utf-8')
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
                    if user_name in self.user_dictionary.keys():
                        if self.user_dictionary[user_name] == password:
                            # 验证成功，创建聊天线程
                            conn.sendall('0'.encode('utf-8'))  # 登录成功
                            self.online_user[user_name] = conn
                            self.chatting_thread(conn, user_name)
                            # 登录成功后，从上方进入chatting_thread聊天程序
                            return  # chatting_thread结束后，函数退出
                    conn.sendall('1'.encode('utf-8'))  # wrong password
                    fail_times += 1
            elif log_in_data[:7] == 'signin:':  # 注册
                log_in_data += '*'  # 补充了'*'
                i = 7
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
                    if user_name in self.user_dictionary.keys():
                        conn.sendall('3'.encode('utf-8'))
                    else:
                        self.user_dictionary[user_name] = password
                        self.buffer_data[user_name] = []
                        conn.sendall('2'.encode('utf-8'))

    def chatting_thread(self, conn: socket.socket, user_name: str):
        """
        此函数在log_in函数中被调用，用来管理用户聊天信息的收发
        """
        if self.buffer_data[user_name]:
            # 当buffer_data[user_name]非空的时候，说明
            # 该用户有离线未接收的消息，将其提取出来并发送给用户
            for j in range(len(self.buffer_data[user_name])):
                conn.sendall(self.buffer_data[user_name][j].encode('utf-8'))
        while self.quit_signal:
            # 开始从socket接受并处理
            recv_data = conn.recv(1024).decode('utf-8')
            self.chatting_data(recv_data, user_name, conn)

    def chatting_data(self, recv_data: str, user_name: str,
                      conn: socket.socket):
        # 对接收到的数据进行处理
        if recv_data:  # 检查是否非空
            if recv_data[0:4] == '<To:':  # 提取出消息要发送的对象
                msg_to = ''  # 消息接收方的user_name
                i = 4
                while recv_data[i] != ' ':
                    msg_to += recv_data[i]
                    i += 1
                i += 1
                if recv_data[i:i + 4] == 'Msg:':  # 提取出消息内容
                    msg_receive = ''  # 消息内容
                    i += 4
                    while recv_data[i] != '>':
                        msg_receive += recv_data[i]
                    if msg_to in self.online_user.keys():
                        # 如果用户在线，直接发送消息
                        self.online_user[msg_to].sendall(("<From:" + user_name
                                                          + " Msg:" + msg_receive +
                                                          '>').encode('utf-8'))
                    elif msg_to in self.user_dictionary.keys():
                        # 如果用户不在线，但是在已经注册的用户中，将其保存在缓存中
                        self.buffer_data[msg_to].append("<From:" + user_name
                                                        + " Msg:" + msg_receive +
                                                        '>')
                    else:
                        # 用户不存在
                        conn.sendall("<The user {} doesn't exist>"
                                     .format(msg_to).encode('utf-8'))
                    if recv_data[i + 1:]:
                        # 递归调用函数，当从socket中接收到的信息中带有多条用户消息时
                        # 需要检查是否已经将这条消息中的所有用户消息遍历完
                        self.chatting_data(recv_data[i + 1:], user_name, conn)
            if recv_data[0:4] == 'quit':
                # 用户退出登录
                self.online_user.pop(user_name)
                conn.shutdown(_socket.SHUT_RDWR)
                return

    def get_quit_signal(self, threadName):
        """
        当用户输入q时，将self.quit_signal置为0
        """
        quit_char = 'a'  # 随意给一个初始值
        while quit_char != 'q':
            quit_char = input('需要退出的时候，在键盘上按下q键')
        self.quit_signal = 0
        return
