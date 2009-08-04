#!/usr/bin/env python
#-*- coding: utf-8 -*-

# Purist - Python URL shortener using SQLite 3, memcached and web.py

import web, sqlite3, memcache, random, string

cache = memcache.Client(['127.0.0.1:11211'])
dbfile = 'uris.db'

siteuri = "http://go.heyc.org.uk/"

uris = (
 "/",           "intro",
 "/api",        "api",
 # TODO: Implement stats!
 #"/(.*)!",      "stats",
 "/(.*)",       "uri"
)

conn = sqlite3.connect(dbfile)
c = conn.cursor()
app = web.application(uris, globals())
if __name__ == "__main__": app.run()
application = app.wsgifunc()

def urigen(bottom=0, top=9):
 length = random.randint(bottom, top)
 charpool = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
 chars = ''
 for char in random.sample(charpool, length): chars+=char
 return chars

def geturibycode(code):
 uricode = cache.get("[ii]" + str(code))
 if not uricode:
  uricode = c.execute("SELECT * FROM uri WHERE id='" + code + "'").fetchone()[1]
  cache.set("[ii]" + str(code), uricode, 86400) # expires in 24 hours
 return uricode

def seturibycode(code, uri):
 cache.set("[ii]" + str(code), uri, 86400)
 c.execute('INSERT INTO uri VALUES("' + code + '", "' + uri + '")')
 return conn.commit()

class intro:
 def GET(self):
  return """<!DOCTYPE html><html><head><title>URL Shortener</title></head><body>
  <h1>Purist - a URL shortener</h1>
  <form action="/api" method="get">
  <p><label><b>URL to shorten:</b><br><input type="text" name="uri"></label></p>
  <label><b>Optional custom URL:</b><br><input type="text" name="custom"></label><br>
  <p><input type="submit" value="Shorten it!"></p>
  </form>
  <p><b>API:</b> /api?uri=<em>URL to be shortened</em>&custom=<em>Optional custom name</em>. Returns short URL as text</p>
  </body></html>"""

class uri:
 def GET(self, path): 
  try:
   web.seeother(geturibycode(path))
  except:
   web.seeother("/")

class api:
 def GET(self):
  customuri = web.websafe(web.input(custom="").custom)
  if not web.input(uri="").uri == "":
   if customuri == "":
    customuri = urigen()
    seturibycode(customuri, web.input(uri="").uri);
    return siteuri + customuri
   else:
    seturibycode(customuri, web.input(uri="").uri);
    return siteuri + customuri
