from Node import Node, gl_node_type
from Draw_pic import Draw_map
from Pipe import Pipe
from Route import Connect, Msg, Route_path
from queue import Queue
import threading
import time

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
    m_cur_src=None
    m_cur_dst=None
    m_is_in_rebuild=False
    m_draw_lock=None
    m_is_quit=False

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

        #bind double click function
        self.m_draw.bind_dbc(self.del_node)
        #bind stop
        self.m_draw.bind_btn_stop(self.stop_all_nodes_callback)
        self.show_all()
        
        self.m_cur_src=None
        self.m_cur_dst=None

        #init draw lock
        self.m_draw_lock = threading.Lock()

        self.m_is_quit=False

    # show map 
    def show_all(self):
        self.m_draw.show_all()

    # update before network rebuild anytime
    def update_all(self, _del_node):
        pass
        # # get current route info of src node
        # _cur_src_route_dict = self.get_global_src().get_route()
        # _cur_src_route = _cur_src_route_dict[self.get_global_dst()]

        # # check if deleted node is in the route path
        # if _cur_src_route.is_in(_del_node):
        #     # if need to find a route, re-draw whole canvas first
        #     self.m_draw.remove_all()

        #     # stop all nodes in current route path
        #     for _node in _cur_src_route.get_nodes_in_path():
        #         _node.stop_node()


        #     #re-build and re-draw route
        #     nodes_in_path = _cur_src_route.get_nodes_in_path()
        #     idx = 0
        #     while idx < ( len(nodes_in_path) - 1):
        #         self.del_edge(nodes_in_path[idx], nodes_in_path[idx+1])
        #         idx += 1
            
        #     # re-draw all node on work after delete route edge
        #     self.put_nodes()

        #     # no route path available, stop src node sending msg
        #     if not self.cal_route():
        #         self.m_cur_src.stop_node()

        #     # restart all paused node
        #     for _node in _cur_src_route.get_nodes_in_path():
        #         _node.start_node()
        # else:
        #     # just re-draw route
        #     self.re_draw_route(_cur_src_route.get_nodes_in_path())

    # reset all connect in connect pool
    def init_all_con(self):
        for con in self.m_con_pool:
            con.close_con()

    # get draw obj
    def get_draw(self):
        return self.m_draw
    
    # get size of current map
    def get_size(self):
        return [self.m_w, self.m_h]

    # load nodes
    def load_nodes(self, _nodes_list):
        self.m_nodes_list = _nodes_list
        self.m_nodes_nb = len(_nodes_list)
    
    # put a node onto map by its pos
    def put_node(self, _node):
        _pos = _node.get_pos()
        self.m_draw.put_point(_pos[0], _pos[1])
    
    # put nodes from given nodes' list
    def put_nodes(self):
        # draw nodes one by one 
        # ignore node un-work
        for _node in self.m_nodes_list:
            if _node.is_work():
                self.put_node(_node)
                if _node is self.get_global_src() or _node is self.get_global_dst():
                    #mark src and dst node
                    self.mark_node(_node)

    #set src and dst
    def set_src_dst(self, _src, _dst):
        self.m_cur_src = _src
        self.m_cur_dst = _dst
        _src.add_dst_node(_dst)

    # mark a node
    def mark_node(self, _node):
        _pos = _node.get_pos()
        # process
        self.m_draw.mark_point(_pos[0], _pos[1])

    # init all edge
    # any nodes pair that can touch with each other, and both of them is on working, 
    # contitudes a edge
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
                            # self.m_draw.add_edge(node1.get_pos(), node2.get_pos(), _dash=(4,4) )
                            self.m_edges.append((node1, node2))
                            for con in self.m_con_pool:
                                if not con.is_in_use():
                                    # add a new connect for each nodes pair
                                    con.set_nodes(node1.get_id(), node2.get_id())
                                    node1.add_connect(con, node2)
                                    node2.add_connect(con, node1)
                                    con.open_con()
                                    break

    #draw route path
    def draw_route(self):
        # wait src find a route
        _src_node = self.get_global_src()
        _dst_node = self.get_global_dst()
        _route_to_dst = None
        _src_route_dist = _src_node.get_route()
        
        while not _route_to_dst:
            if _dst_node in _src_route_dist.keys():
                _route_to_dst = _src_route_dist[_dst_node]
        
        # get route nodes list
        nodes_in_route = _route_to_dst.get_nodes_in_path()
                
        # re-draw all edge on route path
        idx=0

        # process edge
        while idx < len(nodes_in_route) - 1:
            self.m_draw.add_edge(nodes_in_route[idx].get_pos(), nodes_in_route[idx+1].get_pos() , _fill='green')
            idx += 1
        
        # process node
        for _node in nodes_in_route:
            node_pos = _node.get_pos()
            # switch status of nodes on working
            self.m_draw.mod_point(node_pos[0], node_pos[1])
    
    # get src
    def get_global_src(self):
        return self.m_cur_src

    # get node
    def get_global_dst(self):
        return self.m_cur_dst

    # all nodes start
    def start_all_nodes(self):
        for _node in self.m_nodes_list:
            if _node.is_work():
                # for src node
                if _node is self.get_global_src():
                    _node.node_lunch()

                #for dst node
                elif _node is self.get_global_dst():
                    _node.node_lunch()

                #for fwd node
                else:
                    _node.node_lunch()

        # check if all node ready
        for _node in self.m_nodes_list:
            if _node.is_work():
                while not _node.is_ready():
                    continue

        # start all node by reverse order
        for _node in reversed(self.m_nodes_list):
            if _node.is_work():
                _node.start_node()

    # double click event
    def del_node(self, event):
        _x = event.x
        _y = event.y
        print("Double click event on (%d, %d)"%(_x, _y))
        for _node in self.m_nodes_list:
            if _node.under_cover(_x, _y):

                if _node is self.get_global_src():
                    print("Can not delete src node")
                    return
                elif _node is self.get_global_dst():
                    print("Can not delete dst node")
                    return
                else:
                    print("Remove %s"%(_node.get_name()))
                
                _node.go_die()
                _node_pos = _node.get_pos()

                # do delete
                self.get_draw().del_point(_node_pos[0], _node_pos[1])

                self.m_nodes_nb -= 1
                self.update_all(_node)
                break

    # stop all node
    # bind to button
    def stop_all_nodes_callback(self, event):
        for _node in self.m_nodes_list:
                _node.go_die()
        
        for _node in self.m_nodes_list:
            _node.wait_node()

        print("All node stop")

        self.m_is_quit = True

    # stop all nodes 
    def stop_all_nodes(self):
        if self.m_is_quit:
            return

        for _node in self.m_nodes_list:
                _node.go_die()
        
        for _node in self.m_nodes_list:
            _node.wait_node()
        
        print("All node stop")
    
    #keep the map visiable
    def show_loop(self):
        self.m_draw.show_loop()
        
