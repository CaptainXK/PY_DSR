import threading
from queue import Queue

class Pipe:
    rw_lock=None
    m_buf=None
    m_msg_nb=0

    def __init__(self): 
        self.rw_lock = threading.RLock()
        self.m_buf = Queue()
        self.m_msg_nb=0

    # put msg onto buf 
    def send(self, _msg):
        with self.rw_lock:
            self.m_buf.put(_msg)
            self.m_msg_nb += 1
        

    # flush
    def send_all(self, _msgs):
        with self.rw_lock:
            for _msg in _msgs:
                self.m_buf.put(_msg)
                self.m_msg_nb += 1
        

    # get msg from buf
    def recv(self):
        _msg = None
        
        with self.rw_lock:
            if not self.m_buf.empty():
                _msg = self.m_buf.get()
        
            self.m_msg_nb -= 1

        return _msg

    # recv all msg from m_buf
    def recv_all(self):
        _msgs = []
        
        with self.rw_lock:
            while not self.m_buf.empty():
                _msg = self.m_buf.get()
                _msgs.append(_msg)
        
            self.m_msg_nb = 0
        

        return _msgs



