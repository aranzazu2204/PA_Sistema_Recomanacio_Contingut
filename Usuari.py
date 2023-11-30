# -*- coding: utf-8 -*-
"""
Fitxer de python que conté la classe Usuari del projecte.

@author: Lucía Revaliente i Aránzazu Miguélez
"""


# CLASSE USUARI
class Usuari:
    def __init__(self, idd=-1, edat=-1, poblacio='', professio=''):
        self._idd = idd
        self._edat = edat
        self._poblacio = poblacio
        self._professio = professio

    def __str__(self):
        return 'UsuariID: ' + str(self._idd) + '\nEdat: ' + str(
            self._edat) + '\nPoblacio: ' + self._poblacio + '\nProfessio: ' + self._professio

    @property
    def idd(self):
        return self._idd

    @property
    def edat(self):
        return self._edat

    @property
    def poblacio(self):
        return self._poblacio

    @property
    def professio(self):
        return self._professio
