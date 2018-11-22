import threading
from queue import *
from Route import *

class Pipe:
    rw_lock=None
    m_buf=None

    def __init__(self):
        self.rw_lock = threading.Lock()
        self.m_buf = Queue()
    
    def __send__(self, _msg):
        self.rw_lock.acquire()

        self.m_buf.put(_msg)
        
        self.rw_lock.release()

    def __recv__(self):
        self.rw_lock.acquire()

        _msg = None

        if len(self.m_buf) > 0:
            _msg = self.m_buf.get()
        
        self.rw_lock.release()

        return _msg

