# -*- coding: utf-8 -*-

from google.appengine.ext import ndb


class Sporocilo(ndb.Model):
    besedilo = ndb.StringProperty()
    # z ukazom auto_now_add=True se bo čas inastanka avtomatično zapisal, ko se bo vnos zapisal v bazo.
    nastanek = ndb.DateTimeProperty(auto_now_add=True)
    # Vsakič ko bomo ustvarili novo sporočilo, bo vrednost v njegovem polju
    # izbrisano avtomatično False.
    # Ko pa bomo v IzbrisHandlerju sporocilo izbrisali, mu bomo  spremenili to polje v True.
    izbrisano = ndb.BooleanProperty(default=False)


    # Vsi ostali property-ji na tej povezavi https://cloud.google.com/appengine/docs/python/ndb/properties#types.