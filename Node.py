import math
from queue import Queue
from Pipe import Pipe
from Route import Connect, Msg, Route_path
import re
import threading
import datetime
import time
import copy

gl_node_type={'SRC':0, 'FWD':1, 'DST':2}

# Node base class
class Node:
    m_is_work=True # node is available or not
    m_is_run=True # node threading is running or not
    m_x=0
    m_y=0
    m_range=0
    m_name=''
    m_snd_buf=None
    m_rsnd_buf=None
    m_connects=None
    m_id=0
    m_point_sz=5
    m_type=0
    m_route=None #fwd route for src node
    m_node_thd=None
    m_ready=False # sig flag shared with Map to notify that "I am ready"

    def __init__(self, _name, _x, _y, _range):
        self.m_x = _x
        self.m_y = _y
        self.m_range = _range
        self.m_name = _name
        self.m_snd_buf = Queue() 
        self.m_rsnd_buf = Queue() 
        self.m_is_work=True
        self.m_is_run=True
        self.m_id = int(re.search(r'([\d]+)', _name, re.I).group(0))
        self.m_point_sz=5
        self.m_type=0
        self.m_ready=False # sig flag shared with Map to notify that "I am ready"

        #next hop dist
        # key = next hop node
        # val = connect to next hop node
        self.m_connects = {}

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
        if _tar_node.is_work() and _tar_node in self.m_connects.keys():
            _snd_pipe = self.m_connects[_tar_node].get_snd_pipe(self.m_id)
            _snd_pipe.send(_msg)
    
    #recv
    def recv_msg(self, _tar_node):
        #recv msg to rcv_buf
        if _tar_node.is_work() and _tar_node in self.m_connects.keys():
            _rcv_pipe = self.m_connects[_tar_node].get_rcv_pipe(self.m_id)
            return _rcv_pipe.__recv__()
        else:
            return None

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

    #check if node is configured ready
    def is_ready(self):
        return self.m_ready

    #stop running
    def start_node(self):
        self.m_is_run = True
    
    #stop running
    def stop_node(self):
        if self.is_run():
            self.m_is_run = False

    #check if the given pos(_x, _y) is on node
    def under_cover(self, _x, _y):
        _dis = math.sqrt((pow(abs(_x - self.m_x), 2) + pow(abs(_y - self.m_y), 2)) )
        _dis = int(_dis)

        if _dis <= self.m_point_sz:
            return True
        else:
            return False
    
    # wait work done
    def wait_node(self):
        self.m_node_thd.join()
        # print("[%s quit]"%(self.get_name()))

# sender node
class Src_node(Node):
    m_dst_nodes = None
    m_test_content = 'I\'ve got you in my sight'
    m_rd_pit = 0 # 0 means no route discover request is pending, otherwise at least one request does
    m_cur_msg_id=0

    def __init__(self, _name, _x, _y, _range):
        # involve base class init
        Node.__init__(self, _name, _x, _y, _range)
        self.m_dst_nodes = []
        self.m_rd_pit = 0
        self.m_cur_msg_id = 0

    # add a dst_node
    def add_dst_node(self, _node):
        self.m_dst_nodes.append(_node)
    
    # lunch a node
    def node_lunch(self):
        # init threading
        self.m_node_thd = threading.Thread(target=Src_node.main_loop, args=(self,) )

        #start to work    
        self.m_node_thd.start()

    # send rd_msg
    def send_rd_msg(self):
        # poll all neighborhood to send rd msg
        for _node, _connect in self.m_connects.items():
            if not _node.is_work():
                continue

            # get snd pipe
            _snd_pipe = _connect.get_snd_pipe(self.m_id)

            _msgs=[]
            # for all dst node
            for _dst_node in self.m_dst_nodes:
                # prepare rd msg
                _rd_msg = Msg()

                # msg route info
                _route_info = _rd_msg.get_route()

                # set type
                _rd_msg.set_type(1)

                # set dst node
                _route_info.set_dst_node(_dst_node)

                # add my self into route
                _route_info.add_node(self)

                # add into _msgs
                _msgs.append(_rd_msg)
            
            # do send to one neighborhood node
            if len(_msgs) > 0:
                _snd_pipe.send_all(_msgs)
                print("%s : I just sended one rd msg to %s"%(self.get_name(), _node.get_name()))

    # process fb_msg
    def recv_fb_or_nat_msg(self):
        # poll all neighborhood nodes to wait feedback msg
        for _node, _connect in self.m_connects.items():
            if _node.is_work():
                # get recv pipe 
                _rcv_pipe = _connect.get_rcv_pipe(self.m_id)

                # recv all msgs
                _msgs = _rcv_pipe.recv_all()

                # parse all msgs
                for _msg in _msgs:
                    print("%s : recv fb msg"%(self.get_name()))
                    # got a feedback route
                    if _msg.get_type() == 2:
                        # fetch route info in msg
                        _route_info = _msg.get_route()

                        # get dst node
                        _dst_node = _route_info.get_dst_node()

                        # add (_dst_node, _route_info) pair into route dist
                        _route_info.do_reverse()
                        self.m_route[_dst_node] = Route_path()
                        self.m_route[_dst_node].init_by_nodes(_route_info.get_nodes_in_path())
                        self.m_route[_dst_node].set_dst_node(_route_info.get_dst_node())

                        # add _dst_node to dst_node list
                        self.m_dst_nodes.append(_dst_node)

                        # zero rd pit flag
                        self.m_rd_pit = 0

                        # show somthing
                        print("%s : got a route info to %s"%(self.get_name(), _dst_node.get_name()))
                        _route_info.show_route()

    # send nor msg
    def send_nor_msg(self):
        # send to all dst nodes
        for _dst_node in self.m_dst_nodes:
            # new a empty msg
            _msg_to_snd = Msg()

            # set msg type
            _msg_to_snd.set_type(0)

            # got route path info to dst node

            if not _dst_node in self.m_route.keys():
                return
            _route_to_dst = self.m_route[_dst_node]

            # find next hop on current route
            _next_hop_node = _route_to_dst.find_next_hop(self)
            if not _next_hop_node or not _next_hop_node.is_work():
                continue

            # find connect to next hop node
            _next_hop_con = self.get_connect(_next_hop_node)

            # find snd pipe to next hop node
            _snd_pipe = _next_hop_con.get_snd_pipe(self.get_id())

            # fill test content
            _msg_to_snd.fill_content(self.m_test_content)

            # fill route info
            _msg_to_snd.set_route_info(_route_to_dst)

            # set id
            _msg_to_snd.set_id(self.m_cur_msg_id)
            self.m_cur_msg_id += 1

            # do snd
            _snd_pipe.send(_msg_to_snd)
            # print("sender %s: Send %d:\"%s\" to %s"%(self.get_name(), _msg_to_snd.get_id(), _msg_to_snd.get_content(), _next_hop_node.get_name() ) )
    
    # sender loop
    def main_loop(self):
        # notify Map that i am ready
        self.m_ready = True
        print("%s : I am a src node, and i am ready"%(self.get_name()))
        
        # send one msg every 3 seconds
        pre_time = datetime.datetime.now()
        cur_time = 0
        msg_idx = 0

        while self.is_work():
            while not self.is_run():
                if not self.is_work():
                    return
                else:
                    continue
        
            # update cur_time
            cur_time = datetime.datetime.now()

            # check if it is time to send
            if (cur_time - pre_time).seconds < 3:
                # recv and continue
                if len(self.m_route.keys()) == 0:
                    self.recv_fb_or_nat_msg()
                continue
            else:
                # it is time
                # update pre_time and do send
                pre_time = cur_time

            # if there is at least one dst node, do send normal msg
            if len(self.m_route.keys()) > 0:
                self.send_nor_msg()
            
            # otherwise, begin a route discover boardcast if no route discover request is pending
            elif self.m_rd_pit == 0:
                self.send_rd_msg()
                self.m_rd_pit = 1

        # quit main loop
        print("[%s quit]"%(self.get_name()))


# receiver node
class Nor_node(Node):
    def __init__(self, _name, _x, _y, _range):
        # involve base class init
        Node.__init__(self, _name, _x, _y, _range)
    
    # lunch a node
    def node_lunch(self):
        # init threading
        self.m_node_thd = threading.Thread(target=Nor_node.main_loop, args=(self,) )

        #start to work    
        self.m_node_thd.start()
    
    # process rd_msg
    def process_rd_msg(self, _pre_node, _msg):
        # get route info in msg
        _msg_route_info = _msg.get_route()
        
        # if i am the dst node
        if _msg_route_info.get_dst_node() is self:
            # add my self into route nodes list
            _msg_route_info.add_node(self)

            #reverse route nodes list to send it to src
            _msg_route_info.get_nodes_in_path().reverse()

            # modify msg's type to feedback msg
            _msg.set_type(2)

            #do send
            self.process_fb_msg(_msg)
            print("%s : rcv node has received a route discover msg, in process..."%(self.get_name()))
        # if i am not the dst node
        else:
            # check if i am in route info already to avoid loop
            if _msg_route_info.is_in(self):
                return
            else:
            # broadcast route discover msg to all neighbor nodes but the node that msg came from
                _msg_route_info.add_node(self)
                for (_to_node, _connect) in self.m_connects.items():
                    # do not send to
                    if not (_to_node is _pre_node):
                        self.send_msg(_to_node, _msg)

    # process fb_msg
    def process_fb_msg(self, _msg):
        # get route info in msg
        _msg_route_info = _msg.get_route()

        # find next hop node
        _to_node = _msg_route_info.find_next_hop(self)

        if not _to_node:
            return

        # do send
        self.send_msg(_to_node, _msg)

    # process nor msg
    def process_nor_msg(self, _msg):
        # get route info in msg
        _msg_route_info = _msg.get_route()

        # get dst node id in route info
        _dst_node = _msg_route_info.get_dst_node()

        # check if i am the dst id
        # if i am , print content and stop forwarding it
        if _dst_node is self:
            # get msg content
            _msg_content = _msg.get_content()

            # get msg id
            _msg_id = _msg.get_id()

            # show somthing
            print("%s : i receive one msg, id=%d, content='%s'"%(self.get_name(), _msg_id, _msg_content) )
        else:
            # find next hop node
            _to_node = _msg_route_info.find_next_hop(self)

            # do send
            self.send_msg(_to_node, _msg)
    
    # receiver loop
    def main_loop(self):
        # notify Map that i am ready
        self.m_ready = True
        print("%s : I am a normal node, and i am ready"%(self.get_name()))
        
        while self.is_work():
            while not self.is_run():
                if not self.is_work():
                    return
                else:
                    continue
            
            # poll all connects to rcv
            for (_pre_node, _connect) in self.m_connects.items():
                if _pre_node.is_work():
                    # try receive on each connect
                    _rcv_pipe = _connect.get_rcv_pipe(self.get_id())

                    # read all msg on rcv pipe, put all msg got onto m_snd_buf
                    # do recv all
                    _got_msgs = _rcv_pipe.recv_all()

                    # process msg one by one
                    for _got_msg in _got_msgs:
                        # print("%s : recv %d:\"%s\" from %s"%(self.get_name(), _got_msg.get_id(), _got_msg.get_content(), _pre_node.get_name()) )
                        _cur_type = _got_msg.get_type()
                        if _cur_type == 0:   # nor msg
                            # print("%s : recv %d:\"%s\" from %s"%(self.get_name(), _got_msg.get_id(), _got_msg.get_content(), _pre_node.get_name()) )
                            self.process_nor_msg(_got_msg)

                        elif _cur_type == 1: # rd msg
                            # print("%s : recv rd msg from %s"%(self.get_name(), _pre_node.get_name()) )
                            self.process_rd_msg(_pre_node, _got_msg)
                            
                        elif _cur_type == 2: # fb msg
                            # print("%s : recv fb msg from %s"%(self.get_name(), _pre_node.get_name()) )
                            self.process_fb_msg(_got_msg)
                        else:
                            pass
                            # print("%s : waiting..."%(self.get_name()) )


        # quit main loop
        print("[%s quit]"%(self.get_name()))
