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
    #nodes from source to destination
    m_nodes_list=[]

    def __init__(self):
        self.m_nodes_nb=0
        self.m_nodes_list=[]

    #add one node to node list by order
    def add_node(self, _node):
        self.m_nodes_list.append(_node)
        self.m_nodes_nb += 1
    
    #build by node list
    def init_by_nodes(self, _nodes_list):
        for _node in _nodes_list:
            self.add_node(_node)
    
    #find the next node for given node on current route
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

    #show nodes on current route
    def show_route(self):
        for _node in self.m_nodes_list:
            print("%d"%(_node.get_id()), end=' ')
        print("")

    #is in route
    def is_in(self, _node):
        if _node in self.m_nodes_list:
            return True
        else:
            return False

class Msg:
    m_content=''
    m_route_info=None
    m_id=0

    def __init__(self):
        self.m_route_list = []
        self.m_content=''
        self.m_route_info=None
        self.m_id=0

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