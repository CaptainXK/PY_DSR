from Node import *
from Map import *

X = 500
Y = 500

def __main__():
    init_pos = [[10, 10, 100], [50, 50, 100], [100,100,200], [150, 150,100], [150, 200, 300]]
    nodes_list = []

    for x, y, r in init_pos:
        node = Node(x, y, r)
        nodes_list.append(node)

    global X
    global Y

    _map = Map(X, Y)

    _map.put_nodes(nodes_list)

    _map.init_edge(nodes_list)

    _map.show_loop()

__main__()