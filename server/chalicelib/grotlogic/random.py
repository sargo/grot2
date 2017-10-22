import base64
import binascii
import random

from ..utils import timeit


class DenseStateRandom(random.Random):
    """
    A Random class with match smaller state size but setstate will
    have to compute many randoms to recreate the state
    """
    _counter = 0
    _seed = None

    def __init__(self, seed=None):
        self._seed = seed
        super().__init__(seed)

    def random(self):
        self._counter += 1
        return super().random()

    def getstate(self):
        return '{}-{}'.format(self._seed, self._counter)

    @timeit
    def setstate(self, state):
        seed, counter = state.split('-')
        self._seed = int(seed)

        # reset to initial state
        self.seed(self._seed)
        self._counter = 0

        # run random the same times
        for i in range(int(counter)):
            self.random()