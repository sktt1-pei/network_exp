import time
import _thread

b = 1

class Shit:
    sig = 1
    def __init__(self):
        self.sig = 1

    def whatisthis(self,threadName):
        while self.sig:
            print(self.sig)
            time.sleep(2)

    def quit_program(self,threadName):
        a = input('if you want to exit,type in a char')
        if a:
            self.sig = 0

a = Shit()
_thread.start_new_thread(a.quit_program,('Thread_0',))
_thread.start_new_thread(a.whatisthis,('Thread_0',))

'''try:
    _thread.start_new_thread(whatisthis,('Thread_1',2))
    _thread.start_new_thread(whatisthis,('Thread_2',3))

except:
    print("fail")'''

while (1):
    pass
