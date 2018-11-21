# import Tkinter
# from Tkinter import *
import tkinter
from tkinter import *

class Draw_map:
    m_tk=None
    m_canvas=None
    m_bg='white'
    m_point_size=0

    def __init__(self, _w, _h, _bg = 'white'):
        self.m_tk = Tk()
        self.m_canvas = Canvas(self.m_tk, width = _w, height = _h, bg=_bg)
        self.m_bg = _bg
        self.m_point_size = 3
        self.m_canvas.pack()

    #circle : center point (_x, _y) ,R=_r
    def put_point(self, _x, _y, _col = 'black'):
        _r = self.m_point_size
        self.m_canvas.create_oval(_x-_r, _y-_r, _x+_r, _y+_r, fill=_col)
        self.m_tk.update()
    
    def del_point(self, _x, _y, _col = 'white'):
        self.put_point(_x, _y, _col)
    
    def add_edge(self, _pos_1, _pos_2, _col='red'):
        print("edge:(%d, %d)---(%d, %d)"%(_pos_1[0], _pos_1[1], _pos_2[0], _pos_2[1]) )
        self.m_canvas.create_line(_pos_1[0], _pos_1[1], _pos_2[0], _pos_2[1], fill=_col)
        self.m_tk.update()
    
    def del_edge(self, _pos_1, _pos_2, col='while'):
        self.add_edge(self, _pos_1, _pos_2, col)


    def show_loop(self):
        self.m_tk.mainloop()