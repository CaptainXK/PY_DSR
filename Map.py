from Node import *
from Draw_pic import *
from Pipe import *
from Route import *

class Map:
    m_w = 0
    m_h = 0
    m_map = [[]]
    m_draw = None
    m_edges = [[]]
    m_pipes = []
    m_nodes_nb = 0
    m_nodes_list = []
    m_con_pool = []

    #constructor
    def __init__(self, _w, _h):
        self.m_w = _w
        self.m_h = _h
        self.m_map = [[ 0 for i in range(_w + 1)] for i in range(_h + 1)]
        self.m_draw = Draw_map(self.m_w, self.m_h)
        self.m_edges = []
        self.m_pipes = []
        self.m_nodes_nb = 0
        self.m_nodes_list = []
        self.m_con_pool = [Connect() for i in range(100)]
        self.m_draw
        #bind double click function
        self.m_draw.bind_dbc(self.del_node)


    def update_all(self):
        self.m_draw.remove_all()
        self.put_nodes(self.m_nodes_list)
        self.init_edge()
        src_id = 0
        dst_id = len(self.m_nodes_list) - 1
        self.cal_route(self.m_nodes_list[src_id], self.m_nodes_list[dst_id])   

    def init_all_con(self):
        for con in self.m_con_pool:
            con.close_con()
    
    def get_size(self):
        return [self.m_w, self.m_h]
    
    def put_node(self, _node):
        _pos = _node.get_pos()
        self.m_draw.put_point(_pos[0], _pos[1])
    
    def put_nodes(self, _node_list):
        self.m_nodes_list = _node_list

        # draw nodes one by one 
        # ignore node un-work
        for _node in _node_list:
            if _node.is_work():
                self.put_node(_node)
                self.m_nodes_nb += 1

    #double click event
    def del_node(self, event):
        _x = event.x
        _y = event.y
        print("Double click event on (%d, %d)"%(_x, _y))
        idx = 0
        for _node in self.m_nodes_list:
            if _node.under_cover(_x, _y):
                print("Remove %s"%(_node.get_name()))
                _node.go_die()
                break
        self.update_all()

    def init_edge(self):
        
        _node_list = self.m_nodes_list

        #init all edges
        self.m_edges.clear()

        #inie all con
        self.init_all_con()

        # find all node pairs where two nodes can touch each other
        for node1 in _node_list:
            for node2 in _node_list:
                if (node1 is not node2) and node1.is_work() and node2.is_work():
                    if node1.can_touch(node2):
                        # avoid duplicate edge, like "a->b" and "b->a"
                        if not ((node1, node2) in self.m_edges or (node2, node1) in self.m_edges):
                            self.m_draw.add_edge(node1.get_pos(), node2.get_pos(), _dash=(4,4) )
                            self.m_edges.append((node1, node2))
                            for con in self.m_con_pool:
                                if not con.is_in_use():
                                    con.set_nodes(node1.get_id(), node2.get_id())
                                    node1.add_connect(con, node2)
                                    node2.add_connect(con, node1)
                                    con.open_con()
                                    break

    def del_edge(self, _node1, _node2):
        idx = 0
        while idx < len(self.m_edges):
            if self.m_edges[idx] in [(_node1, _node2), (_node2, _node1)]:
                del self.m_edges[idx]
                return 1
            else:
                idx += 1

        self.m_draw.del_edge(_node1.get_pos(), _node2.get_pos())
        
        return 0

    def cal_route(self, _src_node, _dst_node):
        route_tmp = Route_path()

        #BFS to find the shortest path
        nodes_queue = Queue()

        #src node enqueue
        nodes_queue.put(_src_node)

        # pre-nodes dist
        # key = current node
        # val = pre-node
        pre_dist = {}

        pre_dist[_src_node] = None

        cur_node = None

        while not nodes_queue.empty():
            cur_node = nodes_queue.get()

            if cur_node is _dst_node:
                break

            _connect = cur_node.get_connects()

            next_nodes = _connect.keys()            

            for _next_hop_node in next_nodes:
                # avoid loop
                if (not _next_hop_node in pre_dist.keys()) and _next_hop_node.is_work():
                    pre_dist[_next_hop_node] = cur_node

                    #new next hop node enqueue
                    nodes_queue.put(_next_hop_node)

        if not (cur_node is _dst_node):
            print("No available route Path!")
            return  

        # trace back the whole route
        nodes_in_route = []

        while not cur_node is None:
            nodes_in_route.append(cur_node)
            cur_node = pre_dist[cur_node]

        # reverse to ensure list start from src to dst
        nodes_in_route.reverse()

        _route = Route_path()

        _route.init_by_nodes(nodes_in_route)

        _route.show_route()

        idx=0

        for _node in nodes_in_route:
            node_pos = _node.get_pos()
            self.m_draw.mod_point(node_pos[0], node_pos[1])

        while idx < len(nodes_in_route) - 1:
            self.m_draw.add_edge(nodes_in_route[idx].get_pos(), nodes_in_route[idx+1].get_pos() , _col='green')
            idx += 1
        
    def show_loop(self):
        self.m_draw.show_loop()
        
