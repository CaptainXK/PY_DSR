from Pipe import Pipe

class Connect:
    m_in_use=False
    m_nodes=None
    m_1to2_pipe=None
    m_2to1_pipe=None

    def __init__(self):
        self.m_1to2_pipe = Pipe()
        self.m_2to1_pipe = Pipe()
        self.m_in_use = False
        self.m_nodes={}

    # set node1 and node2 for current connect
    def set_nodes(self, _id_1, _id_2):
        self.m_nodes[_id_1] = 1
        self.m_nodes[_id_2] = 2
        self.m_in_use = True

    # get snd pipe
    # node1 uses 1to2 
    # node2 uses 2to1
    def get_snd_pipe(self, _id):
        if self.m_nodes[_id] == 1:
            return self.m_1to2_pipe
        else:
            return self.m_2to1_pipe
    
    # get rcv pipe
    # node1 uses 2to1
    # node2 uses 1to2
    def get_rcv_pipe(self, _id):
        if self.m_nodes[_id] == 1:
            return self.m_2to1_pipe
        else:
            return self.m_1to2_pipe
    
    #check if current connect is in using
    def is_in_use(self):
        return self.m_in_use
    
    #close current connect
    def close_con(self):
        self.m_in_use = False
    
    #open current connect
    def open_con(self):
        self.m_in_use = True

class Route_path:
    m_nodes_nb=0
    
    # nodes from source to destination
    m_nodes_list=[]

    # dst node
    m_dst_node=None

    # src node
    m_src_node=None

    def __init__(self):
        self.m_nodes_nb=0
        self.m_nodes_list=[]
        self.m_dst_node=None
        self.m_src_node=None

    # get nodes number
    def get_nodes_nb(self):
        return self.m_nodes_nb

    # add one node to node list by order
    def add_node(self, _node):
        self.m_nodes_list.append(_node)
        self.m_nodes_nb += 1
    
    # build by node list
    def init_by_nodes(self, _nodes_list):
        for _node in _nodes_list:
            self.add_node(_node)
    
    # find the next node for given node on current route
    def find_next_hop(self, _node):
        _next_node=None
        idx = 0
        while idx < len(self.m_nodes_list):
            if self.m_nodes_list[idx] == _node and (idx+1) < len(self.m_nodes_list):
                _next_node = self.m_nodes_list[idx+1]
                break
            else:
                idx += 1

        return _next_node

    # show nodes on current route
    def show_route(self):
        for _node in self.m_nodes_list:
            print("%d"%(_node.get_id()), end=' ')
        print("")

    # get nodes list
    def get_nodes_in_path(self):
        return self.m_nodes_list

    # is in route
    def is_in(self, _node):
        if _node in self.m_nodes_list:
            return True
        else:
            return False
    
    # reverse route
    def do_reverse(self):
        if len(self.m_nodes_list) > 0:
            self.m_nodes_list.reverse()

    # get dst node
    def get_dst_node(self):
        return self.m_dst_node

    # set dst node
    def set_dst_node(self, _dst_node):
        self.m_dst_node = _dst_node

    # get src node
    def get_src_node(self):
        return self.m_src_node

    # set src node
    def set_src_node(self, _src_node):
        self.m_src_node = _src_node

class Msg:
    m_content='' # content string if needed

    m_route_info=None # route infomation obj

    m_id=0 # sequence number of msg

    m_type=0 # 3 for route force feedback msg, normal node sends it to src node after re-build route
             # 2 for route feedback msg, 
             # 1 for route discover msg,
             # 0 for normal msg 

    def __init__(self):
        self.m_route_list = []
        self.m_content=''
        self.m_route_info=Route_path()
        self.m_id=0
        self.m_type = 0

    # fill content
    def fill_content(self, _content):
        self.m_content = _content

    # get content
    def get_content(self):
        return self.m_content

    # fill route info
    def set_route_info(self, _route_info):
        self.m_route_info = _route_info

    # get route
    def get_route(self):
        return self.m_route_info

    # set id
    def set_id(self, _id):
        self.m_id = _id
    
    # get id
    def get_id(self):
        return self.m_id
    
    # set type
    def set_type(self, _type):
        self.m_type = _type

    # get type
    def get_type(self):
        return self.m_type

    # append a node id
    def append_node_id(self, _id):
        _cur_content = self.get_content()
        _cur_content.append(_id)


    