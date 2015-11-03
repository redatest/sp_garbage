import datetime
from django.db import models

class OfferQuerySets(models.query.QuerySet): 
    #here we define simple filters (or any queryset)
    def watermarked(self):
       return self.filter(is_watermarked = True)

    def is_activated(self):
       return self.filter(activated = True).order_by('-created')

    # get activated offers for index page
    def index_is_activated(self):
       return self.filter(activated = True).order_by('-created')[:6]         

    # managers for the map   
    def get_map_idf_count(self):
       return self.filter(activated = True).filter(region = 5).count()

    def get_map_midi_count(self):   
       return self.filter(activated = True).filter(region = 16).count()

    def get_map_paca_count(self):   
       return self.filter(activated = True).filter(region = 14).count()

    def get_map_calais_count(self):   
       return self.filter(activated = True).filter(region = 1).count()

    def get_map_bretagne_count(self):   
       return self.filter(activated = True).filter(region = 6).count()   

   # managers for the offer type count
    def get_cdd_count(self):
       return self.filter(activated = True).filter(offerType = 4).count()
    def get_cdi_count(self):   
       return self.filter(activated = True).filter(offerType = 5).count()
    def get_stage_count(self):   
       return self.filter(activated = True).filter(offerType = 6).count()
    def get_interim_count(self):   
       return self.filter(activated = True).filter(offerType = 7).count()     

class OfferManager(models.Manager):
    def get_query_set(self):
        return OfferQuerySets(self.model)

    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)

