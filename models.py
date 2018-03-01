# -*- coding: utf-8 -*-

from google.appengine.ext import ndb


class Sporocilo(ndb.Model):
    besedilo = ndb.StringProperty()
    nastanek = ndb.DateTimeProperty(auto_now_add=True)
    izbrisano = ndb.BooleanProperty(dafault=False)