#!/usr/bin/env python3

import datetime
from pathlib import Path
import re
import tkinter as tk
import numpy as np
from threading import Thread
import time
from matplotlib.figure import Figure
from matplotlib import image as mpl_image
from matplotlib.animation import FuncAnimation
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from tsp import tsp_solver


default_dir = Path.home() / Path('.config/unity3d/Elder Game/Project Gorgon/ChatLogs')

class Model():

    _guard_pattern = re.compile(r'^\d{2}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\s\[Status\]')
    _dist_pattern  = re.compile(r'\d{1,4}m')

    def __init__(self, directory = default_dir):
        self.directory = directory
        self.chat_log = self._current_chat_log()
        locations = self.parse_chat(50)
        self.locations = np.concatenate(([[0,0]], locations))
        self.tsp = tsp_solver(self.locations)
        self.shortest_graph = self.tsp.two_opt()

    def parse_chat(self, num=None):
        with open(self.chat_log, 'r') as f:
            loc = []
            for line in f:
                if self._guard_pattern.match(line):
                    coord = [int(dist[:-1]) for dist in self._dist_pattern.findall(line)]
                    if 'west' in line:
                        coord[0] *= -1
                    if 'north' in line:
                        coord[1] *= -1
                    if(len(coord) == 2):
                        loc.append(coord)
            print(len(loc))
            return np.array(loc)
            if num is not None:
                return np.array(loc[-1 * num:])
                #print(len(loc[-1 * (num - 2): -2]))
                #return np.array(loc[-1 * (num - 2): -2])
            else:
                return np.array(loc[:-80])

    def _current_chat_log(self):
        d = datetime.datetime.now()
        chat_log = 'Chat-{:02d}-{:02d}-{:02d}.log'.format(d.year - 2000, d.month, d.day)
        return self.directory / Path(chat_log)

    def next_spot(self):
        tmp = np.copy(self.shortest_graph[1:-1])
        for _ in range(len(tmp)):
            ret = tmp[0]
            tmp[tmp > ret] -= 1
            tmp = tmp[1:]
            yield ret


class View(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.data = np.array([])
        self.scale = 1
        self.image = ''
        self.inventory_cols = 10
        self.current_loc = -1

        self.fig = Figure()
        self.fig.patch.set_facecolor('#222222')
        self.ax = self.fig.add_subplot(111, frameon=False)
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.inventory = tk.Frame(master)
        self.inventory.config(bg = '#222222')
        self.inventory.pack(side = tk.RIGHT)

        self.update_inv = tk.Button(self.inventory, text = 'Next', bg = '#a9a9a9', highlightthickness = 0)
        self.update_inv.pack()

        self.next_item = tk.Label(self.inventory, text = 'Next: \nFound in\nrow: \ncol: ')
        self.next_item.config(bg = '#222222',fg = '#a9a9a9', font = ('Helvetica', 13))
        self.next_item.pack(padx = 40, pady = 20)

    def init_graph(self):
        self.ax.cla()
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.imshow(mpl_image.imread(self.image))
        x, y = self.scale * self.data.swapaxes(0, 1)
        self.ax.plot(x, y, lw=3, zorder = 1)
        self.ax.scatter(x, y, c='r', zorder = 2)

    def animate_graph(self):
        x, y = self.scale * self.data.swapaxes(0, 1)
        new_scatter = lambda _ : self.ax.scatter(x[self.current_loc], y[self.current_loc], c='g', zorder = 3)
        _ = FuncAnimation(self.fig, new_scatter, init_func = self.init_graph, interval = 10)
        self.canvas.draw()

    def update_control(self, num):
        self.next_item.config(text = 'Next: {}\nFound in\nrow: {}\ncol: {}'.format(
            num, (num - 1) // self.inventory_cols + 1, (num - 1) % self.inventory_cols + 1))
        self.current_loc += 1


class Controller():

    def __init__(self, master, model, view, regions):
        self.model = model
        self.view = view
        self.survey_map = self.model.next_spot()
        self.view.update_inv.config(command = lambda: self.view.update_control(next(self.survey_map)))
        self.regions = regions
        self.foo()

    def foo(self):
        self.view.scale = regions['Serbule'].scale
        data = np.array([self.model.locations[i] for i in self.model.shortest_graph])
        self.view.data = data + self.regions['Serbule'].landmarks['Well']
        self.view.image = self.regions['Serbule'].image
        self.view.animate_graph()


class Region():
    ''' This class holds all the information required by the GUI to display
        a region.
    '''
    # image     : is a png file (string)
    # scale     : pixel per meter (or whatever unit of measurement)
    # landmarks : is a dictionary linking landmarks to coordinates

    def __init__(self, image, scale, landmarks):
        self.image = image
        self.scale = scale
        self.landmarks = landmarks


serb = Region('serbule_map.png', 602 / 1000,
              {'Well' : (np.array([[746, 734]]) * 1000 / 602).astype(int)})

regions = {'Serbule' : serb}

bar = 42


def observe_chat(**kwargs):
    time.sleep(2)
    # another hotfix
    #_survey_found_pattern = re.compile(r'^\d{2}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\s\[Status\] Rubywall Crystal ((\b\w*\b) added to inventory.|added to inventory.)')
    _survey_found_pattern = re.compile(r'^\d{2}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\s\[Status\] You earned 25 XP in Geology.')
    _timestamp_pattern = re.compile(r'^\d{2}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
    file = open(kwargs['model'].chat_log)
    while file.readline():
        pass
    survey_map = kwargs['model'].next_spot()
    num_iter = kwargs['num_it']
    kwargs['view'].update_control(next(survey_map))
    num_iter = len(kwargs['model'].shortest_graph)
    current_survey_node_ts = 60 # this is 60 seconds so it would've normally wrapped around
    while num_iter:
        line = file.readline()
        match = _survey_found_pattern.match(line)
        if match:
            next_survey_node_ts = int(_timestamp_pattern.match(line)[0][-2:])
            if current_survey_node_ts != next_survey_node_ts:
                kwargs['view'].update_control(next(survey_map))
                num_iter -=1
                time.sleep(0.3)        
        else:
            time.sleep(0.05)        
    file.close()


def main():
    root = tk.Tk()
    root['bg'] = '#222222'
    root.title('Project:Gorgon Survey Tool')
    model = Model()
    view = View(root)
    controller = Controller(root, model, view, regions)
    chat_parser_thread = Thread(target=observe_chat, 
                                kwargs={'num_it': 80, 'view': view, 'model': model, 'controller': controller})
    chat_parser_thread.start()
    root.mainloop()


if __name__ == "__main__":
    main()
