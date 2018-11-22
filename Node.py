import math
from queue import *
from Pipe import *
from Route import *
import re

SRC_NODE=0
FWD_NODE=1
DST_NODE=2


class Node:
    m_is_work=True
    m_x=0
    m_y=0
    m_range=0
    m_name=''
    m_snd_buf=None
    m_rcv_buf=None
    m_connects=None
    m_id=0

    
    def __init__(self, _name, _x, _y, _range):
        self.m_x = _x
        self.m_y = _y
        self.m_range = _range
        self.m_name = _name
        self.m_snd_buf = Queue() 
        self.m_rcv_buf = Queue()

        #next hop dist
        # key = next hop node
        # val = connect to next hop node
        self.m_connects = {}
        self.m_is_work=True
        self.m_id = int(re.search(r'(\d)', _name, re.I).group(0))
        print("name=%s, id=%d, x=%d, y=%d, r=%d"%(self.m_name, self.m_id, self.m_x, self.m_y, self.m_range))
    
    def go_die(self):
        self.m_is_work = False
    
    def get_id(self):
        return self.m_id
    
    def get_pos(self):
        return [self.m_x, self.m_y]
    
    def get_range(self):
        return self.m_range

    def can_touch(self, _node):
        _pos = _node.get_pos()
        _range = _node.get_range()

        #calculate distance
        _dis = int(math.sqrt(pow(abs(_pos[0] - self.m_x), 2) + pow(abs(_pos[1] - self.m_y), 2) ))

        #can touch?
        if _dis <= self.m_range and _dis <= _range:
            return True
        else:
            return False
    #sendmsg
    def send_msg(self, _tar_node, _msg):
        #send msg from snd_buf
        _snd_pipe = self.m_connects[_tar_node].get_snd_pipe(self.m_id)
        _snd_pipe.__send__(_msg)
    
    #recv
    def recv_msg(self, _tar_node):
        #recv msg to rcv_buf
        _rcv_pipe = self.m_connects[_tar_node].get_rcv_pipe(self.m_id)
        return _rcv_pipe.__recv__()

    #load msg to snd_buf
    def load_msgs(self, _msgs):
        for _msg in _msgs:
            self.m_snd_buf.put(_msg)
        
        return len(self.m_snd_buf)

    #add a new connection working as FIB
    def add_connect(self, _connect, _tar_node):
        self.m_connects[_tar_node] = _connect

    def get_connect(self, _tar_node):
        return self.m_connects[_tar_node]
    
    def get_connects(self):
        return self.m_connects
    
    # def main_loop(self, _connect):
