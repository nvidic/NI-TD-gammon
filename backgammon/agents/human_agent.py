from ..game import Game

class HumanAgent(object):
    def __init__(self, player):
        self.player = player
        self.name = 'Human'

    def get_action(self, roll, moves, game=None):
        if not moves:
            input("-> No moves for you...(hit enter)")
            return None

        while True:
            while True:
                mv1 = input('\n -> Please enter a move "<location start>,<location end>" ("%s" for on the board, "%s" for off the board): ' % (Game.ON, Game.OFF))
                mv1 = self.get_formatted_move(mv1)
                if not mv1:
                    print('\n!!! Bad format enter e.g. "3,4"')
                else:
                    print("mv1: ("+str(mv1[0])+", "+str(mv1[1])+")")
                    break

            while True:
                mv2 = input('\n -> Please enter a second move (enter to skip): ')
                if mv2 == '':
                    mv2 = None
                    break
                mv2 = self.get_formatted_move(mv2)
                if not mv2:
                    print('\n!!! Bad format enter e.g. "3,4"')
                else:
                    print("mv2: ("+str(mv2[0])+", "+str(mv2[1])+")")
                    break

            r1, r2 = roll
            if r1==r2:
                while True:
                    mv3 = input(
                        '\n -> Please enter a third move (enter to skip): ')
                    mv3 = self.get_formatted_move(mv3)
                    if not mv3:
                        print('\n!!! Bad format enter e.g. "3,4"')
                    else:
                        print("mv3: (" + str(mv3[0]) + ", " + str(mv3[1]) + ")")
                        break

                while True:
                    mv4 = input('\n -> Please enter a fourth move (enter to skip): ')
                    if mv4 == '':
                        mv4 = None
                        break
                    mv4 = self.get_formatted_move(mv4)
                    if not mv4:
                        print('\n!!! Bad format enter e.g. "3,4"')
                    else:
                        print("mv4: (" + str(mv4[0]) + ", " + str(mv4[1]) + ")")
                        break

            if r1==r2:
                if mv1:
                    if mv2:
                        if mv3:
                            if mv4:
                                move = (mv1, mv2, mv3, mv4)
                            else:
                                move = (mv1, mv2, mv3, )
                        else:
                            move = (mv1, mv2, )
                    else:
                        move = (mv1, )
            else:
                if mv2:
                    move = (mv1, mv2)
                else:
                    move = (mv1,)

            #if mv2:
            #    move = (mv1, mv2)
            #else:
            #    move = (mv1,)



            if move in moves:
                return move
            elif move[::-1] in moves:
                move = move[::-1]
                return move
            else:
                #print move
                print("****Move: " + str(move))

                for move in moves:
                    #print("  --> move: [ (" + str(move[0]) + ", " + str(move[1]) + ") ]")
                    print("  --> move: " + str(move))

                print("\n!!! You can't play that move")

        return None

    def get_formatted_move(self, move):
        try:
            start, end = move.split(",")
            if start == Game.ON:
                return (start, int(end))
            if end == Game.OFF:
                return (int(start), end)
            return (int(start), int(end))
        except:
            return False
