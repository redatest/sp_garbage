# -*- coding: utf-8 -*-

from django.db import models

class profile_candid_querySets(models.query.QuerySet): 

    def idf_candidates_count(self):
       return self.filter(region = 5).count()

    def midi_candidates_count(self):
       return self.filter(region = 16).count()

    def paca_candidates_count(self):
       return self.filter(region = 14).count()

    def calais_candidates_count(self):
       return self.filter(region = 1).count()

    def bretagne_candidates_count(self):   
        return self.filter(region = 6).count()
   
class profile_candid_manager(models.Manager):
    def get_query_set(self):
        return profile_candid_querySets(self.model)

    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)

