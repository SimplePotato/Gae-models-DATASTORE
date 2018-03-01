#!/usr/bin/env python
import os
import jinja2
import webapp2

from models import Sporocilo

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)
                #  Autoescape nastavljen na TRUE prepreci vnos JavaSCript Injection !!!


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


class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("hello.html")

class RezultatHandler(BaseHandler):
    def post(self):
        rezultat = self.request.get("input-sporocilo")

        sporocilo = Sporocilo(besedilo=rezultat)
        sporocilo.put()

        return self.write(rezultat)

class ListHandler(BaseHandler):
    def get(self):
        seznam =Sporocilo.query().fetch()
        params = {"seznam": seznam}
        return self.render_template("seznam.html", params=params)

class PosameznoSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}
        return self.render_template("posamezno_sporocilo.html", params=params)

class UrediHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}
        return self.render_template("uredi_sporocilo.html", params=params)

    def post(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        sporocilo.besedilo = self.request.get("nov-text")
        sporocilo.put() #  shrani besedilo v bazo
        return self.redirect_to("seznam-sporocil")

class IzbrisHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}
        return self.render_template("izbrisi.html", params=params)

    def post(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))





app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/rezultat', RezultatHandler),
    webapp2.Route('/seznam', ListHandler, name="seznam-sporocil"),
    # uporabljaj "name" za povezave do strani, da v primeru spremembe linka ostane isto
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>', PosameznoSporociloHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/edit', UrediHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/delete', IzbrisHandler),
], debug=True)
