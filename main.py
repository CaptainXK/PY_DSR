from Node import Node
from Map import Map
import sys
import getopt

X = 800
Y = 800

def cmd_parse_file(args):
    _file=''

    try:
        opts, arg = getopt.getopt(args, 'f:')
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(1)
    
    for opt, arg in opts:
        if opt == '-f':
            _file = arg
        else:
            print("Option error")
            sys.exit(1) 

    return _file



def load_nodes(_file, _nodes_list):
    _datas = []
    with open(_file, 'r') as _fin:
        _datas = _fin.readlines()

    for _data_items in _datas:
        _data = _data_items.split(' ')
        # print("name=%s, x=%d, y=%d, range=%d"%(_data[0], int(_data[1]), int(_data[2]), int(_data[3])))
        node_tmp = Node(_data[0], int(_data[1]), int(_data[2]), int(_data[3]))
        _nodes_list.append(node_tmp)

def fake_load_node(_nodes_list):
    init_pos = [[10, 10, 100], [50, 50, 100], [100,100,200], [150, 150,150], [150, 200, 150]]

    idx=1
    for x, y, r in init_pos:
        node = Node(str(idx), x, y, r)
        _nodes_list.append(node)
        idx += 1


def __main__():

    global X
    global Y

    nodes_list=[]

    # nodes load test
    # fake_load_node(nodes_list)

    data_file_path = cmd_parse_file(sys.argv[1:])

    if data_file_path is '':
        print("No data file detected\n")
        sys.exit(1)

    load_nodes(data_file_path, nodes_list)

    _map = Map(X, Y)

    _map.load_nodes(nodes_list)

    _map.init_edge()

    src_id = 0
    dst_id = len(nodes_list) - 1

    _map.cal_route(nodes_list[src_id], nodes_list[dst_id])
    
    _map.put_nodes()

    _map.start_all_nodes()

    _map.show_loop()

    _map.stop_all_nodes()

    del _map

__main__()