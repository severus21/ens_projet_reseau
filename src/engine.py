import logging
import socket
import pickle

from collections import deque
from random import getrandbits

class Engine:

    def __init__(self, path=None):
        """
        @param path - path to store program data for recovery
        """
        self.path = path

        if path:
            self.load()
