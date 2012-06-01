#!/usr/bin/env python

'''
Graph-related classes and functions.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-05-30
'''

from collections import namedtuple, defaultdict
from itertools import tee, izip

from it import nwise

Node = namedtuple('Node', ('id', 'value', ))


class Graph(object):
    def __init__(self):
        self._next_id = 0
        self._nodes = set()
        # First entry: Source node
        # Second entry: Type
        # Third entry: Target
        self._edges = defaultdict(dict)

    def add_node(self, value):
        node = Node(value=value, id=self._next_id)
        self._next_id += 1
        return node

    def add_edge(self, _from, _type, to):
        self._edges[_from][_type] = to

    # TODO: Raise exception if the walk can't be completed?
    # This is Depth-first
    def walk(self, start, search, _lbl=None, _lbl_path=None):
        if _lbl_path is None:
            _lbl_path = tuple()
        if _lbl is not None:
            yield _lbl, _lbl_path, start

        edges = self._edges[start]
        for lbl, next in edges.iteritems():
            try:
                if search.accept(lbl):
                    for res in self.walk(next, search, _lbl=lbl,
                            _lbl_path=tuple(_lbl_path + (lbl, ))):
                        yield res
                    break
            except StopGraphSearch:
                raise StopIteration
        else:
            pass # XXX: We couldn't proceed!


class GraphSearch(object):
    def accept(self, edge):
        raise NotImplementedError


class StopGraphSearch(Exception):
    pass


class SeqLblSearch(object):
    def __init__(self, seq):
        self._seq = (e for e in seq)
        self._next = next(self._seq, None)

    def __next(self):
        if self._next is None:
            raise StopGraphSearch
        self._next = next(self._seq, None)

    def accept(self, lbl):
        if lbl == self._next:
            self.__next()
            return True
        else:
            return False


def prev_next_graph(seq):
    graph = Graph()
    nodes = [graph.add_node(val) for val in seq]
    for _from, to in nwise(nodes, 2):
        graph.add_edge(_from, 'NXT', to)
    for _from, to in nwise(nodes[::-1], 2):
        graph.add_edge(_from, 'PRV', to)
    return graph, nodes

if __name__ == '__main__':
    seq = (
            'Bashful', # 0
            'Doc', # 1
            'Dopey', # 2
            'Grumpy', # 3
            'Happy', # 4
            'Sleepy', # 5
            'Sneezy', # 6
            )
    graph, nodes = prev_next_graph(seq)
    grumpy = nodes[3]

    print 'The Dwarfs were going to the mine in this order:', ', '.join(
            n.value for n in nodes)
    print 'We start from:', grumpy.value
    print 'In front of him:', ', '.join(n.value for _, _, n in graph.walk(grumpy,
        SeqLblSearch(('PRV', 'PRV', 'PRV'))))
    print 'Behind him:', ', '.join(n.value for _, _, n in graph.walk(grumpy,
        SeqLblSearch(('NXT', 'NXT', 'NXT'))))
