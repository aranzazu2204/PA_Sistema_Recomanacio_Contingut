# -*- coding: utf-8 -*-
"""
Fitxer de python que conté la classe Items, Movie i Llibre del projecte.

@author: Lucía Revaliente i Aránzazu Miguélez
"""
# IMPORTS
from abc import ABCMeta, abstractmethod


# CLASSE ITEMS ABSTRACTA
class Items(metaclass=ABCMeta):
    def __init__(self, ordre=-1, title=''):
        self._ordre = ordre
        self._title = title
    
    @abstractmethod
    def __str__(self):
        raise NotImplementedError()
    
    @property
    def ordre(self):
        return self._ordre
    
    @property
    def title(self):
        return self._title
    
    
# CLASSE MOVIE
class Movie(Items):
    def __init__(self, ordre=-1, title='', idd=-1, genere=''):
        super().__init__(ordre, title)
        self._idd = idd
        self._genere = genere
        
    def __str__(self):
        return 'MovieId: ' + str(self._idd) + '\nTitle: ' + self._title + '\nGènere/s: ' + self._genere
    
    @property
    def idd(self):
        return self._idd
    
    @property
    def genere(self):
        return self._genere

    
# CLASSE LLIBRE
class Llibre(Items):
    def __init__(self, idd=-1, title='', isbn ='', autor='', any_publicacio=-1):
        super().__init__(idd, title)
        self._isbn = isbn
        self._autor = autor
        self._any_publicacio = any_publicacio
    
    def __str__(self):
        return 'Book ISBN: ' + str(self._isbn) + '\nTitle: ' + self._title + '\nAutor: ' \
            + self._autor + '\nAny publicacio: ' + str(self._any_publicacio)
        
    @property
    def isbn(self):
        return self._isbn
        
    @property
    def autor(self):
        return self._autor
    
    @property
    def any_publicacio(self):
        return self._any_publicacio
