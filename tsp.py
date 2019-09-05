import random
import numpy as np
from numpy.random import permutation
from scipy.spatial import distance_matrix


class tsp_solver():
    ''' This class contains several methods for solving the TSP.
        most methods are meant only for internal use. This Class
        also provides multiple alternative ways to obtain a
        short graph, however it offers only heuristical methods,
        so the result will likely not be THE optimal graph.
        __________________________________________________________

        Heuristic approximations available are:
            
            - nearest neighbour
            - 2-opt

        planned:

            - 3-opt
            - k-opt (Kernighan - Lin)
            - genetic algorithm
    '''

    def __init__(self, locations, start_eq_end=True, pop_size=10):
        ''' start_eq_end : Takes returning to first element in the Graph
                           into account. The first element will correspond to
                           the first element of the array passed as 'locations'
            locations    : Is a list or array type wich contains points in 2D-space.
                           which are visited once.
            pop_size     : Placeholder for the genetic algorithm, currently not in use.
        '''
        
        # Dev comments:
        # ptp_dists (point to point distances) is a N x N Matrix containing the
        #           distances from every point to every other point in self.locations
        # nn_lut    (neares neighbour look up table) is a N x N Matrix containing the
        #           order of nearest points for any point in self.locations
        # pop       (population) set of graphs considered for further optimizations
        #           originally meant for not yet implemented genetic algorithm
        #           now just a collection
        # dists     distance corresponding to the graph in self.pop
        self.start_eq_end = start_eq_end
        if start_eq_end:
            self.locations = np.concatenate((locations, [locations[0]]))
        else:
            self.locations = locations
        self.num_loc = len(locations)
        self.ptp_dists = distance_matrix(locations, locations)
        self.nn_lut = np.array([np.argsort(dists)[1:] for dists in self.ptp_dists])
        self.pop = np.array([self.nearest_neighbour(i) for i in range(self.num_loc)])
        self.dists = self.calc_dists()
        self.calc_fitnesses()
        self.calc_probabiltys()

    def dist(self, tour):
        dist = 0
        for i, j in zip(tour, tour[1:]):
            dist += self.ptp_dists[i][j]
        return dist
    
    # notice that plural indicates that it corresponds to the population
    def calc_dists(self):
        dists = np.zeros(len(self.pop))
        for k, tour in enumerate(self.pop):
            dists[k] = self.dist(tour)
        return dists

    # notice that plural indicates that it corresponds to the population
    def calc_fitnesses(self):
        self.fitnesses = 1 / self.dists

    # notice that plural indicates that it corresponds to the population
    def calc_probabiltys(self):
        self.probabiltys = self.fitnesses / np.sum(self.fitnesses)

    def nearest_neighbour(self, node):
        ''' create an array representing the graph, which will contain the order of indices.
            Always pick the nearest available neighbour to current node
        '''
        tour = np.full(self.num_loc, self.num_loc, dtype = np.int32)
        tour[0] = node
        for i in range(1, len(tour)):
            for n in self.nn_lut[tour[i - 1]]:
                if(np.all(tour != n)):
                    tour[i] = n
                    break
        tour = np.roll(tour, - np.argmin(tour))
        if(self.start_eq_end):
            tour = np.concatenate((tour, [0]))
        return tour

    def pick_graph(self):
        ran = np.random.random()
        i = 0
        while(ran > 0):
            ran -= self.probabiltys[i]
            i += 1
        return self.pop[i-1]

    @staticmethod
    def two_opt_swap(tour, i=None, j=None):
        if i is None:
            i = random.randint(1, len(tour[1:-1]))
        if i is None:
            i = random.randint(i + 1, len(tour[1:-1]))
        return np.concatenate((tour[:i], tour[j-1:i-1:-1], tour[j:]))

    # 2-opt Algorithm adapted from here https://en.wikipedia.org/wiki/2-opt
    # and here https://stackoverflow.com/questions/25585401/travelling-salesman-in-scipy
    def two_opt(self, improvement_threshold=0.01):
        tour = self.shortest_graph
        improvement_factor = 1
        best_distance = self.dist(tour)
        while improvement_factor > improvement_threshold:
            distance_to_beat = best_distance
            for i in range(1, len(tour[1:-1])):
                for j in range(i + 1, len(tour[:-1])):
                    new_tour = self.two_opt_swap(tour, i, j)
                    new_dist = self.dist(new_tour)
                    if new_dist < best_distance:
                        tour = new_tour
                        best_distance = new_dist
            improvement_factor = 1 - best_distance / distance_to_beat
        print(self.dist(tour))
        print(self.dist(self.shortest_graph))
        return tour

    @property
    def shortest_graph(self):
        st = np.argmax(self.fitnesses) 
        return self.pop[st]

    #def create_new_generation(self, kind='mutation', rate=0.5):
    #    tmp = self.pop
    #    for i in range(len(self.new_pop)):
    #        if(kind == 'mutation'):
    #            self.new_pop[i] = Trip.mutate_trip(self.pick_graph(), rate)
    #        if(kind == 'crossover'):
    #            self.new_pop[i] = Trip.cross_trips((self.pick_graph(), self.pick_graph()))
    #    self.pop = self.new_pop
    #    self.new_pop = tmp
    #    self.calc_fitnesses()
    #    self.calc_probabiltys()