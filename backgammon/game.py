import os
import copy
import time
import random
import numpy as np


class Game:
    # prema pravilima backgammon-a definisemo osnovne elemente igre

    # svaka partija uvek pocinje istom postavkom:
    # 'pozicija na tabli' - 'broj zetona' - 'igrac kome pripadaju zetoni'
    LAYOUT = "0-2-o,5-5-x,7-3-x,11-5-o,12-5-x,16-3-o,18-5-o,23-2-x"
    # postoji ukupno 24 polja table koja ce biti indeksirana 0-23
    NUMCOLS = 24
    # tabla ima 4 kvadranta sa po 6 polja
    QUAD = 6
    # konstanta koja se koristi kod poteza kada se zeton "skida" sa table
    OFF = 'off'
    # konstanta koja se koristi kod poteza kada se zeton ponovo ubacuje u igru
    ON = 'on'
    # igra definise 2 igraca ('crni' i 'crveni', 'crni' i 'beli', 'x' i 'o', ...]
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

    # bacanje kockice
    # igrac u svom potezu baca dve kockice
    def roll_dice(self):
        return (random.randint(1, self.die), random.randint(1, self.die))


    def play(self, players, draw=False):

        # igra pocinje tako sto svaki igrac baci po jednu kockicu
        x_roll = random.randint(1, self.die)
        o_roll = random.randint(1, self.die)

        # u slucaju da oba igraca dobiju isti broj, bacanje se ponavlja
        while x_roll == o_roll:
            print("Player x rolled: " + str(x_roll))
            print("Player o rolled: " + str(o_roll) + "\n")
            x_roll = random.randint(1, self.die)
            o_roll = random.randint(1, self.die)

        print("---> Player x rolled: " + str(x_roll))
        print("---> Player o rolled: " + str(o_roll))

        # igrac koji je dobio veci broj igra prvi
        # koristeci kockice koje su bacene (jednu je bacio 'x' a drugu 'o')
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


    # funkcija baca kockice za igraca ciji je red i igra potez u skladu sa kockicama
    def next_step(self, player, player_num, draw=False):
        roll = self.roll_dice()

        if draw:
            self.draw()

        self.take_turn(player, roll, draw=draw)


    def take_turn(self, player, roll, draw=False):

        if draw:
            print("---> Player {%s} rolled [%d] [%d]" % (player.player, roll[0], roll[1]))
            time.sleep(1)

        # svi moguci potezi za datog igraca uz dato bacanje kockica
        moves = self.get_actions(roll, player.player, nodups=True)
        # najbolji moguci potez
        move = player.get_action(roll, moves, self) if moves else None

        # ako postoji potez koji moze da se odigra, on ce biti odigran
        if move:
            self.take_action(move, player.player)

    def clone(self):
        """
        Return an exact copy of the game. Changes can be made
        to the cloned version without affecting the original.
        """
        return Game(None, self.grid, self.off_pieces,
                    self.bar_pieces, self.num_pieces, self.players)

    # odigraj potez action za igraca token
    def take_action(self, action, token):
        """
        Makes given move for player, assumes move is valid,
        will remove pieces from play
        """
        # print("ATELIST: " + str(ateList) + "\n") --> # ATELIST: [0, 0, 0, 0]
        ateList = [0] * 4
        for i, (s, e) in enumerate(action):
            # ako je potez (Game.ON, i) znaci da ponovo ubacujemo zeton u igru
            # samim tim skidamo zeton sa "sipke" tj. bar-a
            if s == Game.ON:
                piece = self.bar_pieces[token].pop()
            # ako je zeton vec u igri, skidamo ga sa trenutne pozicije i prebacujemo na novu
            else:
                piece = self.grid[s].pop()
            # ako zeton skidamo sa table, dodajemo ga u listu off_pieces
            if e == Game.OFF:
                self.off_pieces[token].append(piece)
                continue
            # ukoliko zeton pomeramo na polje odrediste\cilj gde se nalazi jedan protivnicki zeton,
            # protivnicki zeton izbacujemo iz igre i smestamo na bar
            if len(self.grid[e]) > 0 and self.grid[e][0] != token:
                bar_piece = self.grid[e].pop()
                self.bar_pieces[bar_piece].append(bar_piece)
                ateList[i] = 1
            # zeton koji pomeramo smestamo na odrediste
            self.grid[e].append(piece)
        return ateList

    # pomocna funkcija koja se koristi prilikom odredjivanja najboljeg poteza
    # ponistavanje odigranog poteza i vracanje u prethodno stanje
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

    # funkcija koja pronalazi sve moguce poteze za dati roll i igraca player
    def get_actions(self, roll, player, nodups=False):

        moves = set()
        if nodups:
            start = 0
        else:
            start = None

        r1, r2 = roll
        # u slucaju da je igrac dobio iste vrednosti na obe kockice, ima pravo na 4 poteza
        if r1 == r2:  # doubles
            i = 4

            # naci sve poteze za roll npr. 4, 4, 4, 4
            while not moves and i > 0:
                self.find_moves(tuple([r1] * i), player, (), moves, start)
                i -= 1
        else:
            # naci za roll (r1, r2)
            self.find_moves(roll, player, (), moves, start)
            self.find_moves((r2, r1), player, (), moves, start)
            # ako ne postoje potezi, pokusaj da pomeris samo 1 zeton
            if not moves:
                for r in roll:
                    self.find_moves((r,), player, (), moves, start)

        return moves

    # funkcija koja pronalazi jedan po jedan validan potez za dati roll rs, i igraca player
    def find_moves(self, rs, player, move, moves, start=None):
        if len(rs) == 0:
            moves.add(move)
            return
        r, rs = rs[0], rs[1:]

        # kako se 2 igraca po tabli krecu u suprotnim smerovima ( 'o': 0-23 , 'x': 23-0)
        # potrebno je razdvojiti kreiranje poteza
        if player == "o":
            # da li mozemo da uklonimo zeton sa bar-a
            if self.bar_pieces[player]:
                # ako mozemo da ubacimo zeton u igru
                if self.can_onboard(player, r):
                    # skidamo piece sa bar-a
                    piece = self.bar_pieces[player].pop()
                    bar_piece = None
                    # izbacujemo protivnika ako su ispunjeni uslovi
                    if len(self.grid[r - 1]) == 1 and self.grid[r - 1][-1] != player:
                        bar_piece = self.grid[r - 1].pop()

                    # stavljamo nas piece na mesto protivnika ili na slobodno mesto ako protivnik nije bio tu
                    self.grid[r - 1].append(piece)

                    self.find_moves(rs, player, move + ((Game.ON, r - 1),), moves, start)

                    # uklanjamo nas zeton\piece posto ovo nije konacan potez
                    self.grid[r - 1].pop()
                    # dodajemo nas zeton u bar_piece[player]
                    self.bar_pieces[player].append(piece)
                    # ako smo protivnika izbacili sa table, vracamo ga na njegovo mesto
                    if bar_piece:
                        self.grid[r - 1].append(bar_piece)
                return

            # ako su svi zetoni u igri, proveri sve moguce validne poteze datim roll-om r

            offboarding = self.can_offboard(player)

            # za svako polje proveravamo da li postoji validan potez
            for i in range(len(self.grid)):
                if start is not None:
                    start = i
                if self.is_valid_move(i, i + r, player):
                    # skidamo zeton sa trenutne pozicije
                    piece = self.grid[i].pop()
                    bar_piece = None
                    # da li mozemo da izbacimo protivnika
                    if len(self.grid[i + r]) == 1 and self.grid[i + r][-1] != player:
                        bar_piece = self.grid[i + r].pop()
                    # stavljamo zeton na novu poziciju
                    self.grid[i + r].append(piece)
                    self.find_moves(rs, player, move + ((i, i + r),), moves, start)
                    # ponistavamo nas potez
                    self.grid[i + r].pop()
                    self.grid[i].append(piece)
                    if bar_piece:
                        self.grid[i + r].append(bar_piece)

                # da li mozemo da skinemo zeton sa table
                if offboarding and self.remove_piece(player, i, r):
                    # skidamo zeton sa table
                    piece = self.grid[i].pop()
                    # dodajemo ga u listu off_pieces igraca player
                    self.off_pieces[player].append(piece)
                    # trazimo naredni potez
                    self.find_moves(rs, player, move + ((i, Game.OFF),), moves, start)
                    # ponistavamo akcije
                    self.off_pieces[player].pop()
                    self.grid[i].append(piece)
        # igrac je 'x'
        else:
            # da li mozemo da uklonimo zeton sa bar-a
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

                # da li mozemo da uklonimo zeton sa bar-a
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

    # da li igrac moze da uklanja zetone iz igre
    # postoji razlika za igraca 'x' i 'o' zbog smera kretanja po tabli
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

    # da li igrac moze da ubaci zeton u igru
    # postoji razlika za igraca 'x' i 'o' zbog smera kretanja po tabli
    def can_onboard(self, player, r):

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

    # da li sa date pozicije start i bacanjem kockice r mozemo da uklonimo zeton sa table
    # pretpostavka je da su ispunjeni potrebni uslovi za uklanjanje zetona
    # provera uslova se vrsi na drugom mestu u kodu
    # postoji razlika za igraca 'x' i 'o'

    # prema pravilima igre, igrac moze da ukloni zeton(piece) ako su svi zetoni u poslednjem kvadrantu i nijedan zeton
    # se ne nalazi van igre (na bar-u)
    # takodje, dodatno pravilo je da je moguce skloniti zeton sa table sa roll-om vecim od potrebnog ako se
    # na pozicijama dalje od kraja kvadranta ne nalaze zetoni tog igraca
    # npr. igrac 'o' ima zetone na pozicijama 21, 22, 23 a nema ih na pozicijama 18, 19 i 20
    # tada igrac 'o' moze ukloniti zeton na poziciji 21 ako bacanjem kockice dobije bilo koji od brojeva 3, 4, 5 ili 6
    def remove_piece(self, player, start, r):

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

    # da li je zeljeni potez validan
    def is_valid_move(self, start, end, token):
        # ako na start lokaciji igrac token ima zetone
        if len(self.grid[start]) > 0 and self.grid[start][0] == token:
            # prekoracenje ili potkoracenje indeksa
            if end < 0 or end >= len(self.grid):
                return False
            # na poziciji end ima <= 1 zeton (bilo od igraca token bilo od protivnika)
            if len(self.grid[end]) <= 1:
                return True
            # igrac token ima vise od jednog zetona na poziciji end
            if len(self.grid[end]) > 1 and self.grid[end][-1] == token:
                return True
        # protivnik ima vise od jednog zetona na poziciji end
        return False

    # izgled jedne kolone u terminalu
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

    # funkcija prikaza trenutnog stanja igre
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
