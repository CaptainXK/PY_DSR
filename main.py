from Node import Src_node, Nor_node
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

    # first node is src node
    # last node is dst node
    src_id = 0

    idx = 0
    for _data_items in _datas:
        _data = _data_items.split(' ')
        node_tmp = None
        if idx == src_id:
            node_tmp = Src_node(_data[0], int(_data[1]), int(_data[2]), int(_data[3]))
        else:
            node_tmp = Nor_node(_data[0], int(_data[1]), int(_data[2]), int(_data[3]))

        _nodes_list.append(node_tmp)

        idx += 1


def __main__():

    global X
    global Y

    nodes_list=[]

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

    _map.set_src_dst(nodes_list[src_id], nodes_list[dst_id])
    
    _map.put_nodes()
    
    _map.start_all_nodes()
    
    _map.show_loop()

    # if turns off diag directly
    _map.stop_all_nodes()

    del _map

__main__()