#!/usr/bin/env python3
#%%
import numpy as np
from numpy.random import permutation
from collections import namedtuple
from scipy.spatial import distance_matrix
from tkinter import *


class Region():

    Map_dim = namedtuple('Map_dim', ['x', 'y', 'color'])

    def __init__(self, image):
        self.region = mpimg.imread(image)
        self.image_origin = image
        self.dim = Region.Map_dim(*(self.region.shape))
        self.player_coord = np.array([[self.dim.y // 2 + 30, self.dim.x // 2 - 15]])

    def __eq__(self, other):
        if(self.image_origin == other.image_origin):
            return True
        else:
            return False


class Locations():

    def __init__(self, chat_log, num=None):
        pass


class Tsp():
    ''' Class that creates the population for a Genetic Algorithm.
        Currently there is no GA implemented, the first generation though
        is already there and consist of tours which are determined via the 
        (greedy) nearest neighbour algorithm. There is one tour for every
        possible starting point, thus there are already some really good 
        tours present.
    '''

    def __init__(self, locations, start_eq_end=True, pop_size=10):
        ''' start_eq_end : If true the distance, fitness and propability calculation
                           take a last edge from the current last to the first point
                           into account.
            locations    : Is a list or array type wich contains points in 2D-space.
                           which are visited once (or twice if tour ends where it began)
        '''
        self.start_eq_end = start_eq_end
        self.num_loc = len(locations)
        self.ptp_dists = distance_matrix(locations, locations)
        self.nn_lut = np.array([np.argsort(dists)[1:] for dists in self.ptp_dists])
        self.pop = np.array([self.nearest_neighbour(i) for i in range(self.num_loc)])
        self.dists = self.calc_dists()
        self.calc_fitnesses()
        self.calc_probabiltys()
    
    def calc_dists(self):
        dists = np.zeros(len(self.pop))
        for k, tour in enumerate(self.pop):
            for i, j in zip(tour, tour[1:]):
                dists[k] += self.ptp_dists[i][j]
            if(self.start_eq_end):
                dists[k] += self.ptp_dists[-1][0]
        return dists

    def calc_fitnesses(self):
        self.fitnesses = 1 / self.dists

    def calc_probabiltys(self):
        self.probabiltys = self.fitnesses / np.sum(self.fitnesses)

    def nearest_neighbour(self, node):
        ''' create an array representing the tour, which will contain the order of indices.
        '''
        tour = np.full(self.num_loc, self.num_loc, dtype = np.int32)
        tour[0] = node
        for i in range(1, len(tour)):
            for n in self.nn_lut[tour[i - 1]]:
                if(np.all(tour != n)):
                    tour[i] = n
                    break
        tour = np.roll(tour, - np.argmin(tour))
        return tour

    def pick_trip(self):
        ran = np.random.random()
        i = 0
        while(ran > 0):
            ran -= self.probabiltys[i]
            i += 1
        return self.pop[i-1]

    def shortest_trip(self):
        st = np.argmax(self.fitnesses) 
        return self.pop[st]

    #def create_new_generation(self, kind='mutation', rate=0.5):
    #    tmp = self.pop
    #    for i in range(len(self.new_pop)):
    #        if(kind == 'mutation'):
    #            self.new_pop[i] = Trip.mutate_trip(self.pick_trip(), rate)
    #        if(kind == 'crossover'):
    #            self.new_pop[i] = Trip.cross_trips((self.pick_trip(), self.pick_trip()))
    #    self.pop = self.new_pop
    #    self.new_pop = tmp
    #    self.calc_fitnesses()
    #    self.calc_probabiltys()


root = Tk()
root.title = ('Project:Gordon Survey Tool')
canvas = Canvas(width = 1500, height = 1500, bg='black')
canvas.pack()
region = PhotoImage(file = 'serbule_map.png')
canvas.create_image(region.width() // 2, region.height() // 2,  image = region)
root.mainloop()

#num_surveys = 100
#
#
#serb = Region('serbule_map.png')
#surveys = np.random.randint(0, 1434, (num_surveys, 2))
#locations = np.concatenate((serb.player_coord, surveys))
#pop = Population(serb, locations, pop_size = len(locations))
#
#ax= plt.subplot(111, frameon=False)
#ax.set_xticks([])
#ax.set_yticks([])
#
#shortest_trip = np.array([np.array(locations[i]) for i in pop.shortest_trip()])
#shortest_trip = np.append(shortest_trip, serb.player_coord).reshape(num_surveys + 2, 2)
#
#plt.imshow(serb.region)
#ax.plot(shortest_trip.T[0], shortest_trip.T[1])
#plt.show()
#

#%%
