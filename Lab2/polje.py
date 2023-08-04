
class Polje():

    COMP = 'X'
    USER = 'O'

    def __init__(self, w, h):
        
        self.polje =[['-' for x in range(w)] for y in range(h)] 
    


    def print_polje(self):

        print()
        for i in range(len(self.polje[0])):
            print(i+1, end =" ")

        print()
        print('~'*14)

        for i in range(len(self.polje)):
            for j in range(len(self.polje[i])):
                print(self.polje[::-1][i][j], end =" ")
            print()
        print()


    def odigraj(self, igrac, stupac):
        #biljezenje odabranog poteza - vec je prije provjereno da je on ispravan (ne ide izvan okvira polja)

        for i in range(len(self.polje)):
            if self.polje[i][stupac-1] == '-':
                self.polje[i][stupac-1] = igrac
                break
    
        return

    def ukloni_odigravanje(self, stupac):
        #ponisti zadnji potez u tom stupcu
        
        for i in range(len(self.polje)):
            if self.polje[::-1][i][stupac-1] != '-':
                self.polje[::-1][i][stupac-1] = "-"
                break

        return


    def provjeri_unos(self, stupac):
        #provjeri je li stupac slobodan
        if self.polje[-1][stupac-1] == '-':
            return True
        else: return False


    def provjeri_mjesta(self):
        #provjeri ima li jos mjesta na ploci
        for stupac in range(1, len(self.polje[0])+1):
            if self.provjeri_unos(stupac):
                return True
            if stupac == len(self.polje[0]):
                return False


    def provjeri_kraj(self,stupac):

        l = [] #dohvati cijeli stupac

        last_i = 0
        for i in range(len(self.polje)):
            if self.polje[i][stupac-1] != '-':
                last_i = i

            l.append(self.polje[i][stupac-1])

        if self.polje[last_i][stupac-1] == Polje.COMP:
            igrac = Polje.COMP
        else:
            igrac = Polje.USER

        #sad znamo da je element od kojeg trazimo na poziciju self.polje[last_i][stupac-1]
        #dohvatimo niz koji nas zanima i gledamo imamo li u njemu 4 za redom

        #gledamo imamo li 4 u nizu u tom stupcu
        if provjeri_4unizu(l, igrac):
            return True

        #gledamo imamo li 4 u nizu u tom redu
        l.clear()
        l = self.polje[last_i]
        if provjeri_4unizu(l, igrac):
            return True

        #gledamo imamo li 4 u nizu dijagonalno na gore
        x = last_i; y = stupac-1
        while True:
            if x-1>=0 and y-1>=0:
                x = x-1
                y = y-1
            else:
                break
        l = []
        while True:
            if x<len(self.polje) and y<len(self.polje[0]):
                l.append(self.polje[x][y])
                x = x+1
                y = y+1
            else:
                break

        if provjeri_4unizu(l, igrac):
            return True

        #gledamo imamo li 4 u nizu dijagonalno na dolje
        x = last_i; y = stupac-1
        while True:
            if x+1<len(self.polje) and y-1>=0:
                x = x+1
                y = y-1
            else:
                break
        l = []
        while True:
            if x>=0 and y<len(self.polje[0]):
                l.append(self.polje[x][y])
                x = x-1
                y = y+1
            else:
                break
            
        if provjeri_4unizu(l, igrac):
            return True

        return False

def provjeri_4unizu(niz, igrac):
    count = 0
    for el in niz:
        if el == igrac:
            count += 1
        elif not count>=4:
            count = 0
    if count >= 4:
        return True
    else: return False