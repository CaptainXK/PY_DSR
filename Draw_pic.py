# import Tkinter
# from Tkinter import *
from tkinter import *
import threading

class Draw_map:
    m_tk=None
    m_canvas=None
    m_btn_stop=None
    m_bg='white'
    m_point_size=0
    m_draw_lock=None

    def __init__(self, _w, _h, _bg = 'white'):
        self.m_tk = Tk()
        self.m_tk.title('DSR simulation')
        self.m_canvas = Canvas(self.m_tk, width = _w, height = _h, bg=_bg)
        self.m_btn_stop = Button(self.m_tk, text='Stop')
        self.m_bg = _bg
        self.m_point_size = 7
        self.m_draw_lock = threading.Lock()
        # self.m_canvas.pack()
        # self.m_btn_stop.pack()

    #circle : center point (_x, _y) ,R=_r
    def put_point(self, _x, _y, _fill = 'black', _dash=None, _width=1, _outl=None, _r=0):
        if _r == 0:
            _r = self.m_point_size
        
        self.m_canvas.create_oval(_x-_r, _y-_r, _x+_r, _y+_r, fill=_fill, outline = _outl, width = _width, dash = _dash)
        self.m_tk.update()

    # mark a point
    def mark_point(self, _x, _y):
        self.put_point(_x, _y, _width=2, _dash=(4,4), _outl='red', _fill=None, _r=self.m_point_size * 3)

    #change point stat
    def mod_point(self, _x, _y, _fill = 'red'):
        self.put_point(_x, _y, _fill)
    
    #delete a point
    def del_point(self, _x, _y):
        self.put_point(_x, _y, _r=self.m_point_size+2, _fill='white', _outl='white')

    #add a edge
    def add_edge(self, _pos_1, _pos_2, _fill='black', _dash=None, _width=3):
        self.m_canvas.create_line(_pos_1[0], _pos_1[1], _pos_2[0], _pos_2[1], fill=_fill, width=_width, dash=_dash)
        self.m_tk.update()
    
    #delete a edge
    def del_edge(self, _pos_1, _pos_2):
        self.add_edge(_pos_1, _pos_2, _fill='white')

    # show comp
    def show_all(self):
        self.m_canvas.pack()
        self.m_btn_stop.pack()

    #keep map visiable
    def show_loop(self):
        self.m_tk.mainloop()

    #remove all
    def remove_all(self):
        self.m_canvas.delete("all")
    
    #bind double-click event
    def bind_dbc(self, call_back):
        self.m_canvas.bind("<Double-Button-1>", call_back)

    #bind btn_stop press event
    def bind_btn_stop(self, call_back):
        self.m_btn_stop.bind("<Button-1>", call_back)