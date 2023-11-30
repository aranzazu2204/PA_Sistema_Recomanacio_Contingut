# -*- coding: utf-8 -*-
"""
Fitxer de python que conté la classe Datset, Movies, Books del projecte.

@author: Lucía Revaliente i Aránzazu Miguélez
"""
# IMPORTS
from abc import ABCMeta, abstractmethod
import numpy as np
import csv
import os
from Usuari import Usuari
from Items import Movie, Llibre


# CLASSE DATASET ABSTRACTA
class Dataset(metaclass=ABCMeta):
    def __init__(self, dic_usuaris={}, dic_items={}, ratings=np.empty(0)):
        self._usuaris = dic_usuaris
        self._items = dic_items
        self._ratings = ratings

    @property
    def usuaris(self):
        return self._usuaris

    @property
    def items(self):
        return self._items

    @property
    def ratings(self):
        return self._ratings

    @abstractmethod
    def llegeix(self, nom_directori: str):
        raise NotImplementedError()


# CLASSE DATASET MOVIES
class Movies(Dataset):
    def llegeix(self, nom_directori: str):
        # Llegim el document de movies
        # Inicialitzem la llista d'ítems: Movies
        ruta_fitxer = os.path.join(nom_directori + 'Movies/movies.csv')  # Creem la ruta on es troba el fitxer

        with open(ruta_fitxer, 'r', encoding='utf8') as csv_file:  # Obrim el fitxer en mode lectura
            csvreader = csv.reader(csv_file, delimiter=',')  # Creem un objecte per llegir un fitxer csv
            fields = next(csvreader)
            for index, linia in enumerate(csvreader):  # Per cada línia,
                # print(int(linia[0]), linia[1], linia[2])
                movie = Movie(index, linia[1], int(linia[0]), linia[2])  # Creem una pel·lícula
                self._items[movie.idd] = movie  # Afegim la peli al diccionari
                # self._items.append(movie)  #Afegim la película a la llista d'ítems del Dataset

        # Llegim el document de ratings
        ruta_fitxer = os.path.join(nom_directori + 'Movies/ratings.csv')  # Creem la ruta on es troba el fitxer

        # Inicialitzem la llista d'usuaris: Usuaris
        with open(ruta_fitxer, 'r', encoding='utf8') as csv_file:  # Obrim el fitxer en mode lectura
            csvreader = csv.reader(csv_file, delimiter=',')  # Creem un objecte per llegir un fitxer csv
            fields = next(csvreader)
            for linia in csvreader:  # Per cada línia,
                usuari = Usuari(int(linia[0]))  # Creem un usuari
                self._usuaris[usuari.idd] = usuari  # Afegim l'usuari al diccionari

        # Inicialitzem l'array de ratings
        self._ratings = np.zeros((len(self._usuaris), len(self._items)), dtype='int8')  # Creem array buit
        ruta_fitxer = os.path.join(nom_directori + 'Movies/ratings.csv')  # Creem la ruta on es troba el fitxer
        with open(ruta_fitxer, 'r', encoding='utf8') as csv_file:  # Obrim el fitxer en mode lectura
            csvreader = csv.reader(csv_file, delimiter=',')  # Creem un objecte per llegir un fitxer csv
            fields = next(csvreader)
            for linia in csvreader:  # Per cada línia,
                self._ratings[self._usuaris[int(linia[0])].idd - 1, self._items[int(linia[1])].ordre] = int(
                    float(linia[2]))


# CLASSE DATASET BOOKS        
class Books(Dataset):
    MAX_LLIBRES = 10000
    MAX_USUARIS = 100000

    def llegeix(self, nom_directori: str):
        """
        Funció que inicialitza tots els datasets de Books. A més, obté el vocabulari i el retorna
        :param nom_directori:
        :return vocabulari: list[str]. Llista de strings formada per les paraules importants del títol i els autors
        """
        # Llegim el document de movies
        vocabulari = []  # Inicialitzem la llista de vocabulari

        # Inicialitzem la llista d'ítems: Books
        ruta_fitxer = os.path.join(nom_directori + 'Books/Books.csv')  # Creem la ruta on es troba el fitxer
        with open(ruta_fitxer, 'r', encoding='utf8') as csv_file:  # Obrim el fitxer en mode lectura
            csvreader = csv.reader(csv_file, delimiter=',')  # Creem un objecte per llegir un fitxer csv
            fields = next(csvreader)
            for index, linia in enumerate(csvreader):  # Per cada línia,
                if index > self.MAX_LLIBRES:  # Si ja hem enregistrat més de 100.000 llibres,
                    break  # Parem
                book = Llibre(index, linia[1], linia[0], linia[2], linia[3])  # Creem un llibre
                self._items[book.isbn] = book  # Afegim el llibre al diccionari

        # Llegim el document de usuaris
        # Inicialitzem la llista d'usuaris: Usuaris
        ruta_fitxer = os.path.join(nom_directori + 'Books/Users.csv')  # Creem la ruta on es troba el fitxer
        with open(ruta_fitxer, 'r', encoding='utf8') as csv_file:  # Obrim el fitxer en mode lectura
            csvreader = csv.reader(csv_file, delimiter=',')  # Creem un objecte per llegir un fitxer csv
            fields = next(csvreader)
            for index, linia in enumerate(csvreader):  # Per cada línia,
                if index > self.MAX_USUARIS:  # Si ja hem enregistrat 15000 usuaris,
                    break  # Parem
                usuari = Usuari(int(linia[0]), linia[1].split(','), linia[2])  # Creem l'usuari
                self._usuaris[usuari.idd] = usuari
                # self._usuaris.append(usuari)  #L'afegim a la llista d'usuaris

        # Inicialitzem l'array de ratings i Llegim el document de ratings
        self._ratings = np.zeros((len(self._usuaris), len(self._items)), dtype='int8')  # Creem array buit
        ruta_fitxer = os.path.join(nom_directori + 'Books/Ratings.csv')  # Creem la ruta on es troba el fitxer
        with open(ruta_fitxer, 'r', encoding='utf8') as csv_file:  # Obrim el fitxer en mode lectura
            csvreader = csv.reader(csv_file, delimiter=',')  # Creem un objecte per llegir un fitxer csv
            fields = next(csvreader)
            for linia in csvreader:  # Per cada línia,
                if int(float(linia[2])) != 0:
                    # print(linia)
                    if int(linia[0]) in self._usuaris and linia[1] in self._items:
                        # print(linia)
                        self._ratings[int(linia[0]) - 1, self._items[linia[1]].ordre] = int(float(linia[2]))
        return vocabulari  # retornem el vocabulari

# COMPROVACIONS
# Dataset pel.licules
# pelicula = Movies()
# pelicula.llegeix('Datasets/')

# Per guardar en un fitxer binari una còpia exacta de l’objecte
# with open("Movies.dat", 'wb') as fitxer:
#    pickle.dump(pelicula, fitxer)

# Dataset llibres
# book = Books()
# book.llegeix('Datasets/')

# Per guardar en un fitxer binari una còpia exacta de l’objecte
# with open("Books.dat", 'wb') as fitxer:
#    pickle.dump(book, fitxer)
