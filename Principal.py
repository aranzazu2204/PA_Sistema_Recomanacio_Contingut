# -*- coding: utf-8 -*-
"""
Fitxer de python que conté la funció principal del projecte: main() i la classe Principal (collector)

@author: Lucía Revaliente i Aránzazu Miguélez
"""
# IMPORTS
import pickle
from Usuari import Usuari
from Dataset import Movies, Books
from Recomanacio import Recomanacio_colaborativa, Recomanacio_simple, \
    Recomanacio_contingut_movies, Recomanacio_contingut_books

# CONTROLLER: Classe Principal
class Principal:
    ITEMS = ['Pel·lícules', 'Llibres']
    SISTEMES = ['Simple', 'Col·laboratiu', 'Contingut']
    NOM_DIRECTORI = 'Datasets/'
    LLINDAR_MOVIES = 4
    LLINDAR_BOOKS = 7

    def __init__(self):
        self._dataset = ""
        self._sistema = ""
        self._usuari = ""
        self._tipus_dataset = ""
        self._llindar = -1

    @property
    def usuari(self):
        return self._usuari

    def inicialitza(self):
        """
        Funció que inicialitza tot el sistema: dataset, sistema de recomanació, usuari a recomanar...
        :return: None
        """
        # INCIALITZEM DATASET
        # Preguntem a l'usuari quin dataset vol executar
        print('Quina base de dades vols executar?  \n\t1. Pel·lícules\n\t2. Llibres\n')
        res = 'si'  # Inicialitzem la variable per fer un bucle en cas de que els valors introduïts siguin erronis
        while res == 'si':
            try:
                n_dataset = int(input('Opció: '))
                if n_dataset == 1 or n_dataset == 2:  # Si no ha introduït un valor incorrecte,
                    items = self.ITEMS[n_dataset - 1]  # Establim el dataset
                    self._tipus_dataset = items
                    print('\n--------------------------------------------------------------\n')
                    res = 'no'
                else:
                    raise ValueError
            except ValueError:  # Si ha introduït un valor incorrecte, imprimim missatge i torna a preguntar
                print('ERROR: El valor introduït no és un nombre vàlid. Torna-ho a provar!\n')

        print('Com vols inicialitzar el dataset?  \n\t1. Llegint els fitxers\n\t2. Important l\'arxiu pickle\n')
        res = 'si'  # Inicialitzem la variable per fer un bucle en cas de que els valors introduïts siguin erronis
        while res == 'si':
            try:
                inicialitzacio = int(input('Opció: '))
                if inicialitzacio == 1 or inicialitzacio == 2:  # Si no ha introduït un valor incorrecte,
                    res = 'no'  # sortim del bucle
                else:
                    raise ValueError
            except ValueError:  # Si ha introduït un valor incorrecte, imprimim missatge i tornem a preguntar
                print('ERROR: El valor introduït no és un nombre vàlid. Torna-ho a provar!\n')

        # Inicialitzem els datasets
        if inicialitzacio == 1:  # Si l'usuari ha escollit inicialitzar el dataset manualment i
            if n_dataset == 1:  # ha escollit la opció 1 (pel·lícules),
                self._dataset = Movies()  # El dataset serà de pel·lícules
                self._dataset.llegeix(self.NOM_DIRECTORI)  # Incialitzem el dataset
                self._llindar = self.LLINDAR_MOVIES
            else:  # Sinó,
                self._dataset = Books()  # El dataset serà de llibres
                self._dataset.llegeix(self.NOM_DIRECTORI)  # Incialitzem el dataset
                self._llindar = self.LLINDAR_BOOKS
        else:  # Sinó
            # Recuperem dels fitxers de pickle l'objecte desitjat:
            if n_dataset == 1:  # ha escollit la opció 1 (pel·lícules),
                with open("Movies.dat", 'rb') as fitxer:  # llegim el fitxer binari i
                    self._dataset = pickle.load(fitxer)  # importem l'objecte Movie
            else:  # Sinó,
                with open("Books.dat", 'rb') as fitxer:  # llegim el fitxer binari i
                    self._dataset = pickle.load(fitxer)  # importem l'objecte Book

        # INCIALITZEM USUARI
        # Pregunta a quin usuari li volem recomanar items
        print('\n--------------------------------------------------------------\n')
        res = 'si'  # Inicialitzem la variable per fer un bucle en cas de que els valors introduïts siguin erronis
        while res == 'si':
            try:
                print('Introdueix a quin usuari vols recomanar-li items. Si vols finalitzar l\'execució introdueix un '
                      'espai en blanc.')
                usuari = input('Usuari (1 - ' + str(len(self._dataset.usuaris)) + '): ')  # Preguntem a quin usuari
                # volem recomanar
                print('\n--------------------------------------------------------------\n')

                if 1 <= int(usuari) <= len(self._dataset.usuaris):  # si l'usuari està dins el rang d'usuaris
                    res = 'no'  # Parem
                    self._usuari = Usuari(int(usuari))
                elif 1 > int(usuari) > self._dataset.usuaris:  # si l'usuari no està dins el rang d'usuaris,
                    raise TypeError

            except TypeError:
                print("\nERROR: El nombre introduït no és dins l'interval. Torna-ho a provar.\n")
            except ValueError:
                if usuari in ' \n':
                    res = 'no'
                    self._usuari = ' \n'
                    print(
                        'Has introduït un espai en blanc en la incialització. Per tant, no recomanarem res i el '
                        'programa acabarà.')
                else:
                    print("\nERROR: El nombre introduït ha de ser enter. Torna-ho a provar.\n")

        # INCIALITZEM SISTEMA RECOMANACIO
        if self._usuari != ' \n':
            # Preguntem a l'usuari quin sistema de recomanacio vol executar
            print('Mètodes de recomanació disponibles:\n\t1. Simple\n\t2. Col·laboratiu\n\t3. Basat en Contingut')
            res = 'si'  # Inicialitzem la variable per fer un bucle en cas de que els valors introduïts siguin erronis
            while res == 'si':
                try:
                    metode = int(input('Opció: '))  # Demanem el metode
                    if 3 >= metode >= 1:
                        sistema = self.SISTEMES[metode - 1]
                        res = 'no'
                    else:
                        raise ValueError
                except ValueError:  # Si ha introduït un valor incorrecte, imprimim missatge i torna a preguntar
                    print('ERROR: El valor introduït no és un nombre vàlid. Torna-ho a provar.\n')

            if self._usuari != ' \n':  # mentre l'usuari no sigui un espai en blanc o un salt de línia,
                if sistema == self.SISTEMES[0]:  # Si hem escollit el mètode 1 (simple)
                    # Demanem minim vots per fer la recomanacio:
                    res = 'si'  # Inicialitzem variable per fer un bucle en cas de valors introduïts siguin erronis
                    while res == 'si':
                        try:
                            minim_vots = int(input('\nIntrodueix els vots mínims: '))  # demanem el nombre de vots
                            # mínims per recomenar
                        except ValueError:
                            print(
                                '\nERROR: El valor introduït no és un nombre enter. Torna-ho a provar.\n')  # controlem
                            # que sigui un nombre enter,sinó tronem a preguntar
                        else:  # Si tot està bé,
                            res = 'no'  # parem
                    # Iniciem mètode recomanació simple:
                    self._sistema = Recomanacio_simple(self._dataset, self._usuari, minim_vots)

                elif sistema == self.SISTEMES[1]:  # si escollim el sistems 2 (col·laboratiu)
                    # Demanem paràmetre k:
                    res = 'si'  # Inicialitzem variable per fer un bucle en cas de valors introduïts siguin erronis
                    while res == 'si':
                        try:
                            k = int(input("Introdueix els nombre d'usuaris més similars a tu (k): "))  # demanem quina
                            # quantitat d'usuaris similars a ell vol
                        except ValueError:
                            print(
                                "\nERROR: El valor introduït no és un nombre enter. Torna-ho a provar.\n")  # controlem
                            # que sigui un nombre enter,sinó tronem a preguntar
                        else:  # Si tot està bé,
                            res = 'no'  # parem
                    # Inicialitzem sistema recomanació col·laboratiu:
                    self._sistema = Recomanacio_colaborativa(self._dataset, self._usuari, k)

                elif sistema == self.SISTEMES[2]:  # si escollim el sistema 3 (contingut)
                    if self._tipus_dataset == self.ITEMS[0]:
                        self._sistema = Recomanacio_contingut_movies(self._dataset, self._usuari,
                                                                     5)  # executem el sistema de recomanació
                    else:
                        self._sistema = Recomanacio_contingut_books(self._dataset, self._usuari,
                                                                    10)  # executem el sistema de recomanació

    def recomana(self):
        """
        Funció que recomana a l'usuari els items que més li agradaran i els mostra per pantalla.
        :return: None
        """
        dic, recomanacions = self._sistema.calcul_score()  # obtenim les recomanacions
        self._sistema.preguntar_usuari(recomanacions)  # Mostrem per pantalla les recomanacions

    def avalua(self):
        """
        Funció que avalua el sistema de recomanació sel·lecionat.
        :return: None
        """
        n = int(input("Quins N millors ítems vols considerar? "))
        self._sistema.avalua(self._llindar, n)  #Avaluem

    def executa(self):
        """
        Funció que pregunta a l'usuari quina acció vol fer (recomanar o avaluar) i recondueix el programa per
        realitzar-la.
        :return: None
        """
        print('\n--------------------------------------------------------------\n')
        print('Quina acció vols realitzar?:  \n\t1. Recomanar', self._tipus_dataset.lower(),
              '\n\t2. Avaluar les recomanacions fetes\n')
        res = 'si'  # Inicialitzem la variable per fer un bucle en cas de que els valors introduïts siguin erronis
        while res == 'si':
            try:
                accio = int(input('Opció: '))
                if accio == 1 or accio == 2:  # Si no ha introduït un valor incorrecte,
                    res = 'no'  # sortim del bucle
            except ValueError:  # Si ha introduït un valor incorrecte, imprimim missatge i tornem a preguntar
                print('ERROR: El valor introduït no és un nombre vàlid. Torna-ho a provar!\n')

        if accio == 1:  # si ha escollit l'opció 1,
            self.recomana()  # recomanem
        else:  #Sinó,
            self.avalua()  #avaluem


# FUNCIÓ PRINCIPAL
def main():
    """
    Funció que representa el programa principal.
    :return: int. Si retorna un 1 és que tot ha sortit bé.
    """
    # Donem benvinguda
    print('\n--------------------------------------------------------------\n')
    print('Benvingut/da al nostre sistema de recomanació!')
    print('\n--------------------------------------------------------------\n')
    # Inicialitzem i executem els sitemes de recomanació
    principal = Principal()
    principal.inicialitza()
    while principal.usuari != ' \n':
        principal.executa()
        print('\nHa finalitzat el sistema de recomanació!')
        print('\n--------------------------------------------------------------\n')
        print("Tornem a començar...\n")
        principal.inicialitza()
    print('Tancant programa...')
    return 1


# COMPROVACIONS
res = main()
print(res)