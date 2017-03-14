"""`main` is the top level module for your Bottle application."""

# import the Bottle framework
from bottle import Bottle, debug, template, request, post, get
import json
import time, datetime

import urllib2
from google.appengine.ext import ndb

debug(True)
# Create the Bottle WSGI application.
bottle = Bottle()

class UserU(ndb.Model):

    id = ndb.IntegerProperty()
    email = ndb.StringProperty()
    password = ndb.StringProperty()
    money = ndb.FloatProperty()

class StationS(ndb.Model):

    id = ndb.IntegerProperty()
    location = ndb.StringProperty()
    state = ndb.StringProperty()
    user_id = ndb.IntegerProperty()
    start = ndb.DateTimeProperty()
    end = ndb.DateTimeProperty()

class ReadingR(ndb.Model):

    id = ndb.IntegerProperty()
    current = ndb.StringProperty()
    datetime = ndb.StringProperty()


class TransactionT(ndb.Model):

    duration = ndb.FloatProperty()
    amount = ndb.FloatProperty()
    user_id = ndb.IntegerProperty()

# HOMEPAGE
@bottle.post('/login')
def login():
    email = request.forms.get('email')
    password = request.forms.get('password')

    query = UserU.query(UserU.email == email, UserU.password == password).count()
    if query > 0:
        ret = "OK"
    else:
        ret = "NOK"
    return ret

    # print json2html.convert(json=infoFromJson)

# HOMEPAGE
@bottle.post('/register')
def register():
    email = request.forms.get('email')
    password = request.forms.get('password')

    query = UserU.query(UserU.email == email).count()
    if query:
        ret = "NOK"
    else:
        number = UserU.query().count()

        new_id = number + 1
        u = UserU(email=email, id=new_id, password=password, money = 100.0)
        u.put()
        ret = "OK"

    return ret

# HOMEPAGE
@bottle.post('/user/<user_id>/new_station')
def new_station(user_id):
    lat = request.forms.get('lat')
    lon = request.forms.get('lon')

    number = StationS.query().count()
    new_id = number + 1

    s = StationS(id=new_id,location=(lat+","+lon),state="false")
    s.put()
    return "OK"


@bottle.post('/user/<user_id>/money')
def money(user_id):
    user = UserU.query(UserU.id == int(user_id)).fetch(1)
    for u in user:
        money = u.money
    return str(money)

# HOMEPAGE
@bottle.post('/user/<user_id>/charge')
def charge(user_id):
    station_id = request.forms.get('station_id')

    user = UserU.query(UserU.id == int(user_id)).fetch(1)

    for u in user:
        money = u.money

    station = StationS.query(StationS.id == int(station_id)).fetch(1)

    for s in station:
        if s.state == "false":
            s.start = datetime.datetime.now()
            s.state = "true"
            s.user_id = int(user_id)
            s.put()
        elif s.state == "true":
            if(s.user_id == int(user_id)):
                s.end = datetime.datetime.now()
                s.state = "false"
                s.user_id = None
                s.put()
                t = TransactionT(user_id = int(user_id))
                t.duration = (s.end - s.start).total_seconds()
                t.amount = 0.3*t.duration
                t.put()
                for u in user:
                    u.money = u.money-t.amount
                    u.put()


    return "OK"

    #Ver se tem dinheiro na conta
    #Se sim, ver se station esta ocupada
    #Se não estiver, mudar estado

    #query = UserU.query(UserU.email == email).count()


# List available stations
@bottle.route('/station/<station_id>/new')
def new_station(station_id):
    s = StationS(id=int(station_id),state = "false")
    s.location = "38.738165,-9.139013"
    s.put()

    s = StationS(id=int(station_id)+1,state = "false")
    s.location = "38.720,-9.120"
    s.put()

    s = StationS(id=int(station_id)+2,state = "false")
    s.location = "38.74,-9.14"
    s.put()

    s = StationS(id=int(station_id)+3,state = "false")
    s.location = "38.745,-9.145"
    s.put()

    return "OK"


# List available stations
@bottle.route('/station/<station_id>/state')
def check_state(station_id):
    s = StationS.query(StationS.id == int(station_id)).fetch(1)

    for stud in s:
        ret = {'state' : stud.state }

    return json.dumps(ret, sort_keys=True)

# List available stations
@bottle.route('/api/stations')
def list_stations():
    stations = StationS.query().fetch()

    if not stations:
        ret = {"containedStations": []}
    else:
        array = []
        for s in stations:
            array.append({"id": s.id, "location": s.location, "state": s.state})
        ret = {"containedStations": array}

    return json.dumps(ret, sort_keys=True)

# List available stations
@bottle.post('/station/<station_id>/reading')
def receive_reading(station_id):
    station = StationS.query(StationS.id == int(station_id)).fetch(1)
    rec_obj = json.dumps(request.json)
    d = json.loads(rec_obj)
    #if not stations:
        #ret = "NOK"
    #else:
    reading = ReadingR(id=int(station_id), current=d["current"], datetime=d["datetime"])
    reading.put()
    ret = d

    return ret

# Print information error for resquest to non-defined URIs
@bottle.error(404)
def error_404(error):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.'
