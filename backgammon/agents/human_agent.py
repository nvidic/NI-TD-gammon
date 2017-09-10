from ..game import Game

# igrac je covek
class HumanAgent(object):
    def __init__(self, player):
        self.player = player
        self.name = 'Human'

    def get_action(self, roll, moves, game=None):
        if not moves:
            input("-> No moves for you...(hit enter)")
            return None

        # covek sam unosi potez koji zeli da odigra
        while True:
            while True:
                mv1 = input('\n -> Please enter a move "<location start>,<location end>" [e.g. "3,4"] ("%s" for on the board, "%s" for off the board): ' % (Game.ON, Game.OFF))
                if mv1 == '':
                    mv1 = None
                    break
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

            # ukoliko su vrednosti dobijene na dvema kockicama jednake, igrac ima pravo na 2 dodatna poteza
            # koje treba da unese
            if r1==r2:
                while True:
                    mv3 = input('\n -> Please enter a third move (enter to skip): ')
                    if mv3 == '':
                        mv3 = None
                        break
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

            # pravimo potez na osnovu kockica i unetih parametara

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
                if mv1:
                    if mv2:
                        move = (mv1, mv2)
                    else:
                        move = (mv1,)
                else:
                    move = ()

            #if mv2:
            #    move = (mv1, mv2)
            #else:
            #    move = (mv1,)


            # ukoliko imamo validan potez, on ce biti vracen kao rezultat funkcije, a nakon toga odigran
            if move in moves:
                return move
            elif move[::-1] in moves:
                move = move[::-1]
                return move
            # neispavan potez
            else:
                #print move
                print("****Move: " + str(move))

                # stampanje svih mogucih validnih poteza
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
