class Connect:
    m_tar_node=None
    m_snd_pipe=None
    m_rcv_pipe=None

    def __init__(self, _node, _snd_pipe, _rcv_pipe):
        self.m_tar_node = _node
        self.m_snd_pip = _snd_pipe
        self.m_rcv_pip = _rcv_pipe 
    
    def get_snd_pipe(self):
        return self.m_snd_pipe
    
    def get_rcv_pipe(self):
        return self.m_rcv_pipe
    
    def get_tar_node(self):
        return self.m_tar_node

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
    
    def find_next_hop(self, _node):
        idx = 0

        _next_node=None

        while idx < len(self.m_nodes_list):
            if self.m_nodes_list[idx] == _node and (idx+1) < len(self.m_nodes_list):
                _next_node = self.m_nodes_list[idx+1]
                break

        return _next_node

# def cal_routes(_map, _src, _dst):
#     #BFS to find all route available
