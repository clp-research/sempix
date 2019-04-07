# -*- coding: utf-8 -*-

'''The environment controller for MapWorld.
'''

from transitions import Machine
from IPython.display import display, Image


class MapWorld(object):
    '''The MapWorld environment. State machine for one agent.

    Tries to be general in what it returns when entering a new state.
    This is specified by the list of node_descriptors, which are fields
    in the dictionaries describing the nodes / states / rooms.
    '''
    def __init__(self, map_, node_descriptors):
        self.machine = Machine(model=self,
                               states=[str(this_node['id']) for this_node in map_['nodes']],
                               transitions=map_['transitions'],
                               ignore_invalid_triggers=True,
                               initial=map_['initial'])
        self.nodes = map_['nodes']
        self.node_descriptors = node_descriptors

    def _get_node(self, id_):
        for this_node in self.nodes:
            if str(this_node['id']) == id_:
                return this_node

    def describe_node(self, state):
        out = {}
        for descriptor in self.node_descriptors:
                out[descriptor] = (self._get_node(state)[descriptor])
        return (out, [t for t in self.machine.get_triggers(state)
                      if t in 'n s e w'.split()])

    def try_transition(self, trigger):
        if trigger not in self.machine.get_triggers(self.state):
            return (None,
                    [t for t in self.machine.get_triggers(self.state)
                     if t in 'n s e w'.split()])
        else:
            self.trigger(trigger)
            return self.describe_node(self.state)


class MapWorldWrapper(object):
    '''A convenience wrapper around MapWorld, for use in notebook.

    Can show images realising the instances, in which case the URL
    is expected to be in "instance" in the node / state / room
    dictionaries (via the node_descriptors mechanism of MapWorld).
    '''
    def __init__(self, map_, node_descriptor=['instance'], show_image=False,
                 image_prefix=None):
        self.map = map_
        self.mw = MapWorld(map_.to_fsa_def(), node_descriptor)
        self.show_image = show_image
        self.image_prefix = image_prefix
        # need to describe the initial state as well
        self.describe_state(self.mw.state, show_image=show_image)

    def describe_state(self, state, show_image=False):
        description, avail_dirs = self.mw.describe_node(state)
        if show_image:
            image_path = self.image_prefix + '/' + description['instance']
            display(Image(filename=image_path, width=400, height=400))
        else:
            print(description)
        self.print_dirs(avail_dirs)

    def print_dirs(self, avail_dirs):
        out_string = 'You can go: {}'.format(' '.join(avail_dirs))
        print(out_string)

    def upd(self, command):
        if command == 'l':  # look: repeat directions, but don't
            # show image again
            self.describe_state(self.mw.state, show_image=False)
        elif command in 'n s e w'.split():
            description, avail_dirs = self.mw.try_transition(command)
            if description is None:  # transition failed
                print('Nothing happened.')
                self.describe_state(self.mw.state, show_image=False)
            else:
                self.describe_state(self.mw.state, show_image=self.show_image)

    def plt(self):
        self.map.plot_graph(state=eval(self.mw.state))
