# -*- coding: utf-8 -*-
"""
Fitxer de python que conté la classe Items, Movie i Llibre del projecte.

@author: Lucía Revaliente i Aránzazu Miguélez
"""
# IMPORTS
from abc import ABCMeta, abstractmethod
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import os
from Usuari import Usuari
from Items import Items, Movie, Llibre
from Dataset import Movies, Books
from sklearn.model_selection import train_test_split


# CLASSE ABSTRACTA RECOMANACIO
class Recomanacio(metaclass=ABCMeta):
    def __init__(self, dataset="", usuari=""):
        self._dataset = dataset
        self._usuari = usuari

    @property
    def usuari(self):
        return self._usuari

    @abstractmethod
    def calcul_score(self):
        raise NotImplementedError

    @staticmethod
    def preguntar_usuari(recomanacions):
        """"
        Funció utilitzada per preguntar a l'usuari quants ítems vols que li recomanem
        Parameters
        -------
        recomanacions: list[Items]. Llista amb totes les recomanacions.

        Returns
        -------
        None
        """
        if len(recomanacions) == 0:  # Si l'estructura de dades de recomanacions és buida,
            print("\nERROR: No es troba cap item per recomanar")
        else:  # Sinó,
            res = 'si'
            while res == 'si':
                try:
                    # Preguntem quantes recomanacions vol mostrar per pantalla
                    num_recomanacio = int(input('\nEn total hi ha ' + str(
                        len(recomanacions)) + ' recomanacions. Quants ítems vols que et recomanem? '))

                    # Mostrem per pantalla <num_recomanacio> items
                    print('\nLes recomanacions són:\n')
                    for i in range(num_recomanacio):
                        print(recomanacions[i], '\n')

                except ValueError:  # Si ha algun error,
                    print('\nERROR: El valor introduït no és un nombre enter. Torna-ho a provar.\n')
                else:
                    res = 'no'

    def mostrar_recomanacions(self, sorted_score: dict):
        """
        Funció que obté un diccionari amb puntuacions ordenades, les passa a una llista i mostra per pantallas tantes
        recomanacions com l'usuari vulgui.

        Parameters
        -------
        sorted_score: dict[float: int]. Diccionari on la clau és la puntuació que obté l'ítem i el valor és l'ordre
        d'aquest.

        Returns
        -------
        recomanacions: list[Items]. Llista amb totes les recomanacions.
        """
        recomanacions = []  # Inicialitzem la llista de recomanacions
        ordres = {item.ordre: item for item in self._dataset.items.values()}  # Obtenim els items corresponents a
        # cada ordre

        for puntuacio, llista in sorted_score:  # Per cada llista d'ítems de cada puntuació,
            for ordre in llista:  # Obtenim els ordres de cada item
                recomanacions.append(
                    ordres[ordre])  # Busquem l'ítem corresponent i l'afegim a la llista de recomanacions
        return recomanacions

    def avalua(self, llindar: int, n: int):
        # Obtenim la valoració de l'usuari (simple i col·laboratiu):

        valoracio = self._dataset.ratings[self._usuari.idd - 1, :]  # Obtenim la valoracio
        valoracio_no_zero = valoracio != 0  # Identifiquem les que son != 0
        # print(valoracio.shape, valoracio_no_zero.shape)
        ordres = {item.ordre: item for item in self._dataset.items.values()}  # Obtenim els items corresponents a
        x = 0

        if any(valoracio_no_zero):
            res = 'si'
        else:
            print("L'usuari no ha valorat res.")
            return False

        print("\nLes valoracions de l'usuari són:")
        for i in range(len(valoracio)):
            if (x < n):
                if valoracio_no_zero[i] != False and valoracio[
                    i] > llindar:  # si la valoració no és 0 i és més gran que el llindar
                    item = ordres[i]  # obtenim el ítem
                    print("Id: ", item.title, 'Valoracio: ', valoracio[i])  # Imprimim per pantalla
                    x += 1

        return valoracio[valoracio_no_zero]


# CLASSE RECOMANACIO SIMPLE
class Recomanacio_simple(Recomanacio):
    def __init__(self, dataset='', usuari='', min_vots=-1, array_avg=''):
        super().__init__(dataset, usuari)
        self._min_vots = min_vots
        self._array_avg = array_avg

    def calcul_avg(self):
        """
        Funció que crea una matriu amb les mitjanes de les puntuacions de cada item. A més, indica el número de vots
        per a cada item. La funció també calcula la mitjana de les mitjanes de les puntuacions dels items.

        Returns
        -------
        avg_array : np.array. Matriu de numpy. La primera fila representa les puntuacions mitjanes de
        cada item. Cada columna és un item. La segona fila representa el número de vots per cada item. avg_global :
        float. Mitjana de la primera fila de la matriu avg_array
        """
        avg_array = np.zeros((2, len(self._dataset.items)),
                             dtype="float16")  # Creem un array per emmagatzemar avg de cada pelicula
        ratings = self._dataset.ratings  # Obtenim el dataset de ratings
        n_files, n_columnes = ratings.shape
        for item in range(n_columnes):  # Per cada item,
            nota = ratings[:, item]  # Obtenim les notes de tots els usuaris
            notas = np.delete(nota, self._usuari.idd - 1)  # Esborrem la nota de l'usuari al que li recomanarem items
            if len(notas[notas != 0]) >= self._min_vots:  # Si hi ha el mínim vots desitjats,
                avg_array[0, item] = notas[
                    notas != 0].mean()  # Calculem la mitjana de vots entre tots els usuaris sense tenir en compte
                # els zeros
                avg_array[1, item] = len(notas[notas != 0])  # Afegim número de vots
        puntuacions = avg_array[0][avg_array[0] != 0]  # Obtenim les puntuacions mitjanes
        avg_global = np.nanmean(puntuacions)  # Calculem l'avg_global
        return avg_array, avg_global

    def calcul_score(self):
        """
        Funció que calcula les puntuacions per a cada item que l'usuari al que recomanem items no ha vist.
        A més, mostra per pantalla els num_recomanacio items que l'usuari desitji. Ex: els 5 items que més em
        poden agradar.

        Returns
        -------
        dic_score: list[Tuple[float, int]]. Llista de tuples. La primera posició de la tupla és la puntuació i la segona
        l'ordre en l'array de ratings.
        recomanacions: list[Items]. Llista amb tots els items que recomanaríem en ordre decreixent.
        """
        avg_array, avg_global = self.calcul_avg()  # Calculem array_avg i avg_global
        dic_score = {}  # Inicialitzem el diccionari de puntuacions

        linia_v1 = self._dataset.ratings[self._usuari.idd - 1, :]  # Obtenim la línia de l'usuari v1
        # (al que li recomanarem els items)
        items = np.where(linia_v1 == 0)  # Obtenim les columnes (items) per les quals hem de calcular la puntuació

        for columna in items[0]:  # Per cada item que no hagi puntuat l'usuari v1,
            avg_item = avg_array[0, columna]  # Obtenim mitjana de vots per aquest item
            num_vots = avg_array[1, columna]  # Obtenim número de vots per aquest item
            score = ((num_vots / (num_vots + self._min_vots)) * avg_item) + (
                    (self._min_vots / (num_vots + self._min_vots)) * avg_global)  # Calculem puntuacio
            if score in dic_score:  # Si ja havíem enregistrat la puntuació,
                dic_score[score].append(columna)  # L'afegim
            else:  # Sinó,
                dic_score[score] = [columna]  # l'enregistrem
        sorted_score = (sorted(dic_score.items()))[::-1]  # Ordenem el diccionari de major a menor
        # print(sorted_score)
        recomanacions = self.mostrar_recomanacions(sorted_score)  # Obtenim les recomanacions
        return dic_score, recomanacions

    def avalua(self, llindar: int, n: int):
        """
        Funció que avalua el sistema de recomanació de contingut. Mostra per pantalla els valors de MAE,
        precision i recall.
        :return: None
        """
        valoracio_usr = super().avalua(llindar, n)  # Obtenim les valoracions del usr != 0
        if type(valoracio_usr) == bool:
            print("Com l'usuari no ha puntuat, no podem avaluar")
            return False

        prediccio_dic, recomanacions = Recomanacio_simple(self._dataset, self._usuari, self._min_vots).calcul_score()
        # el que canvia amb la simple es la k i el min vots
        prediccions = np.array([prediccio_dic.keys()])
        # print(prediccio_dic.values())
        puntuacions = {}

        # ESTO ES LO QUE DA PROBLEMAS, ACCEDER A LA PUNTUACION PORQUE CADA VALUE DEL DICCIONARIO ES UNA LISTA
        for puntuacio, ordre in prediccio_dic.items():
            for element in ordre:
                puntuacions[element] = puntuacio
        # puntuacions = {element: puntuacio for puntuacio, ordre in prediccio_dic.values() for element in ordre}
        print("\nLes prediccions de l'usuari són:")
        for i in range(n):
            ordre = recomanacions[i].ordre
            print("Id: ", recomanacions[i].title, "Puntuació: ", puntuacions[ordre])

        if valoracio_usr.size != 0:  # si l'usuari ha valorat i no dona error,
            avaluem = Avaluacio(self._dataset, self._usuari, llindar, prediccions,
                                valoracio_usr, n)  # incialitzem l'avaluació
            avaluem.mesures_comparacio()
        else:
            print("L'usuari no ha puntuat, per tant no podem avaluar")


# CLASSE RECOMANACIO COL.LABORATIVA
class Recomanacio_colaborativa(Recomanacio):
    def __init__(self, dataset='', usuari='', k=-1):
        super().__init__(dataset, usuari)
        self._k = k

    def similitud_vectors(self):
        """
        Funció que retorna la similitud entre dos usuaris.

        Returns
        -------
        dic_similituds: dict {distancia: fila}. Diccionari on la key és la distància (float) entre dos usuaris i el
        value la fila de la matriu, és a dir, l'idd-1 del usuari al que hem calculat la distància respecte a l'usuari
        al que recomanem items
        """
        dic_similituds = {}  # inicialitzem el diccionari de similituds
        v1 = self._usuari  # establim v1 com el usuari que volem recomanar
        puntuacions_v1 = self._dataset.ratings[v1.idd - 1, :]  # Obtenim totes les valoracions del usuari v1

        for fila in range(
                len(self._dataset.ratings)):  # recorrem l'array de puntuacions. Cada fila correspon a un usuari
            if fila != v1.idd - 1:
                puntuacions_v2 = self._dataset.ratings[fila, :]  # Obtenim les puntuacions de l'usuari v2

                # Inicialitzem comptadors:
                numerador = 0
                denominador_v1 = 0
                denominador_v2 = 0

                for element_v1, element_v2 in zip(puntuacions_v1, puntuacions_v2):  # Recorrem les puntuacions
                    if element_v1 != 0 and element_v2 != 0:  # Si són diferents de 0, fem els sumatoris
                        numerador += element_v1 * element_v2
                        denominador_v1 += element_v1 ** 2
                        denominador_v2 += element_v2 ** 2

                if denominador_v1 == 0 or denominador_v2 == 0:  # Si es dividirà per zero,
                    distancia = None  # Aquests usuari no ha puntuat cap item per tant, no el tindrem en compte
                else:  # sinó,
                    distancia = numerador / ((denominador_v1 ** 0.5) * (denominador_v2 ** 0.5))  # Calculem la distancia
                    dic_similituds[
                        distancia] = fila  # Afegim al diccionari la distància amb la posicio en la matriu com a valor
        return dic_similituds

    def calcul_k_similars(self):
        """
        Funció que crea un nou array afegint dues columnes: similitud entre usuaris i la mitjana de les puntuacions de
        cada usuari. Ho afegim a l'array principal perquè si en fem un de nou no sabrem quina posició té i no podrem
        buscar-lo després.

        La primera part consisteix en buscar els k similars. Crida a similitud_vectors(), ordena les distancies de
        major a menor i sel·leciona els k primers. Això ho fa perquè recorre l'array i només mira les similituds != -1.
        Si no hi ha k elements amb similituds, retorna un avis i es queda amb el màxim k trobat.

        La segona part consisteix en buscar la mitjana. Per cada línia, calcula la mitjana de les puntuacions i
        ho afegeix. Els usuaris no selecionats (no son k), tenen de mitjana -1 perquè no ens cal aquest paràmetre.

        Potser aquesta funció és ineficient perquè hem de verificar per cada línia si hi ha un -1 o no, però ho fem
        així per poder saber la posicio de l'ítem. Potser l'ideal seria utilitzar l'array de numpy que no emmagatzema
        a memòria les posicions buides (que serien els nostres -1).

        Returns
        -------
        array_final: np.array. Array de ratings on s'han afegit dues columnes: columna de similituds en la columna [-2]
        i columna de mitjanes en la columna [-1]. Només els k elements tindran valors en aquestes posicions. La resta
        té el valor -1.

        """
        # BUSQUEM ELS K SIMILARS:
        dic_similituds = self.similitud_vectors()  # Obtenim les distàncies entre els usuaris
        similituds_sorted = sorted(dic_similituds.items())[::-1]  # Ordenem el diccionari formant una tupla
        similituds = np.ones(shape=len(self._dataset.ratings), dtype="float64") * (
            -1)  # Inicialitzem l'array de puntuacions
        for i in range(self._k):  # Seleccionem k,
            similitud, ordre = similituds_sorted[i][0], similituds_sorted[i][
                1]  # Obtenim la putuacio i l'ordre en la matriu
            if similitud != -1:  # Si existeix una similitud,
                similituds[ordre] = similitud  # Afegim la puntuacio a l'array
            else:  # Sinó,
                print("No hi ha k pel·lícules que et poguem recomanar")
        array = np.concatenate((self._dataset.ratings, similituds.reshape(-1, 1)),
                               axis=1)  # Fem un append de l'array per afegir-la com a columna: creem un array nou

        # CALCULEM LES MITJANES DE LES PUNTUACIONS (SENSE TENIR EN COMPTE ELS ZEROS):
        mitjanes = np.ones(shape=len(self._dataset.ratings), dtype="float64") * (-1)  # Inicialitzem l'array de mitjanes
        for usuari in range(len(self._dataset.ratings)):  # recorrem cada fila dels ratings
            if usuari == self._usuari.idd - 1:  # Si és l'usuari al que recomanem els items,
                mitjana = self._dataset.ratings[usuari, :][(self._dataset.ratings[usuari,
                                                            :]) != 0].mean()  # calculem la mitjana de les
                # puntuacions que ha donat l'usuari sense tenir en compte els zeros
                mitjanes[usuari] = mitjana  # Afegim la mitjana a l'array

            elif array[usuari][-1] != -1:  # Si és un dels k usuaris
                mitjana = self._dataset.ratings[usuari, :][(self._dataset.ratings[usuari, :]) != 0].mean()  # calculem
                # la mitjana de les puntuacions que ha donat l'usuari sense tenir en compte els zeros
                mitjanes[usuari] = mitjana  # Afegim la mitjana a l'array
        array_final = np.concatenate((array, mitjanes.reshape(-1, 1)),
                                     axis=1)  # 'afegim en forma de columna al nostre array de ratings
        return array_final

    def calcul_score(self):
        """
        Funció que retorna una llista amb els k elements recomanats, ordenats de major a menor. A més, mostra per
        pantalla tants com vulgui l'usuari.

        Primer obté l'array amb les similituds i mitjanes cridant a la funció calcul_k_similars(). Després, obté la
        línia de l'usuari al que li recomanem els items.

        Per poder calcular les puntuacions dels ítems encara no valorats, obté dos arrays de numpy. 'items' són les
        columnes de la matriu 'array' on es troben els items no valorats per l'usuari. 'usuaris'són les files de la
        matriu 'array' on es troben els k usuaris més similars.

        A partir d'aquí, es calculen les puntuacions per cada item i es guarden ordenades de major a menor. Es pregunta
        a l'usuari quantes recomanacions vols que es mostrin per pantalla i es retorna la llista total.

        Returns
        -------
        dic_score: list[Tuple[float, int]]. Llista de tuples. La primera posició de la tupla és la puntuació i la segona
        l'ordre en l'array de ratings.
        recomanacions: list[Items]. Llista on es retornen tots els ítems recomanats per l'Usuari, ordenats de major
        probabilitat de que li agradi a menys.
        """
        dic_score = {}  # Inicialitzem el diccionari de puntuacions

        array = self.calcul_k_similars()  # Obtenim l'array amb les puntuacions, la similitud i les mitjanes
        linia_v1 = array[self._usuari.idd - 1, :]  # Obtenim la línia de l'usuari v1 (al que li recomanarem els items)
        items = np.where(linia_v1[:-2] == 0)  # Obtenim les columnes (items) per les quals hem de calcular la puntuació
        usuaris = np.where(array[:, -2] != -1)  # Obtenim les files (usuaris) que hem d'incloure els càlculs
        # print(usuaris)  #La longitus de l'array ha de ser equivalent a k
        for columna in items[0]:  # Per cada ítem que l'usuari no ha puntuat (no ha vist),
            # Inicialitzem els sumatoris,
            numerador = 0
            denominador = 0
            for fila in usuaris[0]:  # Per cada k usuari,
                numerador += array[fila, -2] * (
                        array[fila, columna] - array[fila, -1])  # Realitzem sumatori del numerador
                denominador += array[fila, -2]  # Realitzem sumatori del denominador
            puntuacio = linia_v1[-1] + (
                    numerador / denominador)  # Calculem la puntuacio final per a aquesta columna (item)
            if puntuacio in dic_score:  # Si la puntuacio estava enregistrada,
                dic_score[puntuacio].append(columna)  # l'afegim a la llista
            else:  # Sinó,
                dic_score[puntuacio] = [columna]  # L'enregistrem al diccionari
        sorted_score = (sorted(dic_score.items()))[::-1]  # Ordenem el diccionari de major a menor
        recomanacions = self.mostrar_recomanacions(sorted_score)  # Obtenim les recomanacions
        return dic_score, recomanacions

    def avalua(self, llindar: int, n: int):
        """
        Funció que avalua el sistema de recomanació de contingut. Mostra per pantalla els valors de MAE,
        precision i recall.
        :return: None
        """
        valoracio_usr = super().avalua(llindar, n)  # Obtenim les valoracions del usr != 0
        if type(valoracio_usr) == bool:
            return False
        prediccio_dic, recomanacions = Recomanacio_colaborativa(self._dataset, self._usuari, self._k).calcul_score()
        # el que canvia amb la simple es la k i el min vots
        prediccions = np.array([prediccio_dic.keys()])
        puntuacions = {element: puntuacio for puntuacio, ordre in prediccio_dic.items() for element in ordre}

        print("\nLes prediccions de l'usuari són:")
        for i in range(n):
            ordre = recomanacions[i].ordre
            print("Id: ", recomanacions[i].title, "Puntuació: ", puntuacions[ordre])

        if valoracio_usr.size != 0 or valoracio_usr[0] is not np.isnan():  # si l'usuari ha valorat i no dona error,
            avaluem = Avaluacio(self._dataset, self._usuari, llindar, prediccions, valoracio_usr,
                                n)  # incialitzem l'avaluació
            avaluem.mesures_comparacio()
        else:
            print("L'usuari no ha puntuat, per tant no podem avaluar")


# CLASSE RECOMANACIÓ EN BASE AL CONTINGUT
class Recomanacio_contingut(Recomanacio):
    def __init__(self, dataset='', usuari='', pmax=-1):
        super().__init__(dataset, usuari)
        self._pmax = pmax

    @property
    def pmax(self):
        return self._pmax

    @abstractmethod
    def calcul_tf_idf(self):
        pass

    def perfil_usuari(self, tdidf_matriu):
        """
        Funció que retorna el perfil d'un usuari.
        :return perfil_usuari: np.array. Vector que correspon al perfil d'un usuari. Té tants elements com items
        """
        matriu_shape = tdidf_matriu.shape  # Obtenim la seva dimensió
        puntuacio_u1 = self._dataset.ratings[self._usuari.idd - 1, :]  # Obtenim la puntuacio de l'usuari al que
        # volem recomanar
        if np.sum(puntuacio_u1) == float(0):
            print('L\'usuari no ha puntuat cap ítem. Per tant, no realitzarem cap recomanació.')
            return -1
        else:
            perfil_usuari = np.sum(np.multiply(puntuacio_u1, tdidf_matriu.T), axis=1) / np.sum(
                puntuacio_u1)  # Calculem el perfil amb la fórmula
            return perfil_usuari

    def calcul_distancia(self, tdidf_matriu):
        """
        Funció que calcula la distància entre l'usuari i tots els ítems.
        :return:
        """
        perfil_usuari = self.perfil_usuari(tdidf_matriu)  # obtenim el perfil de l'usuari
        if type(perfil_usuari) == int:  # si l'usuari no ha puntuat res
            return -1  # retornem un -1
        else:  # sinó
            distancia_matriu = np.dot(tdidf_matriu, perfil_usuari)  # calculem la distància
            return distancia_matriu

    def calcul_score(self):
        """
        Funció que calcula la puntuació final de cada ítem.

        Returns
        -------
        dic_score: list[Tuple[float, int]]. Llista de tuples. La primera posició de la tupla és la puntuació i la segona
        l'ordre en l'array de ratings.
        recomanacions: list[Items]. Llista on es retornen tots els ítems recomanats per l'Usuari, ordenats de major
        probabilitat de que li agradi a menys.
        """
        matriu_tf_idf = self.calcul_tf_idf()  # Calculem la matriu de
        distancia_matriu = self.calcul_distancia(matriu_tf_idf)
        if type(distancia_matriu) != int:
            puntuacio_final = (self._pmax * distancia_matriu)
            puntuacions = {puntuacio: [i] for i, puntuacio in enumerate(puntuacio_final)}
            sorted_score = (sorted(puntuacions.items()))[::-1]  # Ordenem el diccionari de major a menor obtenint una
            # llista amb tuples: la primera posició és la puntuació i la segona l'ordre
            recomanacions = self.mostrar_recomanacions(sorted_score)
        return puntuacions, recomanacions

    def avalua(self, llindar: int, n: int):
        """
        Funció que avalua el sistema de recomanació de contingut. Mostra per pantalla els valors de MAE,
        precision i recall.
        :return: None
        """
        valoracio_usr = super().avalua(llindar, n)  # Obtenim les valoracions del usr != 0
        if type(valoracio_usr) == bool:
            print("Com l'usuari no ha puntuat,no podem avaluar")
        if valoracio_usr.size != 0:  # si l'usuari ha valorat i no dona error,
            avaluem = Avaluacio(self._dataset, self._usuari, llindar, n)  # incialitzem l'avaluació
            avaluem.calculem_prediccions_contingut()
            avaluem.mesures_comparacio()
        else:
            print("L'usuari no ha puntuat, per tant no podem avaluar")


# CLASSE RECOMANACIÓ EN BASE AL CONTINGUT - Movies
class Recomanacio_contingut_movies(Recomanacio_contingut):
    def calcul_tf_idf(self):
        """
        Funció que retorna una matriu amb la representació tf-idf.
        :return tfidf_matriu: np.array. Matriu amb la representació tf-idf. Les files representen els items i les
        columnes la puntuació tf-idf.
        """
        ll_generes = [item.genere for item in
                      self._dataset.items.values()]  # Obtenim la llista de gèneres per cada ítem
        tfidf = TfidfVectorizer(stop_words='english')  # Incialitzem vector
        return tfidf.fit_transform(ll_generes).toarray()  # Creem la matriu amb la puntuacio tfidf


# CLASSE RECOMANACIÓ EN BASE AL CONTINGUT - Books
class Recomanacio_contingut_books(Recomanacio_contingut):
    @staticmethod
    def delete_words(nom_directori: str):
        """
        Funció que elimina els articles i paraules no rellevants d'un string.
        :param nom_directori: str. Nom del directori on es troben els fixterrs amb les paraules no rellevants.
        :return resultat: str. paraules rellevants de un str (sense els caràcters invalids), en míniscules i separades
        pel caràcter '|'.
        """
        ruta_fitxer_prep = os.path.join(
            nom_directori + '/prepositions.csv')  # Creem la ruta on es troba el fitxer de preposicions
        ruta_fitxer_num = os.path.join(nom_directori + '/numeros.txt')  # Creem la ruta on es troba el fitxer de numeros
        invalid = ['!', '?', '¿', '\)', '\(', '/', '$', '&', '%', '#', '@', ',', ':', '.', '\"', '\'', '<', '>',
                   '*', ]  # Inicialitzem llista de simbols invalids,
        with open(ruta_fitxer_prep, 'r') as Invalid:  # Llegim el document de preposicions i articles
            for linia in Invalid:  # Per cada línia,
                word = linia[:-1].split(',')  # Obtenim les preposicions i articles
                invalid.append(word[1])  # Afegim les paraules a la llista de caracters invalids

        with open(ruta_fitxer_num, 'r') as Invalid:  # Llegim el document de numeros
            text = Invalid.read().split(',')
            for i in text:
                invalid.append(i)
        return invalid  # retornem la llista

    def calcul_tf_idf(self):
        """
        Funció que retorna una matriu amb la representació tf-idf.
        :return tfidf_matriu: np.array. Matriu amb la representació tf-idf. Les files representen els items i les
        columnes la puntuació tf-idf.
        """
        invalid = self.delete_words('Datasets')
        # print(invalid)
        ll_generes = [item.title + '|' + item.autor for item in
                      self._dataset.items.values()]  # Obtenim la llista de gèneres per cada ítem
        # print(ll_generes, len(ll_generes))
        tfidf = TfidfVectorizer(stop_words=invalid)  # Incia litzem vector
        return tfidf.fit_transform(ll_generes).toarray()  # Creem la matriu amb la puntuacio tfidf


# CLASSE AVALUACIÓ
class Avaluacio:
    def __init__(self, dataset='', usuari='', llindar=-1, prediccio=np.zeros(1), valoracions=np.zeros(1), n=-1):
        self._dataset = dataset
        self._usuari = usuari  # Array de numpy (1,) amb les valoracions de l'usuari. A l'hora de fer els càlculs
        self._prediccions = prediccio  # Array de numpy (1,) amb les prediccions calculades pel nostre sistema.
        # només tindrem en compte els ítems on la valoracio!=0.
        self._valoracions = valoracions
        self._llindar = llindar  # En el cas de movies: llindar=4 i en el de books llindar=7
        self._n = n

    def crear_conjunt_train_test(self, llindar):
        """
        Funció que crea el conjunt d'entrenament i de test a partir de l'array de ratings.
        :param llindar: int
        :return: np.array, np.array
        """
        train, test = train_test_split(self._dataset.ratings, test_size=0.2, random_state=50)
        self._llindar = llindar

        # print("Mida de la matriu de train: ", (train.shape))
        # print("Mida de la matriu de test: ", (test.shape))
        return train, test

    def entrenem_dades(self):
        """
        Funció que calcula la matriu tfidf i el perfil de l'usuari a partir de l'array de train
        :return: perfil_usuari : np.array, matriu_tf_idf : np.array
        """
        self._valoracions = self._dataset.ratings[self._usuari.idd - 1, :][
            self._dataset.ratings[self._usuari.idd - 1, :] != 0]  # Valoracio de l'usuari (train i test)
        if self._valoracions.size != 0:  # si les valoracions no són 0,
            train, test = self.crear_conjunt_train_test(self._llindar)  # creem conjunt test,train
        else:  # Sinó
            return None  # retornem None
        self._dataset._ratings = train

        if self._llindar == 4:  # si el llindar es 4 seran pel·lícules
            tf_idf = Recomanacio_contingut_movies(self._dataset, self._usuari).calcul_tf_idf()
            perfil = Recomanacio_contingut_movies(self._dataset, self._usuari).perfil_usuari(tf_idf)

        else:  # sinó seran llibres
            tf_idf = Recomanacio_contingut_books(self._dataset, self._usuari).calcul_tf_idf()
            perfil = Recomanacio_contingut_books(self._dataset, self._usuari).perfil_usuari(tf_idf)
        return perfil, tf_idf

    def calculem_prediccions_contingut(self):
        """
        Funció que calcula les prediccions de les puntuacions finals de cada ítem
        :return: None
        """
        train, test = self.crear_conjunt_train_test(self._llindar)
        perfil_usuari, matriu_tf_idf = self.entrenem_dades()
        self._dataset._ratings = test  # fem que sigui ratings de test per fer els càlculs

        if self._llindar == 4:  # si el llindar es 4 seran pel·lícules
            recomanacio = Recomanacio_contingut_movies()
            recomanacio._pmax = 5
        else:
            recomanacio = Recomanacio_contingut_books()
            recomanacio._pmax = 10

        if type(perfil_usuari) == int:  # si l'usuari no ha puntuat res
            return -1  # retornem un -1
        else:  # sinó
            distancia_matriu = np.dot(matriu_tf_idf, perfil_usuari)  # calculem la distància
        # calculem la puntuació final predecida per cada ítem
        if type(distancia_matriu) != int:
            puntuacio_final = (recomanacio.pmax * distancia_matriu)
            puntuacions_ordre = {puntuacio: [i] for i, puntuacio in enumerate(puntuacio_final)}
            puntuacions = [puntuacio for i, puntuacio in enumerate(puntuacio_final)]
        self._prediccions = np.array([puntuacions])  # retornem el diccionar i la llista de puntuacions predites

    def mesures_comparacio(self):
        # Calculem el MAE

        valoracio_list = self._dataset.ratings[self._usuari.idd - 1, :][
            self._dataset.ratings[self._usuari.idd - 1, :] != 0].tolist()
        pred_list = [x for i in self._prediccions for x in i]
        numerador = [abs(prediccio - valoracio) for prediccio, valoracio in zip(pred_list, valoracio_list) if
                     (valoracio != 0)]
        sum_numerador = np.sum(numerador)
        length_numerador = len(numerador)

        if length_numerador > 0 and not np.isnan(sum_numerador):
            mae = sum_numerador / length_numerador
        else:
            mae = None

        # Calculem la precisió

        dic = {pred: [val] for pred, val in zip(pred_list, valoracio_list)}
        dic_sorted = (sorted(dic.items()))[::-1]  # L'ordenem de major a menor i escollim les N millors
        suma = 0
        for prediccio, (valoracio) in dic_sorted[:self._n + 1]:
            if valoracio >= [self._llindar]:
                suma += 1
        precision = str((suma / self._n) * 100) + ' %'

        # Calculem el recall
        num = 0
        for prediccio, (valoracio) in dic_sorted[:self._n + 1]:
            if valoracio >= [self._llindar]:
                num += 1

        den = sum([1 for valoracio in self._valoracions if valoracio >= self._llindar])
        if den == 0:
            print("L'usuari no ha valorat res per sobre del llindar, no podem avaluar.")
            recall = None
        recall = str((num / den) * 100) + ' %'

        # Els mostrem per pantalla
        print('\nEl resultat de l\'avaluacio és:\n\tMae: ', mae, '\n\tPrecisió:', precision, '\n\tRecall:',
              recall)  # Mostrem per pantalla

# COMPROVACIONS
# Dataset prova
# ratings = np.array([[7,6,7,4,5,4], [6,7,0,4,3,4],[1,2,0,3,3,4],[1,0,1,2,3,0],[0,3,3,1,1,0]])
# print(ratings)

# dic_users = {}
# for i in range(4):
#     dic_users[i+1]=Usuari(i+1)

# dic_items = {}
# for i in range(6):
#     dic_items[i+1]=Movie(i+1)

# dataset_movies = Movies(dic_users, dic_items, ratings)

# recomanacio_colaborativa = Recomanacio_colaborativa(dataset_movies, Usuari(5), 2)
# res = recomanacio_colaborativa.calcul_score()


# Sistema recomanacio simple
# pelicula = Movies()
# pelicula.llegeix('Datasets/')
# recomanacio = Recomanacio_simple(pelicula, Usuari(2), 10)
#  # array_avg, avg_global = recomanacio.calcul_avg()
# recomanacions = recomanacio.avalua(4)

# llibre = Books()
#  llibre.llegeix('Datasets/')
#  recomanacio = Recomanacio_simple(llibre, Usuari(10), 10)
# # array_avg, avg_global = recomanacio.calcul_avg()
#  recomanacions = recomanacio.calcul_score()


# Sistema recomanacio col.laboratiu
# pelicula = Movies()
# pelicula.llegeix('Datasets/')
# recomanacio = Recomanacio_colaborativa(pelicula,Usuari(1),10).avalua(4)

# llibre = Books()
# llibre.llegeix('Datasets/')
# recomanacio = Recomanacio_colaborativa(llibre,Usuari(10),10).calcul_score()

# Sistema de recomanació per contingut
# Pel·lícules:
# pelicula = Movies()
# pelicula.llegeix('Datasets/')
# #print(pelicula.ratings[1,:][pelicula.ratings[1]==5])
# recomanacio = Recomanacio_contingut_movies(pelicula,Usuari(7), 5).avalua(4)  #li hem de pasar el llindar

# # Books:
# llibre = Books()
# llibre.llegeix('Datasets/')
# recomanacio = Recomanacio_contingut_books(llibre,Usuari(1), 10).avalua(7)
