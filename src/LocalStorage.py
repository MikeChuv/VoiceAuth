from __future__ import annotations
import sys
if sys.version_info > (3, 8, 3):
    import pickle
else:
    import pickle5 as pickle

import logging

import env
from Users import Users
from UserAccount import Admin
from Singleton import Singleton

class LocalStorage(metaclass=Singleton):

    def __init__(self, users : Users, threshold : float, recordsCount : int, minDistance : float):
        self.users = users
        self.threshold = threshold
        self.recordsCount = recordsCount
        self.minDistance = minDistance
        # TODO add min dustance between users

    def save(self, filename : str):
        with open(filename + '.pickle', 'wb') as outfile:
            pickle.dump(self, outfile, protocol=pickle.HIGHEST_PROTOCOL)

    
    @classmethod
    def load(cls, filename : str) -> LocalStorage:
        try:
            with open(filename + '.pickle', 'rb') as infile:
                obj = pickle.load(infile)
                Singleton.add(cls, obj)
                # cls.__class__._instances[cls] = obj
                return obj
        except FileNotFoundError:
            logging.info(f'[LocalStorage] File not found: {filename}.pickle, constructing default...')
            users = Users()
            users[env.DEFAULT_ADMIN] = Admin(env.DEFAULT_ADMIN)
            threshold = 3
            recordsCount = 3
            minDistance = 2
            return cls(users, threshold, recordsCount, minDistance)
