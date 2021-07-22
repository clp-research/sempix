# -*- coding: utf-8 -*-

'''Map objects for the map world environment.

AbstractMap encapsulates generation of graph through random walk.
ADEMap is an example of a fully specified map, where nodes in the graph
are adorned with additional information (here: room categories and room
instances [images] from the ADE20k dataset.

ADEMap needs to know the mapping between categories and instances (files
from the corpus). This is pre-compiled in ade_cat_instances.json.gz.
If that is missing, run make_and_write_instance_list() (for which you
need to have the corpus available).
'''

# TODO:
# - use visual similarity to sample maximally confusable images from
#   target type.


import numpy as np
import networkx as nx

from glob import glob
import json
import gzip
import os
import matplotlib.pyplot as plt


class AbstractMap(object):
    '''Map graph, created with random walk.

    Arguments:
      n: number of rows of grid for random walk
      m: number of columns of grid for random walk
      n_rooms: how many rooms to create

    Attributes:
      G: the created map graph. (A networkX graph.)

    n*m must be larger than n_rooms. The larger it is, the more freedom
    the random walk has to walk in one direction, and the less compact
    the resulting layout gets.

    This walks by first creating an n*m matrix, and then randomly walking
    around it until the required number of rooms has been created.
    '''
    dir2delta = {'n': np.array((-1, 0)),
                 's': np.array((1, 0)),
                 'e': np.array((0, 1)),
                 'w': np.array((0, -1))}

    def __init__(self, n, m, n_rooms):
        if n*m < n_rooms:
            raise ValueError('n*m must be larger than n_rooms')
        self.n = n
        self.m = m
        self.n_rooms = n_rooms
        self.G = self.make_graph(n, m, n_rooms)

    def make_graph(self, n, m, n_rooms):
        map_array = np.zeros((n, m))
        G = nx.Graph()

        current_pos = np.random.randint(0, n), np.random.randint(0, m)
        map_array[current_pos] = 1
        G.add_node(current_pos)

        while map_array.sum() < n_rooms:
            random_dir = np.random.choice(['n', 's', 'e', 'w'])
            new_pos = tuple(np.array(current_pos) + self.dir2delta[random_dir])
            if min(new_pos) < 0 or new_pos[0] >= n or new_pos[1] >= m:
                # illegal move
                continue
            map_array[new_pos] = 1
            G.add_node(new_pos)
            G.add_edge(current_pos, new_pos)
            current_pos = new_pos
        return G

    def plot_graph(self):
        nx.draw_networkx(self.G, pos={n: n for n in self.G.nodes()})

    def __repr__(self):
        return '<AbstractMap({}, {}, {})>'.format(self.n, self.m, self.n_rooms)


class ADEMap(AbstractMap):
    '''Create map for the ADEworld.

    Map filled with selected types from ADE20k. We selected some categories
    that seemed more common and potentially easier to describe. (For some
    games, these might serve as target rooms.) Additionally, we identified
    some categories that can serve as fillers. Finally, we have "outdoors"
    categories.

    Arguments:

      n: number of rows of grid for random walk  [from AbstracMap]
      m: number of columns of grid for random walk  [from AbstracMap]
      n_rooms: how many rooms to create [from AbstracMap]
      target_type_distr: list of integers, controls ambiguity (see below).

    or None. (Then init via .from_json().)

    Some rooms are identified as "outdoors". These are rooms with degree 1,
    that is, rooms that are connected to only one other one. Think of these
    as the entries into the house.

    Let's say target_type_distr is (3,2). This means that we will have (at
    least) two types from the list of potential target categories, and that
    the first of these will occur three times, and the second twice. This
    controls "type ambiguity" of the map.

    N.B.: At the moment, there are no checks to ensure that there are enough
    rooms after the outdoor rooms have been assigned, so make sure that then
    sum of the rooms specified here is relatively small, to account for
    the possiblity that the remaining rooms are all outdoor rooms.

    This only assigns categories and image instances to the rooms. For other use
    cases, one could imagine textual information also being assigned to rooms.
    '''

    _target_cats = ['b/bathroom', 'b/bedroom', 'k/kitchen',
                    'b/basement', 'n/nursery', 'a/attic', 'c/childs_room',
                    'p/playroom', 'd/dining_room', 'h/home_office',
                    's/staircase', 'u/utility_room', 'l/living_room',
                    'j/jacuzzi/indoor', 'd/doorway/indoor', 'l/locker_room',
                    'w/wine_cellar/bottle_storage', 'r/reading_room',
                    'w/waiting_room', 'b/balcony/interior']

    _distractor_cats = ['h/home_theater', 's/storage_room', 'h/hotel_room',
                        'm/music_studio', 'c/computer_room', 's/street',
                        'y/yard', 't/tearoom', 'a/art_studio',
                        'k/kindergarden_classroom', 's/sewing_room',
                        's/shower', 'v/veranda', 'b/breakroom',
                        'p/patio', 'g/garage/indoor',
                        'r/restroom/indoor', 'w/workroom', 'c/corridor',
                        'g/game_room', 'p/poolroom/home', 'c/cloakroom/room',
                        'c/closet', 'p/parlor', 'h/hallway', 'r/reception',
                        'c/carport/indoor', 'h/hunting_lodge/indoor']
    # TODO: remove outdoor categories from this set? Why is there street and yard in here?

    _outdoor_cats = ['g/garage/outdoor', 'a/apartment_building/outdoor',
                     'j/jacuzzi/outdoor', 'd/doorway/outdoor',
                     'r/restroom/outdoor', 's/swimming_pool/outdoor',
                     'c/casino/outdoor', 'k/kiosk/outdoor',
                     'a/apse/outdoor', 'c/carport/outdoor',
                     'f/flea_market/outdoor', 'c/chicken_farm/outdoor',
                     'w/washhouse/outdoor', 'c/cloister/outdoor',
                     'd/diner/outdoor', 'k/kennel/outdoor',
                     'h/hunting_lodge/outdoor', 'c/cathedral/outdoor',
                     'n/newsstand/outdoor', 'p/parking_garage/outdoor',
                     'c/convenience_store/outdoor', 'b/bistro/outdoor',
                     'i/inn/outdoor', 'l/library/outdoor']

    # not sure the following is the python way to do this... this is a
    # class attribute, so at least this is only done once...
    if not os.path.isfile('ade_cat_instances.json.gz'):
        raise FileNotFoundError('"ade_cat_instance.json.gz" not found. Run make_and_write_instance_list.py?')
    with gzip.open('ade_cat_instances.json.gz', 'rb') as f:
        _cat_instances_bytes = f.read()
        _cat_instances_str = _cat_instances_bytes.decode('utf-8')
        _cat_instances = json.loads(_cat_instances_str)

    def __init__(self, *args):
        if len(args) > 0:
            n, m, n_rooms, target_type_distr = args
            AbstractMap.__init__(self, n, m, n_rooms)
            self.assign_types(target_type_distr)
            self.assign_instances()
        else:
            pass

    def assign_types(self, target_type_distr):
        G = self.G

        outdoor = [this_node for this_node in G.nodes() if G.degree[this_node] == 1]
        # assign outdoor cats to those
        for this_node in outdoor:
            G.nodes[this_node]['base_type'] = 'outdoor'
            G.nodes[this_node]['type'] = np.random.choice(self._outdoor_cats)
            G.nodes[this_node]['target'] = False

        unassigned = [this_node for this_node in G.nodes() if G.degree[this_node] > 1]

        target_types = np.random.choice(self._target_cats,
                                        len(target_type_distr), replace=False)
        for target_type, repetitions in zip(target_types, target_type_distr):
            for _ in range(repetitions):
                try:
                    this_node = unassigned[np.random.choice(range(len(unassigned)))]
                    G.nodes[this_node]['base_type'] = 'indoor'
                    G.nodes[this_node]['type'] = target_type
                    G.nodes[this_node]['target'] = True
                    unassigned.remove(this_node)
                except:
                    # skip the room type assignment if no unassigned rooms are left
                    pass
        remainder_types = list(set(self._target_cats)
                               .difference(set(target_types))
                               .union(set(self._distractor_cats)))
        for this_node in unassigned:
            G.nodes[this_node]['base_type'] = 'indoor'
            G.nodes[this_node]['type'] = np.random.choice(remainder_types)
            G.nodes[this_node]['target'] = False
        self.G = G

    def assign_instances(self):
        G = self.G
        already_sampled = []
        for this_node in G.nodes():
            not_yet = True
            while not_yet:
                this_instance = np.random.choice(ADEMap._cat_instances[G.nodes[this_node]['type']])
                if this_instance not in already_sampled:
                    not_yet = False
            G.nodes[this_node]['instance'] = this_instance
        self.G = G

    def print_mapping(self):
        for this_node in self.G.nodes():
            print('{}: {} {:>50}'.format(this_node,
                                         self.G.nodes[this_node]['type'],
                                         self.G.nodes[this_node]['instance']))

    def _catname(self, category):
        parts = category.split('/')
        if parts[-1].endswith('door') or parts[-1] == 'interior':
            return parts[-2]
        else:
            return parts[-1]

    def plot_graph(self, nodes='types', state=None):
        G = self.G
        nx.draw_networkx(G, pos={n: n for n in G.nodes()}, with_labels=False,
                         node_color='blue', node_shape='s')
        for this_node in G.nodes():
            x, y = np.array(this_node) + np.array((-0.2, 0.2))
            if nodes == 'types':
                label = self._catname(G.nodes[this_node]['type'])
            elif nodes == 'inst':
                label = G.nodes[this_node]['instance']
            plt.text(x, y, label)
        if state is not None:
            nx.draw_networkx_nodes(G,
                                   pos={n: n for n in G.nodes()},
                                   with_labels=False,
                                   node_color='red',
                                   node_shape='s',
                                   nodelist=[state])
        plt.axis('off')

    def to_json(self):
        return nx.json_graph.node_link_data(self.G)

    @classmethod
    def from_json(cls, map_json):
        '''Construct map object from json serialisation.

        Example:
           map = ADEMap.from_json(PATH_TO_JSON)
        '''
        new_instance = cls()
        new_instance.G = nx.json_graph.node_link_graph(map_json)
        return new_instance

    def to_fsa_def(self, pick_initial=True):
        this_json = self.to_json()
        # transitions
        transitions = this_json['links']
        dir2delta = {'n': np.array((0, 1)), 's': np.array((0, -1)),
                     'e': np.array((1, 0)), 'w': np.array((-1, 0))}
        # N.B.: the interpretation of the coordinates has suddenly
        # changed, compared to AbstracMap.. There, the numpy convention
        # was used (row, column). Here, it is now (x, y). Doesn't
        # really matter semantically; I've adapted this here as this
        # is how it is interpreted visually when plotting the graph.
        flip_dir = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
        out_transitions = []
        for this_transition in transitions:
            for d, o in dir2delta.items():
                if np.array_equal(np.array(this_transition['target']),
                                  np.array(this_transition['source']) + o):
                    out_transitions.append({'source':
                                            str(this_transition['source']),
                                            'dest':
                                            str(this_transition['target']),
                                            'trigger': d})
                    out_transitions.append({'source':
                                            str(this_transition['target']),
                                            'dest':
                                            str(this_transition['source']),
                                            'trigger': flip_dir[d]})
                    break
        # nodes
        nodes = this_json['nodes']
        # pick initial
        if pick_initial:
            initial_node = np.random.choice([node for node in nodes if node['base_type'] == 'outdoor'])
            # TODO: make selection of initial more flexible?
            initial = str(initial_node['id'])
            initial_type = initial_node['type']
        else:
            initial, initial_type = None, None
        return {'transitions': out_transitions, 'nodes': nodes,
                'initial': initial, 'initial_type': initial_type}


def make_instance_list(ade_path, categories):
    place_instances = {}
    for this_type in categories:
        full_paths = glob(ade_path + this_type + '/*.jpg')
        place_instances[this_type] = ['/'.join(this_path.split('/')
                                               [len(ade_path.split('/'))-1:])
                                      for this_path in full_paths]
    return place_instances


def make_and_write_instance_list(ade_path, filename):
    place_instances = make_instance_list(ade_path,
                                         ADEMap._target_cats +
                                         ADEMap._distractor_cats +
                                         ADEMap._outdoor_cats)
    with gzip.open(filename, 'w') as f:
        json_s = json.dumps(place_instances, indent=4)
        json_bytes = json_s.encode('utf-8')
        f.write(json_bytes)
