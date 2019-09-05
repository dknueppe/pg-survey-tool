#!/usr/bin/env python3

from pathlib import Path
import re
import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasAgg, NavigationToolbar2Tk
from PIL import Image, ImageTk
from tsp import tsp_solver


class Model():

    query_pattern = ''
    survey_patterns = {
        'Serbule Rubywall Crystall' : r'\[Status\].*'
    }

    def __init__(self, chat_log, survey_option):
        self.chat_log = chat_log
        self.query_pattern = survey_option
        locations = self.parse_chat(chat_log)
        self.locations = np.concatenate(([[0,0]], locations, [[0,0]]))
        self.tsp = tsp_solver(self.locations)

    def parse_chat(self, chat_log, num=None):
        pattern = re.compile(self.query_pattern)
        with open(chat_log, 'r') as f:
            loc = []
            for line in f:
                coord = []
                if not pattern.findall(line):
                    continue
                for word in line.split():
                    if(re.match(r'^\d{1,4}m$', word)):
                        coord.append(int(word[:-1]))
                    if (word == 'west'):
                        coord[0] *= -1
                    if (word == 'north.'):
                        coord[1] *= -1
                if (len(coord) == 2):
                    loc.append(np.array(coord))
        if num is not None:
            return np.array(loc[-1 * num:])
        else:
            return np.array(loc)


class Region():
    ''' This class holds all the information required by the GUI to display
        a region.
    '''
    # image     : is a png file
    #landmarks  : is a dictionary linking landmarks to coordinates

    def __init__(self, image, landmarks):
        self.image = image
        self.landmarks = landmarks



#__________________________________Control____________________________________
class Foo(tk.Frame):

    def __init__(self, master, region, name='', *args, **kwargs):
        self.master = master
        self.region = region
        self.name = name
        self.image = Image.open(region).resize((957, 1000))
        self.aspect_ratio = self.image.width / self.image.height
        self.render = ImageTk.PhotoImage(self.image)
        super().__init__(master, *args, **kwargs)
        self.show_image()

    def show_image(self):
        self.create_image(0, 0, image = self.render, anchor = tk.NW, tag = 'map')

    #def fit_image(self, event):
    #    self.delete('map')
    #    ar = event.width / event.height
    #    if (ar < self.aspect_ratio):
    #        ratio = self.winfo_reqwidth() / self.image.width
    #    else:
    #        ratio = self.winfo_reqheight() / self.image.height
    #    new_dim = (self.image.width * ratio, self.image.height * ratio)
    #    img = self.image.resize(new_dim)
    #    rend = ImageTk.PhotoImage(img)
    #    self.create_image(0, 0, image = rend, anchor = NW, tag = 'map')


def main():
    chatlog = 'foo.log'
    surveys = parse_chat(chatlog)
    ratio_pxpm = 602 / 1000
    serb_well = np.array([746, 734]) / ratio_pxpm
    locations = np.concatenate(([[0, 0]], surveys)) + serb_well
    routes = tsp_solver(locations)

    shortest_graph = np.array([locations[i] for i in routes.two_opt()])
    shortest_graph = shortest_graph * ratio_pxpm

    root = tk.Tk()
    root.title('Project:Gorgon Survey Tool')

    region = Region(root, 'serbule_map.png', 'Serbule', width = 957, height = 1000, bg='black')
    region.pack(side=tk.LEFT)
    loc_ordered = shortest_graph * 957 / 1434
    for point, next_point in zip(loc_ordered, np.roll(loc_ordered, -1, axis = 0)):
        region.create_line(*point, *next_point, width = 3, fill = 'blue', smooth = True)

    inventory = tk.Frame(root, width = 500, height = 1000, bg='#423930')
    inventory.pack(side=tk.RIGHT)
    
    root.mainloop()


if __name__ == "__main__":
    main()