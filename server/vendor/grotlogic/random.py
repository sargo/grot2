import base64
import binascii
import random


class DenseStateRandom(random.Random):
    """
    A Random class with dense state.
    """

    def getstate(self):
        def _pack(number):
            text = hex(number)[2:]
            if len(text) % 2:
                text = '0' + text
            return base64.a85encode(binascii.unhexlify(text)).decode()

        return ' '.join(map(_pack, super().getstate()[1]))

    def setstate(self, state):
        def _unpack(text):
            return int(binascii.hexlify(base64.a85decode(text)).decode(), 16)

        return super().setstate(
            [self.VERSION, tuple(map(_unpack, state.split(' '))), None])