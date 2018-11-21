from Node import *
from Map import *

X = 500
Y = 500

def __main__():
    init_pos = [[230, 100], [50, 50], [20,20], [120, 75], [200, 300]]
    nodes_list = []

    for x, y in init_pos:
        node = Node(x, y, 100)
        nodes_list.append(node)

    global X
    global Y

    _map = Map(X, Y)

    _map.put_nodes(nodes_list)

    _map.show_loop()

__main__()