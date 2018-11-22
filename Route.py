from Pipe import *

class Connect:
    m_in_use=False
    m_nodes={}
    m_1to2_pipe=None
    m_2to1_pipe=None

    def __init__(self):
        self.m_1to2_pip = Pipe()
        self.m_2to1_pip = Pipe()
        self.m_in_use = False

    def set_nodes(self, _id_1, _id_2):
        self.m_nodes[_id_1] = 1
        self.m_nodes[_id_2] = 2
        self.m_in_use = True

    
    def get_snd_pipe(self, _id):
        if self.m_nodes[_id] == 1:
            return self.m_1to2_pipe
        else:
            return self.m_2to1_pipe
    
    def get_rcv_pipe(self, _id):
        if self.m_nodes[_id] == 1:
            return self.m_2to1_pipe
        else:
            return self.m_1to2_pipe
    
    def is_in_use(self):
        return self.m_in_use
    
    def close_con(self):
        self.m_in_use = False
    
    def open_con(self):
        self.m_in_use = True
    
class Msg:
    m_route_list=[]
    m_content=''
    m_route_info=None

    def __init__(self):
        self.m_route_list = []
        self.m_content=''
        self.m_route_info=None

    def fill_content(self, _content):
        self.m_content = _content

    def set_route_info(self, _route_info):
        self.m_route_info = _route_info
    

class Route_path:
    m_nodes_nb=0
    #nodes from source to destination
    m_nodes_list=[]

    def __init__(self):
        self.m_nodes_nb=0
        self.m_nodes_list=[]

    def add_node(self, _node):
        self.m_nodes_list.append(_node)
        self.m_nodes_nb += 1
    
    def init_by_nodes(self, _nodes_list):
        for _node in _nodes_list:
            self.add_node(_node)
    
    def find_next_hop(self, _node):
        idx = 0

        _next_node=None

        while idx < len(self.m_nodes_list):
            if self.m_nodes_list[idx] == _node and (idx+1) < len(self.m_nodes_list):
                _next_node = self.m_nodes_list[idx+1]
                break

        return _next_node

    def show_route(self):
        for _node in self.m_nodes_list:
            print("%d"%(_node.get_id()), end=' ')
        print("")