import math
from queue import Queue
from Pipe import Pipe
from Route import Connect, Msg, Route_path
import re
import threading
import datetime

gl_node_type={'SRC':0, 'FWD':1, 'DST':2}

class Node:
    m_is_work=True # node is available or not
    m_is_run=True # node threading is running or not
    m_x=0
    m_y=0
    m_range=0
    m_name=''
    m_snd_buf=None
    m_rsnd_buf=None
    # m_rcv_buf=None
    m_connects=None
    m_id=0
    m_point_sz=5
    m_type=0
    m_route=None #fwd route for src node
    m_node_thd=None


    def __init__(self, _name, _x, _y, _range):
        self.m_x = _x
        self.m_y = _y
        self.m_range = _range
        self.m_name = _name
        self.m_snd_buf = Queue() 
        self.m_rsnd_buf = Queue() 
        # self.m_rcv_buf = Queue()

        #next hop dist
        # key = next hop node
        # val = connect to next hop node
        self.m_connects = {}

        self.m_is_work=True
        self.m_is_run=True
        self.m_id = int(re.search(r'([\d]+)', _name, re.I).group(0))
        self.m_point_sz=5
        print("name=%s, id=%d, x=%d, y=%d, r=%d"%(self.m_name, self.m_id, self.m_x, self.m_y, self.m_range))
        self.m_type=0

        #route dist
        # key = dst node
        # val = route info
        self.m_route={}

        # init threading object for working loop 
        self.m_node_thd=None

    #get node's id    
    def get_id(self):
        return self.m_id

    #get node's name
    def get_name(self):
        return self.m_name
    
    #get node's pos
    def get_pos(self):
        return [self.m_x, self.m_y]
    
    #get communication range
    def get_range(self):
        return self.m_range
    
    #check if current node can communicate with the given node 
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
    
    #delete a connect
    def del_connect(self, _tar_node):
        del self.m_connects[_tar_node]

    #get one connect
    def get_connect(self, _tar_node):
        return self.m_connects[_tar_node]
    
    #get all connects
    def get_connects(self):
        return self.m_connects

    #add or modify a route
    def set_route(self, _route, _dst_node):
        self.m_route[_dst_node] = _route

    #get route
    def get_route(self):
        return self.m_route

    #check if node is on working
    def is_work(self):
        return self.m_is_work

    #just go die    
    def go_die(self):
        self.m_is_work = False
        self.stop_node()

    #check if node is on runing
    def is_run(self):
        return self.m_is_run

    #stop running
    def start_node(self):
        self.m_is_run = True
    
    #stop running
    def stop_node(self):
        if self.is_run():
            print("%s stop running"%(self.get_name()))
            self.m_is_run = False

    #check if the given pos(_x, _y) is on node
    def under_cover(self, _x, _y):
        _dis = math.sqrt((pow(abs(_x - self.m_x), 2) + pow(abs(_y - self.m_y), 2)) )
        _dis = int(_dis)

        if _dis <= self.m_point_sz:
            return True
        else:
            return False
    
    # lunch a node
    def node_lunch(self, _type, _map):
        global gl_node_type
        self.m_type = gl_node_type[_type]

        # init threading
        if self.m_type == gl_node_type['SRC']:
            #send node
            print("%s is sender"%(self.get_name()))
            self.m_node_thd = threading.Thread(target=Node.snd_loop, args=(self, _map) )

        elif self.m_type == gl_node_type['FWD']:
            #forward node
            print("%s is forwarder"%(self.get_name()))
            self.m_node_thd = threading.Thread(target=Node.fwd_loop, args=(self, _map) )

        else:
            #receive node
            print("%s is receiver"%(self.get_name()))
            self.m_node_thd = threading.Thread(target=Node.rcv_loop, args=(self, _map) )

        #start to work    
        self.start_node()
        self.m_node_thd.start()

    # sender loop
    def snd_loop(self, _map):
        # send one msg every 3 seconds
        pre_time = datetime.datetime.now()
        cur_time = 0
        msg_idx = 0

        while self.is_run() and self.is_work():
            
            # if map is in rebuild, keep waiting
            while _map.is_in_rebuild():
                continue
        
            # update cur_time
            cur_time = datetime.datetime.now()

            #check if it is time to send
            if (cur_time - pre_time).seconds < 3:
                # keep wait
                continue
            else:
                # it is time
                # update pre_time and do send
                pre_time = cur_time
                
            # new a empty msg
            _msg_to_snd = Msg()

            # got dst_node
            _dst_node = _map.get_global_dst()

            # got route path info to dst node
            _route_to_dst = self.m_route[_dst_node]

            # find next hop on current route
            _next_hop_node = _route_to_dst.find_next_hop(self)

            # find connect to next hop node
            _next_hop_con = self.get_connect(_next_hop_node)

            # find snd pipe to next hop node
            _snd_pipe = _next_hop_con.get_snd_pipe(self.get_id())

            # fill test content
            _msg_to_snd.fill_content("I\'ve got you in my sight")

            # fill route info
            _msg_to_snd.set_route_info(_route_to_dst)

            # set id
            _msg_to_snd.set_id(msg_idx)
            msg_idx += 1

            # do snd
            _map.get_draw().mod_point(self.m_x, self.m_y, _col='yellow')
            _snd_pipe.send(_msg_to_snd)
            _map.get_draw().mod_point(self.m_x, self.m_y)
            print("sender %s: Send %d:\"%s\" to %s"%(self.get_name(), _msg_to_snd.get_id(), _msg_to_snd.get_content(), _next_hop_node.get_name() ) )

    # forwarder loop
    def fwd_loop(self, _map):
        while self.is_run() and self.is_work():
            
            # if map is in rebuild, keep waiting
            while _map.is_in_rebuild():
                continue
            
            # poll all connects to rcv
            for (_pre_node, _connect) in self.m_connects.items():
                if _pre_node.is_work():
                    #debug
                    # print("%s poll %s"%(self.get_name(), _pre_node.get_name() ) )

                    # try receive on each connect
                    _rcv_pipe = _connect.get_rcv_pipe(self.get_id())

                    if _rcv_pipe is None:
                        continue

                    # read all msg on rcv pipe
                    # put all msg got onto m_snd_buf
                    _got_msgs = _rcv_pipe.recv_all()

                    #no msgs, try next node
                    if _got_msgs is None or len(_got_msgs) <= 0:
                        continue

                    for _got_msg in _got_msgs:
                        # print("%s:recv %d:\"%s\" from %s"%(self.get_name(), _got_msg.get_id(), _got_msg.get_content(), _pre_node.get_name()) )
                        self.m_snd_buf.put(_got_msg)

                # send msg
                while not self.m_snd_buf.empty():
                    # print("%s prepare to send"%(self.get_name()) )
                    
                    # dequeue a msg
                    _msg_to_snd = self.m_snd_buf.get()
                    if _msg_to_snd == None:
                        break
                    
                    # print("Msg \"%s\" in buf is ready to send"%( _msg_to_snd.get_content() ) )
                    
                    # find next hop by route info on msg
                    _next_hop_node = _msg_to_snd.get_route().find_next_hop(self)
                    # print("Next hop node is %s"%(_next_hop_node.get_name() ) )

                    if (not _next_hop_node is None) and _next_hop_node.is_work():
                        # print("%s: Send %d:\"%s\" to %s"%(self.get_name(), _msg_to_snd.get_id(), _msg_to_snd.get_content(), _next_hop_node.get_name() ) )

                        #find connect to target connect
                        _tar_connect = self.m_connects[_next_hop_node]

                        #find snd_pipe to target node
                        _snd_pipe = _tar_connect.get_snd_pipe(self.get_id())

                        #do send
                        _map.get_draw().mod_point(self.m_x, self.m_y, _col='yellow')
                        _snd_pipe.send(_msg_to_snd)
                        _map.get_draw().mod_point(self.m_x, self.m_y)

    # receiver loop
    def rcv_loop(self, _map):
        while self.is_run() and self.is_work():
            
            # if map is in rebuild, keep waiting
            while _map.is_in_rebuild():
                continue
            
            # poll all connects to rcv
            for (_pre_node, _connect) in self.m_connects.items():
                if _pre_node.is_work():
                    # try receive on each connect
                    _rcv_pipe = _connect.get_rcv_pipe(self.get_id())

                    # read all msg on rcv pipe
                    # put all msg got onto m_snd_buf
                    _got_msg = _rcv_pipe.recv()
                    while not _got_msg is None:
                        _map.get_draw().mod_point(self.m_x, self.m_y, _col='yellow')
                        print("dst %s: recv %d:\"%s\" from %s"%(self.get_name(), _got_msg.get_id(), _got_msg.get_content(), _pre_node.get_name()) )
                        _map.get_draw().mod_point(self.m_x, self.m_y)
                        self.m_snd_buf.put(_got_msg)
                        _got_msg = _rcv_pipe.recv()
                        _map.get_draw().mod_point(self.m_x, self.m_y)
                
    # wait work done
    def wait_node(self):
        self.m_node_thd.join()

    
