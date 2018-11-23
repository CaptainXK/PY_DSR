import threading
from queue import Queue

class Pipe:
    rw_lock=None
    m_buf=None
    m_msg_nb=0

    def __init__(self): 
        self.rw_lock = threading.Lock()
        self.m_buf = Queue()
        self.m_msg_nb=0

    # try lock 
    def do_lock(self):
        self.rw_lock.acquire()
    
    # try release
    def do_release(self):
        self.rw_lock.release()

    # put msg onto buf 
    def send(self, _msg):
        self.do_lock()

        self.m_buf.put(_msg)

        self.m_msg_nb += 1
        
        self.do_release()

    # flush
    def send_all(self, _msgs):
        self.do_lock()

        for _msg in _msgs:
            self.m_buf.put(_msg)
            self.m_msg_nb += 1
        
        self.do_release()

    # get msg from buf
    def recv(self):
        _msg = None
        
        self.do_lock()

        if not self.m_buf.empty():
            _msg = self.m_buf.get()
        
        self.m_msg_nb -= 1
        
        self.do_release()

        return _msg

    def recv_all(self):
        _msgs = []
        
        self.do_lock()

        while not self.m_buf.empty():
            _msg = self.m_buf.get()
            _msgs.append(_msg)
        
        self.m_msg_nb = 0
        
        self.do_release()

        return _msgs



