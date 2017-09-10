import random

class RandomAgent(object):

    def __init__(self, player):
        self.player = player
        self.name = 'Random'

    # potez se bira slucajno iz liste svih mogucih pokreta (moves)
    def get_action(self, moves, game=None):
        return random.choice(list(moves)) if moves else None
