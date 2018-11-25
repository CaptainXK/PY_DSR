# import Tkinter
# from Tkinter import *
from tkinter import *
import threading
from Pipe import Pipe

# draw control event msg class 
class Draw_control_event:
    m_pos=[]    # pos[0] for 'oval', pos[0] and pos[1] for src and dst pos respectively for 'edge'
    m_fill=None # fill color
    m_outl=None # border color
    m_width=0   # edge width
    m_dash=None # full line or dot line
    m_type=None # 'edge', 'oval'
    m_point_sz = 5
    m_src=None  # 'Map' or 'Node'

    def __init__(self, x=0, y=0, fill=None, outl=None, width=1, dash=None, type=None, src=None):
        self.m_pos = []
        self.m_fill = fill
        self.m_outl = outl
        self.m_width = width
        self.m_dash = dash
        self.m_type = type
        self.m_point_sz = 5
        self.m_src=src

    # create a node
    def event_create_node(self, x, y):
        self.m_pos.append([x, y])
        self.m_fill = 'black'
    
    # mark a node
    def event_mark_node(self, x, y):
        self.m_pos.append([x, y])
        self.m_fill = None
        self.m_point_sz = 5 * 3
        self.m_dash = (4, 4)
        self.m_outl = 'red'

    # delete a node
    def event_delete_node(self, x, y):
        self.m_pos.append([x, y])
        self.m_fill = 'white'
        self.m_point_sz += 3 # plus 1 to ensure wipe the whole node
        self.m_outl = 'white'
    
    # set node's color to work status
    def event_work_node(self, x, y):
        self.m_pos.append([x, y])
        self.m_fill = 'yellow'
    
    # set node's color to ready status
    def event_ready_node(self, x, y):
        self.m_pos.append([x, y])
        self.m_fill = 'red'

    # create a edge
    def event_create_edge(self, x1, y1, x2, y2):
        self.m_pos.append([x1, y1]) # src point
        self.m_pos.append([x2, y2]) # dst point
        self.m_dash = (4, 4)
        self.m_width = 1
        self.m_fill = 'black'

    # delete a edge
    def event_delete_edge(self, x1, y1, x2, y2):
        self.m_pos.append([x1, y1]) # src point
        self.m_pos.append([x2, y2]) # dst point
        self.m_width = 1
        self.m_fill = 'white'

    # create a route
    def event_create_route(self, x1, y1, x2, y2):
        self.m_pos.append([x1, y1]) # src point
        self.m_pos.append([x2, y2]) # dst point
        self.m_width = 3
        self.m_fill = 'green'

    # delete a route
    def event_delete_route(self, x1, y1, x2, y2):
        self.m_pos.append([x1, y1]) # src point
        self.m_pos.append([x2, y2]) # dst point
        self.m_width = 3
        self.m_fill = 'black'

# draw class
class Draw_map:
    m_tk=None
    m_canvas=None
    m_btn_stop=None
    m_bg='white'
    m_working=True
    m_event_pipe=None
    m_draw_thd=None
    m_lock=True

    def __def__(self):
        self.quit()

    def __init__(self, _w, _h, _bg = 'white'):
        self.m_tk = Tk()
        self.m_tk.title('DSR simulation')
        self.m_canvas = Canvas(self.m_tk, width = _w, height = _h, bg=_bg)
        self.m_btn_stop = Button(self.m_tk, text='Stop')
        self.m_bg = _bg
        self.m_working = True
        self.m_lock = False
        self.m_event_pipe = None
        self.m_draw_thd = None
        self.m_canvas.pack()

    # draw node 
    def draw_point(self, _x=0, _y=0, _r=0, _fill=None, _outl=None, _width=None, _dash=None):
        self.m_canvas.create_oval(_x-_r, _y-_r, _x+_r, _y+_r, fill=_fill, outline=_outl, width = _width, dash = _dash)
        self.m_tk.update()
    
    # handle a node event
    def handler_node(self, event_msg):
        _pos = event_msg.m_pos[0]
        self.draw_point(_x=_pos[0], _y=_pos[1], _r=event_msg.m_point_sz, _fill=event_msg.m_fill, _dash=event_msg.m_dash, _outl=event_msg.m_outl)

    #add a edge
    def draw_edge(self, _pos_1, _pos_2, _fill=None, _width=None, _dash=None):
        self.m_canvas.create_line(_pos_1[0], _pos_1[1], _pos_2[0], _pos_2[1], fill=_fill, width=_width, dash=_dash)
        self.m_tk.update()

    # handle a edge event
    def handler_edge(self, event_msg):
        self.draw_edge(_pos_1=event_msg.m_pos[0], _pos_2=event_msg.m_pos[1], _fill=event_msg.m_fill, _width=event_msg.m_width, _dash=event_msg.m_dash)
    
    #keep map visiable
    def show_loop(self):
        self.m_tk.mainloop()

    #remove all
    def remove_all(self):
        self.m_canvas.delete("all")
    
    #rebuild all
    def build_all(self):
        self.m_canvas.pack()
        self.m_btn_stop.pack()

    #bind double-click event
    def bind_dbc(self, call_back):
        self.m_canvas.bind("<Double-Button-1>", call_back)

    #bind btn_stop press event
    def bind_btn_stop(self, call_back):
        self.m_btn_stop.bind("<Button-1>", call_back)

    #process event
    def process_one_event(self, event_msg):
        if event_msg.m_type == 'oval':
            # print("Node event")
            self.handler_node(event_msg)
        elif event_msg.m_type == 'edge':
            # print("Edge event")
            self.handler_edge(event_msg)

    #set event pipe
    def set_event_pipe(self, _pipe):
        self.m_event_pipe = _pipe

    #lunch work
    def lunch_work(self):
        self.m_draw_thd = threading.Thread(target = Draw_map.main_loop, args=(self,))
        if self.m_draw_thd is None:
            print("Draw module lunch work fail")
        else:
            print("[Lunch draw map module]")
            self.m_draw_thd.start()

    #work loop
    def main_loop(self):
        print("Draw module : I'am ready")
        while self.m_working:
        
            # receive all msgs
            event_msgs = self.m_event_pipe.recv_all()

            if len(event_msgs) > 0:
                for _event in event_msgs:
                    # print("Msg from %s"%(_event.m_src))
                    # when lock, only react to Map
                    # when unlock, react to Map and node
                    if (not self.m_lock) or (self.m_lock and _event.m_src == 'Map'):
                        self.process_one_event(_event)
                    

    #unlock
    def unlock(self):
        self.m_lock = False

    #lock
    def lock(self):
        self.m_lock = True

    #quit
    def quit(self):
        self.m_lock = False
        self.m_working = False
        self.m_draw_thd.join()
        print("[Draw module quit]")