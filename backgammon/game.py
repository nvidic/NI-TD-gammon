﻿import os
import copy
import time
import random
import numpy as np


class Game:
    LAYOUT = "0-2-o,5-5-x,7-3-x,11-5-o,12-5-x,16-3-o,18-5-o,23-2-x"
    NUMCOLS = 24
    QUAD = 6
    OFF = 'off'
    ON = 'on'
    TOKENS = ['x', 'o']

    def __init__(self, layout=LAYOUT, grid=None, off_pieces=None, bar_pieces=None, num_pieces=None, players=None):
        """
        Define a new game object
        """
        self.die = Game.QUAD
        self.layout = layout
        if grid:
            self.grid = copy.deepcopy(grid)
            self.off_pieces = copy.deepcopy(off_pieces)
            self.bar_pieces = copy.deepcopy(bar_pieces)
            self.num_pieces = copy.deepcopy(num_pieces)
            self.players = players
            return
        self.players = Game.TOKENS
        self.grid = [[] for _ in range(Game.NUMCOLS)]
        self.off_pieces = {}
        self.bar_pieces = {}
        self.num_pieces = {}
        for t in self.players:
            self.bar_pieces[t] = []
            self.off_pieces[t] = []
            self.num_pieces[t] = 0

    @staticmethod
    def new():
        game = Game()
        game.reset()
        return game

    # sta radi ovaj metod: izgleda da daje izgled table u svom formatu (matrica)
    def extract_features(self, player):
        features = []
        for p in self.players:
            for col in self.grid:
                feats = [0.] * 6
                if len(col) > 0 and col[0] == p:
                    for i in range(len(col)):
                        feats[min(i, 5)] += 1
                features += feats
            features.append(float(len(self.bar_pieces[p])) / 2.)
            features.append(float(len(self.off_pieces[p])) / self.num_pieces[p])
        if player == self.players[0]:
            features += [1., 0.]
        else:
            features += [0., 1.]
        # -1 se koristi za unknown dimension: ovde ovo znaci, daj mi sve u jednoj vrsti, a ne znam tacno koliko kolona
        # ce to zauzeti
        # print("extract_features returns: " + str(len(np.array(features).reshape(1, -1)[0])))
        # print("extract_features returns: " + str(np.array(features).reshape(1, -1)))
        return np.array(features).reshape(1, -1)

    def roll_dice(self):
        return (random.randint(1, self.die), random.randint(1, self.die))

    def play(self, players, draw=False):
        x_roll = random.randint(1, self.die)
        o_roll = random.randint(1, self.die)

        while x_roll == o_roll:
            print("Player x rolled: " + str(x_roll))
            print("Player o rolled: " + str(o_roll) + "\n")
            x_roll = random.randint(1, self.die)
            o_roll = random.randint(1, self.die)

        print("---> Player x rolled: " + str(x_roll))
        print("---> Player o rolled: " + str(o_roll))

        roll = (x_roll, o_roll)
        self.draw()

        if x_roll > o_roll:
            # roll = (x_roll, o_roll)
            # print("Player x plays first with roll: "+str(roll))
            player_num = 0
            self.take_turn(players[player_num], roll, draw=draw)
            player_num = 1
        else:
            # roll = (o_roll, x_roll)
            # print("Player o plays first with roll: "+str(roll))
            player_num = 1
            self.take_turn(players[player_num], roll, draw=draw)
            player_num = 0

        # player_num = random.randint(0, 1)
        while not self.is_over():
            self.next_step(players[player_num], player_num, draw=draw)
            player_num = (player_num + 1) % 2
        return self.winner()

    def next_step(self, player, player_num, draw=False):
        roll = self.roll_dice()

        if draw:
            self.draw()

        self.take_turn(player, roll, draw=draw)

    def take_turn(self, player, roll, draw=False):
        if draw:
            print("---> Player {%s} rolled [%d] [%d]" % (player.player, roll[0], roll[1]))
            time.sleep(1)

        moves = self.get_actions(roll, player.player, nodups=True)
        move = player.get_action(roll, moves, self) if moves else None

        if move:
            self.take_action(move, player.player)

    def clone(self):
        """
        Return an exact copy of the game. Changes can be made
        to the cloned version without affecting the original.
        """
        return Game(None, self.grid, self.off_pieces,
                    self.bar_pieces, self.num_pieces, self.players)

    def take_action(self, action, token):
        """
        Makes given move for player, assumes move is valid,
        will remove pieces from play
        """
        # print("ATELIST: " + str(ateList) + "\n") --> # ATELIST: [0, 0, 0, 0]
        ateList = [0] * 4
        for i, (s, e) in enumerate(action):
            if s == Game.ON:
                piece = self.bar_pieces[token].pop()
            else:
                piece = self.grid[s].pop()
            if e == Game.OFF:
                self.off_pieces[token].append(piece)
                continue
            if len(self.grid[e]) > 0 and self.grid[e][0] != token:
                bar_piece = self.grid[e].pop()
                self.bar_pieces[bar_piece].append(bar_piece)
                ateList[i] = 1
            self.grid[e].append(piece)
        return ateList

    def undo_action(self, action, player, ateList):
        """
        Reverses given move for player, assumes move is valid,
        will remove pieces from play
        """
        for i, (s, e) in enumerate(reversed(action)):
            if e == Game.OFF:
                piece = self.off_pieces[player].pop()
            else:
                piece = self.grid[e].pop()
                if ateList[len(action) - 1 - i]:
                    bar_piece = self.bar_pieces[self.opponent(player)].pop()
                    self.grid[e].append(bar_piece)
            if s == Game.ON:
                self.bar_pieces[player].append(piece)
            else:
                self.grid[s].append(piece)

    def get_actions(self, roll, player, nodups=False):
        """
        Get set of all possible move tuples
        """
        moves = set()
        if nodups:
            start = 0
        else:
            start = None

        r1, r2 = roll
        if r1 == r2:  # doubles
            i = 4
            # keep trying until we find some moves
            # naci sve poteze za roll npr. 4, 4, 4, 4
            while not moves and i > 0:
                self.find_moves(tuple([r1] * i), player, (), moves, start)
                i -= 1
        else:
            # naci za roll (r1, r2)
            self.find_moves(roll, player, (), moves, start)
            self.find_moves((r2, r1), player, (), moves, start)
            # has no moves, try moving only one piece
            if not moves:
                for r in roll:
                    self.find_moves((r,), player, (), moves, start)

        return moves

    def find_moves(self, rs, player, move, moves, start=None):
        if len(rs) == 0:
            moves.add(move)
            return
        r, rs = rs[0], rs[1:]

        if player == "o":
            # see if we can remove a piece from the bar
            if self.bar_pieces[player]:
                if self.can_onboard(player, r):
                    # skidamo piece sa bar-a
                    piece = self.bar_pieces[player].pop()
                    bar_piece = None
                    # izbacujemo protivnika
                    if len(self.grid[r - 1]) == 1 and self.grid[r - 1][-1] != player:
                        bar_piece = self.grid[r - 1].pop()

                    # stavljamo nas piece na mesto protivnika ili na slobodno mesto ako protivnik nije bio tu
                    self.grid[r - 1].append(piece)

                    self.find_moves(rs, player, move + ((Game.ON, r - 1),), moves, start)
                    self.grid[r - 1].pop()
                    self.bar_pieces[player].append(piece)
                    if bar_piece:
                        self.grid[r - 1].append(bar_piece)
                return

            # otherwise check each grid location for valid move using r
            offboarding = self.can_offboard(player)

            for i in range(len(self.grid)):
                if start is not None:
                    start = i
                if self.is_valid_move(i, i + r, player):

                    piece = self.grid[i].pop()
                    bar_piece = None
                    if len(self.grid[i + r]) == 1 and self.grid[i + r][-1] != player:
                        bar_piece = self.grid[i + r].pop()
                    self.grid[i + r].append(piece)
                    self.find_moves(rs, player, move + ((i, i + r),), moves, start)
                    self.grid[i + r].pop()
                    self.grid[i].append(piece)
                    if bar_piece:
                        self.grid[i + r].append(bar_piece)

                # If we can't move on the board can we take the piece off?
                if offboarding and self.remove_piece(player, i, r):
                    piece = self.grid[i].pop()
                    self.off_pieces[player].append(piece)
                    self.find_moves(rs, player, move + ((i, Game.OFF),), moves, start)
                    self.off_pieces[player].pop()
                    self.grid[i].append(piece)
        # igrac je 'x'
        else:
            # see if we can remove a piece from the bar
            if self.bar_pieces[player]:
                if self.can_onboard(player, r):
                    # skidamo piece sa bar-a
                    piece = self.bar_pieces[player].pop()
                    bar_piece = None
                    # izbacujemo protivnika
                    if len(self.grid[Game.NUMCOLS - r]) == 1 and self.grid[Game.NUMCOLS - r][-1] != player:
                        bar_piece = self.grid[Game.NUMCOLS - r].pop()

                    # stavljamo nas piece na mesto protivnika ili na slobodno mesto ako protivnik nije bio tu
                    self.grid[Game.NUMCOLS - r].append(piece)

                    self.find_moves(rs, player, move + ((Game.ON, Game.NUMCOLS - r),), moves, start)
                    self.grid[Game.NUMCOLS - r].pop()
                    self.bar_pieces[player].append(piece)
                    if bar_piece:
                        self.grid[Game.NUMCOLS - r].append(bar_piece)
                return

            # otherwise check each grid location for valid move using r
            offboarding = self.can_offboard(player)

            for i in range(len(self.grid)):
                if start is not None:
                    start = i
                if self.is_valid_move(i, i - r, player):

                    piece = self.grid[i].pop()
                    bar_piece = None
                    if len(self.grid[i - r]) == 1 and self.grid[i - r][-1] != player:
                        bar_piece = self.grid[i - r].pop()
                    self.grid[i - r].append(piece)
                    self.find_moves(rs, player, move + ((i, i - r),), moves, start)
                    self.grid[i - r].pop()
                    self.grid[i].append(piece)
                    if bar_piece:
                        self.grid[i - r].append(bar_piece)

                # If we can't move on the board can we take the piece off?
                if offboarding and self.remove_piece(player, i, r):
                    piece = self.grid[i].pop()
                    self.off_pieces[player].append(piece)
                    self.find_moves(rs, player, move + ((i, Game.OFF),), moves, start)
                    self.off_pieces[player].pop()
                    self.grid[i].append(piece)

    def opponent(self, token):
        """
        Retrieve opponent players token for a given players token.
        """
        for t in self.players:
            if t != token:
                return t

    def is_won(self, player):
        """
        If game is over and player won, return True, else return False
        """
        return self.is_over() and player == self.players[self.winner()]

    def is_lost(self, player):
        """
        If game is over and player lost, return True, else return False
        """
        return self.is_over() and player != self.players[self.winner()]

    def reverse(self):
        """
        Reverses a game allowing it to be seen by the opponent
        from the same perspective
        """
        self.grid.reverse()
        self.players.reverse()

    def reset(self):
        """
        Resets game to original layout.
        """
        for col in self.layout.split(','):
            loc, num, token = col.split('-')
            self.grid[int(loc)] = [token for _ in range(int(num))]
        for col in self.grid:
            for piece in col:
                self.num_pieces[piece] += 1

    def winner(self):
        """
        Get winner.
        """
        return 0 if len(self.off_pieces[self.players[0]]) == self.num_pieces[self.players[0]] else 1

    def is_over(self):
        """
        Checks if the game is over.
        """
        for t in self.players:
            if len(self.off_pieces[t]) == self.num_pieces[t]:
                return True
        return False

    def can_offboard(self, player):
        # count = 0
        # for i in range(Game.NUMCOLS - self.die, Game.NUMCOLS):
        #    if len(self.grid[i]) > 0 and self.grid[i][0] == player:
        #        count += len(self.grid[i])
        # if count + len(self.off_pieces[player]) == self.num_pieces[player]:
        #    return True
        # return False


        count = 0

        if player == "o":
            for i in range(Game.NUMCOLS - self.die, Game.NUMCOLS):
                if len(self.grid[i]) > 0 and self.grid[i][0] == player:
                    count += len(self.grid[i])
            if count + len(self.off_pieces[player]) == self.num_pieces[player]:
                return True
            return False
        else:
            for i in range(0, self.die):
                if len(self.grid[i]) > 0 and self.grid[i][0] == player:
                    count += len(self.grid[i])
            if count + len(self.off_pieces[player]) == self.num_pieces[player]:
                return True
            return False

    def can_onboard(self, player, r):
        """
        Can we take a players piece on the bar to a position
        on the grid given by roll-1?
        """
        if player == "o":
            if len(self.grid[r - 1]) <= 1 or self.grid[r - 1][0] == player:
                # if player=="o":
                # print("onboard - player je o")
                return True
            else:
                return False
        # player je x
        else:
            if len(self.grid[Game.NUMCOLS - r]) <= 1 or self.grid[Game.NUMCOLS - r][0] == player:
                return True
            else:
                return False

    def remove_piece(self, player, start, r):
        """
        Can we remove a piece from location start with roll r ?
        In this function we assume we are cool to offboard,
        i.e. no pieces on the bar and all are in the home quadrant.
        """
        # za 'o'
        if player == "o":
            isLast = False
            if start < Game.NUMCOLS - self.die:
                return False
            if len(self.grid[start]) == 0 or self.grid[start][0] != player:
                return False
            if start + r == Game.NUMCOLS:
                return True
            if start + r > Game.NUMCOLS:
                for i in range(start - 1, Game.NUMCOLS - self.die - 1, -1):
                    # if len(self.grid[i]) != 0 and self.grid[i][0] == self.players[0]:
                    if len(self.grid[i]) != 0:
                        if self.grid[i][0] == player:
                            # isLast = False
                            return False
                        else:
                            isLast = True
                            # else:
                            #    isLast = True
                    else:
                        isLast = True
                if isLast:
                    return True
            return False
        # za 'x'
        else:
            isLast = False
            if start >= self.die:
                return False
            if len(self.grid[start]) == 0 or self.grid[start][0] != player:
                return False
            if start - r == -1:
                return True
            if start - r < -1:
                for i in range(start + 1, self.die):
                    # if len(self.grid[i]) != 0 and self.grid[i][0] == self.players[0]:
                    if len(self.grid[i]) != 0:
                        if self.grid[i][0] == player:
                            # isLast = False
                            return False
                        else:
                            isLast = True
                if isLast:
                    return True
            return False

    def is_valid_move(self, start, end, token):

        if len(self.grid[start]) > 0 and self.grid[start][0] == token:
            if end < 0 or end >= len(self.grid):
                return False
            if len(self.grid[end]) <= 1:
                return True
            if len(self.grid[end]) > 1 and self.grid[end][-1] == token:
                return True
        return False

    def draw_col(self, i, col):
        print("-----------------------"),
        print("COL: %d", col)
        # print(col)
        if i == -2:
            if col < 10:
                print(""),
            print(str(col) + "|"),
        elif i == -1:
            print("--"),
        elif len(self.grid[col]) > i:
            print(" * " + self.grid[col][i]),
        else:
            print(" _ "),

    def draw(self):

        # os.system('clear')

        # largest = max([len(self.grid[i]) for i in range(len(self.grid)//2,len(self.grid))])

        # print("\nPrvi ispis")
        # print("LARGEST %d", largest)

        # for i in range(-2,largest):
        #    print(i)
        #   for col in range(len(self.grid)//2,len(self.grid)):
        #      #print("COL: %d", col)
        #     self.draw_col(i,col)
        #    print("|")
        # print()
        # print()


        # print("Drugi ispis")
        # largest = max([len(self.grid[i]) for i in range(len(self.grid)//2)])
        # print("LARGEST %d", largest)
        # onoliko puta koliko ima najvise zetona u polovini ispisujemo celu polovinu table
        # ovo je za kolone od 11 do 0
        # for i in range(largest-1,-3,-1):
        #   for col in range(len(self.grid)//2-1,-1,-1):
        #      self.draw_col(i,col)
        #  print("|")


        # print("Treci ispis")
        # for t in self.players:
        #   print("** <Player %s>  Off Board : "%(t)),
        #  for piece in self.off_pieces[t]:
        #     print(t+''),
        #   print("   Bar : "),
        #  for piece in self.bar_pieces[t]:
        #     print(t+''),
        # print()


        # print("REDEFINED DRAW:")
        # REDEFINED DRAW
        print("-------------------------------------")
        for i in range(len(self.grid)):
            print(str(i) + " || ", end=" ")

            if len(self.grid[i]) >= 1:
                for elem in self.grid[i]:
                    print(elem, end=" ")
                print(" ")
            else:
                print(" ")

            print("-------------------------------------")

        print()
        for t in self.players:
            print("<Player %s>  Off Board : " % (t)),
            for piece in self.off_pieces[t]:
                print(t + '', end=" "),
            print(" ")

        print("Bar : ", end="  ")
        for t in self.players:
            for piece in self.bar_pieces[t]:
                print(t + ' ', end=" "),
        print(" ")
        print("  ")
