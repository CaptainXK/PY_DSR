from Node import *
from Draw_pic import *

class Map:
    m_w = 0
    m_h = 0
    m_map = [[]]
    m_draw = None

    #constructor
    def __init__(self, _w, _h):
        self.m_w = _w
        self.m_h = _h
        self.m_map = [[ 0 for i in range(_w + 1)] for i in range(_h + 1)]
        self.m_draw = Draw_map(self.m_w, self.m_h)
    
    def get_size(self):
        return [self.m_w, self.m_h]
    
    def put_node(self, _node):
        _pos = _node.get_pos()
        self.m_draw.put_point(_pos[0], _pos[1])
    
    def put_nodes(self, _node_list):
        for _node in _node_list:
            self.put_node(_node)

    def del_node(self, _node):
        _pos = _node.get_pos()
        self.m_draw.del_point(_pos[0], _pos[1])     

    def init_edge(self, _node_list):
        for node1 in _node_list:
            for node2 in _node_list:
                if node1 is not node2:
                    if node1.can_touch(node2):
                        self.m_draw.add_edge(node1.get_pos(), node2.get_pos())

    def show_loop(self):
        self.m_draw.show_loop()
        
