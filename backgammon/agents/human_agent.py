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

        # preostali moguci potezi
        availableMoves = set()
        numberOfMoves = 2
        moveNumber = 1
        # ukoliko su vrednosti dobijene na dvema kockicama jednake, igrac ima pravo na 2 dodatna poteza
        # koje treba da unese
        if roll[0] == roll[1]:
            print("You're lucky! You have four moves! :) \n")
            numberOfMoves = 4
        completeMove = set()

        # covek sam unosi potez koji zeli da odigra
        while True:
            # posle svakog poteza moguce je da je igrac pobedio pa to treba proveriti
            if game.is_over():
                print("The game is over! YOU WON! Congrats!\n")
                return None
            if not moves:
                input("-> No moves for you...(hit enter)")
                return None
            availableMoves.clear()
            mv1 = input('\n -> Please enter your ' + str(moveNumber) + '. move "<location start>,<location end>" [e.g. "3,4"] ("%s" for on the board, "%s" for off the board): ' % (Game.ON, Game.OFF))
            mv1 = self.get_formatted_move(mv1)
            if not mv1:
                print('\n!!! Bad format enter e.g. "3,4"')
            else:
                print("mv1: ("+str(mv1[0])+", "+str(mv1[1])+")")

                # svi moguci potezi
                for move_set in moves:
                    print("move: "+str(move_set))
                    if move_set[0] == mv1:
                        print("m == mv1")
                        # uklanjamo prvu akciju i ostavljamo drugu ili drugu, trecu i cetvrtu
                        # print("type(m): "+str(type(m))) ---> tuple
                        # print("len(move_set): " + str(len(move_set)))
                        # print(move_set[1:])
                        # print("len(move_set[1:]): "+str(len(move_set[1:])))
                        availableMoves.add(move_set[1:])
                        print("dodajem availableMoves.add(move_set[1:])"+str(move_set[1:]))

                # ako nismo uneli validan potez ponovi unos
                if len(availableMoves) == 0:
                    print("You can't play that move!")
                else:
                    print("availableMoves: ")
                    for m in availableMoves:
                        print("m: "+str(m))

                    mvs = set()
                    mvs.add(mv1)
                    completeMove.add(mv1)
                    game.take_action(mvs, "o")
                    game.draw()
                    moves.clear()
                    moves = availableMoves.copy()
                    moveNumber += 1
                    if moveNumber > numberOfMoves:
                        if game.is_over():
                            print("The game is over! YOU WON! Congrats!\n")
                            return None
                        break
        # funkcija na kraju ne treba nista da vraca zato sto su svi potezi odigrani
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
'''
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
                    matchFound = False
                    for move_set in availableMoves:
                        for m in move_set:
                            if m == mv2:
                                print("m == mv2")
                                matchFound = True
                                # uklanjamo prvu akciju i ostavljamo drugu ili drugu, trecu i cetvrtu
                                # print("type(m): "+str(type(m))) ---> tuple
                                # print("len(move_set): " + str(len(move_set)))
                                # print(move_set[1:])
                                # print("len(move_set[1:]): "+str(len(move_set[1:])))
                                avMovesHelp.add(move_set[1:])
                                print("dodajem avMovesHelp.add(move_set[1:])" + str(move_set[1:]))
                                break
                            else:
                                break

                    print("matchFound: "+str(matchFound))

                    # ako nismo uneli validan potez ponovi unos
                    if matchFound == False:
                        print("You can't play that move!")
                    else:
                        availableMoves = avMovesHelp
                        print("availableMoves: ")
                        for m in availableMoves:
                            print("m: " + str(m))

                        mvs = set()
                        mvs.add(mv2)
                        game.take_action(mvs, "o")
                        game.draw()
                        break


            r1, r2 = roll

            # ukoliko su vrednosti dobijene na dvema kockicama jednake, igrac ima pravo na 2 dodatna poteza
            # koje treba da unese
            # u available moves imamo jos 2 poteza
            if r1==r2:
                while True:
                    avMovesHelp.clear()
                    mv3 = input('\n -> Please enter a third move (enter to skip): ')
                    if mv3 == '':
                        mv3 = None
                        break
                    mv3 = self.get_formatted_move(mv3)
                    if not mv3:
                        print('\n!!! Bad format enter e.g. "3,4"')
                    else:
                        print("mv3: (" + str(mv3[0]) + ", " + str(mv3[1]) + ")")

                        matchFound = False
                        for move_set in availableMoves:
                            for m in move_set:
                                if m == mv3:
                                    print("m == mv3")
                                    matchFound = True
                                    # uklanjamo prvu akciju i ostavljamo drugu ili drugu, trecu i cetvrtu
                                    # print("type(m): "+str(type(m))) ---> tuple
                                    # print("len(move_set): " + str(len(move_set)))
                                    # print(move_set[1:])
                                    # print("len(move_set[1:]): "+str(len(move_set[1:])))
                                    avMovesHelp.add(move_set[1:])
                                    print("dodajem avMovesHelp.add(move_set[1:])" + str(move_set[1:]))
                                    break
                                else:
                                    break

                        print("matchFound: " + str(matchFound))

                        # ako nismo uneli validan potez ponovi unos
                        if matchFound == False:
                            print("You can't play that move!")
                        else:
                            availableMoves = avMovesHelp
                            print("availableMoves: ")
                            for m in availableMoves:
                                print("m: " + str(m))

                            mvs = set()
                            mvs.add(mv3)
                            game.take_action(mvs, "o")
                            game.draw()
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

                    matchFound = False
                    for move_set in availableMoves:
                        for m in move_set:
                            if m == mv4:
                                print("m == mv2")
                                matchFound = True
                                # uklanjamo prvu akciju i ostavljamo drugu ili drugu, trecu i cetvrtu
                                # print("type(m): "+str(type(m))) ---> tuple
                                # print("len(move_set): " + str(len(move_set)))
                                # print(move_set[1:])
                                # print("len(move_set[1:]): "+str(len(move_set[1:])))
                                avMovesHelp.add(move_set[1:])
                                print("dodajem avMovesHelp.add(move_set[1:])" + str(move_set[1:]))
                                break
                            else:
                                break

                    print("matchFound: " + str(matchFound))

                    # ako nismo uneli validan potez ponovi unos
                    if matchFound == False:
                        print("You can't play that move!")
                    else:
                        availableMoves = avMovesHelp
                        print("availableMoves: ")
                        for m in availableMoves:
                            print("m: " + str(m))

                        mvs = set()
                        mvs.add(mv4)
                        game.take_action(mvs, "o")
                        game.draw()
                        break
'''
'''       # pravimo potez na osnovu kockica i unetih parametara

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
'''

