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
