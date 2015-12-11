import ephem, math, pytz, json
from ephem import cities
from flask import Flask, jsonify, request
from datetime import datetime
from urllib.parse import quote

app = Flask(__name__)
__version__ = 1
v = __version__
host = 'http://astropos.sphygm.us'

@app.route('/')
@app.route('/api')
@app.route('/api/v{0}'.format(v))
def index():
  return "Welcome to the Astropos API!"

@app.route('/api/v{0}/stars/<string:star_name>'.format(v), methods=['GET'])
@app.route('/api/v{0}/stars/<string:star_name>/<string:loc_name>'.format(v), methods=['GET'])
@app.route('/api/v{0}/bodies/<string:body_name>'.format(v), methods=['GET'])
@app.route('/api/v{0}/bodies/<string:body_name>/<string:loc_name>'.format(v), methods=['GET'])
def get_body_data(star_name=None, body_name=None, loc_name=None):
  try:
    try:
      loc = cities.lookup(loc_name) if loc_name else None
    except:
      return errors(400, 'Invalid observer location: {0}'.format(loc_name))

    if body_name:
      try:
        body = getattr(ephem, body_name.title())()
      except:
        return errors(400, 'Invalid body name: {0}'.format(body_name))
    elif star_name:
      try:
        body = ephem.star(star_name.title())
      except:
        return errors(400, 'Invalid star name: {0}'.format(star_name))

    body.compute(loc) if loc else body.compute()

    try:
      cons = ephem.constellation(body)
    except:
      cons = None
      pass

    result = {}
    data = {'id': body.name, 'type': 'body' if body_name else 'star'}
    links = {'self': host+quote(request.path)}
    result['data'] = data
    result['links'] = links

    bodydata = {}
    data['attributes'] = bodydata
    addstr(bodydata,body,['name','neverup','circumpolar'])
    adddeg(bodydata,body,['alt','az','ra','dec','elong','radius','a_ra','a_dec','g_ra','g_dec','hlon','hlat','libration_lat','libration_long','colong','subsolar_lat','cmlI','cmlII'])
    addnum(bodydata,body,['mag','phase','sun_distance','earth_distance','size','x','y','z','moon_phase','earth_tilt','sun_tilt','earth_visible','sun_visible'])
    adddate(bodydata,body,['rise_time','transit_time','set_time'])
    if cons:
      bodydata['constellation_abbr'] = cons[0]  
      bodydata['constellation'] = cons[1]  
  
    if loc:
      observer = {}
      data['relationships'] = {'observer': observer}
      addstr(observer,loc,['name'])
      adddeg(observer,loc,['lat','lon'])
      adddate(observer,loc,['date'])

    return json.dumps(result, sort_keys=True, indent=4, ensure_ascii=False), 200, {'Content-Type': 'application/json; charset=utf-8'}
  except Exception as ex:
    return errors(500, 'Internal server error: {0}'.format(str(ex)))

def addstr(dict, obj, attrlist):
  add(dict, obj, attrlist, str)
def adddeg(dict, obj, attrlist):
  add(dict, obj, attrlist, rtd)
def addnum(dict, obj, attrlist):
  add(dict, obj, attrlist, float)
def adddate(dict, obj, attrlist):
  add(dict, obj, attrlist, isodate)
def add(dict, obj, attrlist, func):
  for attr in attrlist:
    try:
      if (hasattr(obj,attr)): dict[attr] = func(getattr(obj,attr))
    except:
      pass

def rtd(radians):
  return 180*float(radians)/math.pi

def isodate(datestr):
  if datestr:
    return datetime.strptime(str(datestr),'%Y/%m/%d %H:%M:%S').replace(tzinfo=pytz.timezone('UTC')).isoformat()
  else:
    return "None"

def errors(status, detail):
  response = jsonify({'errors': [{'status': str(status), 'detail': detail}] })
  response.status_code = status
  return response


if __name__ == '__main__':
  app.run(debug=True)

