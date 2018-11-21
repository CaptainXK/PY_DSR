import math

class Node:
    m_x=0
    m_y=0
    m_range=0
    
    def __init__(self, _x, _y, _range):
        self.m_x = _x
        self.m_y = _y
        self.m_range = _range
    
    def get_pos(self):
        return [self.m_x, self.m_y]
    
    def get_range(self):
        return self.m_range

    def can_touch(self, _node):
        _pos = _node.get_pos()
        _range = _node.get_range()

        #calculate distance
        _dis = int(math.sqrt(pow(abs(_pos[0] - self.m_x), 2) + pow(abs(_pos[1] - self.m_y), 2) ))

        #can touch?
        if _dis <= self.m_range and _dis <= _range:
            return True
        else:
            return False
