from Node import *
from Draw_pic import *
from Pipe import *

class Map:
    m_w = 0
    m_h = 0
    m_map = [[]]
    m_draw = None
    m_edges = [[]]
    m_pipes = []
    m_nodes_nb = 0

    #constructor
    def __init__(self, _w, _h):
        self.m_w = _w
        self.m_h = _h
        self.m_map = [[ 0 for i in range(_w + 1)] for i in range(_h + 1)]
        self.m_draw = Draw_map(self.m_w, self.m_h)
        self.m_edges = []
        self.m_pipes = []
        self.m_nodes_nb = 0
    
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
        self.m_nodes_nb = len(_node_list)
        for node1 in _node_list:
            for node2 in _node_list:
                if node1 is not node2:
                    if node1.can_touch(node2):
                        if not ((node1, node2) in self.m_edges or (node2, node1) in self.m_edges):
                            self.m_draw.add_edge(node1.get_pos(), node2.get_pos(), _dash=(4,4))
                            self.m_edges.append((node1, node2))

    def init_route(self):
        _map = [0 for i in range(self.m_nodes_nb + 1) for i in range(self.m_nodes_nb) + 1]
        
        for node1, node2 in self.m_edges:
            _map[node1.get_id()][node2.get_id()] = 1

    def del_edge(self, _node1, _node2):
        idx = 0
        while idx < len(self.m_edges):
            if self.m_edges[idx] in [(_node1, _node2), (_node2, _node1)]:
                del self.m_edges[idx]
                return 1
            else:
                idx += 1
        
        return 0

    def show_loop(self):
        self.m_draw.show_loop()
        
