#!/usr/bin/env python
# coding=utf-8

# bližnjica do --> dev_appserver.py ./ <-- za copy/paste

import os
import jinja2
import webapp2

from models import Sporocilo

#  Pove Kje imamo HTML fajle
template_dir = os.path.join(os.path.dirname(__file__), "templates")

#  IF Autoescape == TRUE to prepreci JavaSCript Injection !!!
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


# BaseHandler je class, ki nam pomaga upravljati HTML datoteke preko Jinje.
class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if params is None:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))
#  BaseHandler poskusi uporabljat v vseh nadaljnih projektih zaradi priročnosti.
#  Handlerji kontrolirajo kateri HTML bo prikazan in kaj bo v njem
#  Vsi nadaljni Handlerji imajo podedovane značilnosti iz BaseHandlerja.

########################################################################################################################

class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("hello.html")

class RezultatHandler(BaseHandler):
    def post(self):
        #  Tu dobimo vnešeno vsebino katero smo vpisali v input polje v hello.html.
        #  Pomembno je da dostopaš do inputa preko Atributa name="NekiNeki"
        rezultat = self.request.get("input-sporocilo")

        #  Sporocilo = objekt kateri vsebuje atribut besedilo.
        #  Atributov se lahko doda tudi več, vendar jih moramo imeti v modelu.
        #  Primer: Sporocilo(besedilo=rezultat, avtor="Tisti Nekdo", Kraj="Rovte")
        sporocilo = Sporocilo(besedilo=rezultat)
        sporocilo.put()

        #  Še izpišemo v Browserju (self.write(NekiNeki)
        return self.write(rezultat)



#  ListHandler = Vsa sporočila
class ListHandler(BaseHandler):
    def get(self):
        #  Z ukazom Sporocilo.query().fetch() potegnemo sporočila iz baze.
        #  z Sporocilo.query(Sporocilo.izbrisano == False).fetch() pa vzamemo iz baze le tista sporočila
        #  katera imajo polje izbrisano nastavljeno na False. "Glej v models.py"

        seznam = Sporocilo.query(Sporocilo.izbrisano == False).fetch()
        params = {"seznam": seznam}
        return self.render_template("seznam.html", params=params)




class PosameznoSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        #  Z metodo .get_by_id() iz baze vzamemo sporocilo, katerega id je enak podanemu
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}
        return self.render_template("posamezno_sporocilo.html", params=params)




class UrediHandler(BaseHandler):
    def get(self, sporocilo_id):
        #  ideja = Vzeti sporočilo iz baze
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}

        #  In ga pokazati
        return self.render_template("uredi_sporocilo.html", params=params)


    def post(self, sporocilo_id):
        #  Vzamemo sporočilo iz baze.
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))

        #  Sporočilo posodobimo.
        sporocilo.besedilo = self.request.get("nov-text")

        #  In ga shranimo nazaj v bazo
        sporocilo.put()

        #  Uporabnika preusmerimo nazaj na seznam sporočil (po imenu name="NekiNeki")
        #  Pomen Preusmerjanja po imenu je v tem, da se lahko pot povezave spremeni
        #  ime pa ostane enako in ne potrebujemo spreminjati poti na več mestih.
        return self.redirect_to("seznam-sporocil")


# Dodatno:
# na strani https://stackoverflow.com/questions/6515502/javascript-form-submit-confirm-or-cancel-submission-dialog-box
# prvi ogovor pokaze kako lahko s pomocjo javascripta pokazemo potrditveno sporocilo

class IzbrisHandler(BaseHandler):
    def get(self, sporocilo_id):
        # vzamemo sporočilo iz baze.
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}

        #  prikazemo potrditveno spletno stran.
        #  Ker si pošljemo sporočilo, lahko prikažemo še kakšno informacijo o sporočilu.
        return self.render_template("ask_delete.html", params=params)

    def post(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))

        #  Sporočila ne izbrišemo, ampak ga zgolj "skrijemo"
        sporocilo.izbrisano = True

        #  In zapisemo nazaj v bazo
        sporocilo.put()
        self.redirect_to("seznam-sporocil")


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler), # Ta del ukaže prikaz HTML na glavni (Root) strani.
    webapp2.Route('/rezultat', RezultatHandler),
    #  Pot poimenujemo, da se lahko sklicemo nanjo ko preusmerimo uporabnika
    # Uporabljaj "name" za povezave do strani, da v primeru spremembe linka ostane isto
    webapp2.Route('/seznam', ListHandler, name="seznam-sporocil"),

     # Na to pot primejo linki oblike /sporocilo/{{poljubne števke}}
+    # sporocilo_id pa je zgolj poimenovanje, ki ga potem uporabimo v metodi,
+    # ki se klice ob prihodu na to pot.

     #  Ko bo uporabnik šel na URL naslov, ki bo zgledal nekako tako:
     #  http://mojapp.appspot.com/sporocilo/1234567890,
     #  bo naša GAE aplikacija vedela, da je 1234567890 ID sporočila,
     #  in ga bo vstavila v handler kot sporocilo_id.
     #  Handler bo nato preko tega ID-ja našel sporočilo v podatkovni bazi
     #  in ga poslal v naš HTML.
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>', PosameznoSporociloHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/edit', UrediHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/delete', IzbrisHandler),
], debug=True)
