from unittest import TestCase

from ..random import DenseStateRandom


class DenseStateRandomTestCase(TestCase):

    def setUp(self):
        self.random = DenseStateRandom(0)

    def test_random_choice(self):
        initial_state = self.random.getstate()

        first_run = [
            self.random.choice(range(10))
            for i in range(10)
        ]
        self.random.setstate(initial_state)
        second_run = [
            self.random.choice(range(10))
            for i in range(10)
        ]
        self.assertListEqual(first_run, second_run)