#!flask/bin/python3

import ephem, math
from ephem import cities
from flask import Flask, jsonify
from inspect import ismethod

app = Flask(__name__)


@app.route('/')
def index():
  return "Welcome to the Astropos API!"

@app.route('/body/<string:body_name>/<string:observer_loc>', methods=['GET'])
def get_body_data(body_name, observer_loc):
  try:
    loc = cities.lookup(observer_loc)
  except:
    return errors('400', 'Invalid observer location: %s' % observer_loc)

  try:
    body = getattr(ephem, body_name.title())(loc)
  except:
    return errors('400', 'Invalid body name: %s' % body_name)

  try:
    cons = ephem.constellation(body)
  except:
    cons = None
    pass

#'compute_pressure', 'copy', 'date', 'disallow_circumpolar', 'elev', 
#'elevation', 'epoch', 'horizon', 'lat', 'lon', 'long', 'name', 
#'next_antitransit', 'next_pass', 'next_rising', 'next_setting', 
#'next_transit', 'pressure', 'previous_antitransit', 'previous_rising', 
#'previous_setting', 'previous_transit', 'radec_of', 'sidereal_time', 'temp']


#['a_dec', 'a_epoch', 'a_ra', 'alt', 'az', 'circumpolar', 'compute', 
#'copy', 'dec', 'earth_distance', 'elong', 'g_dec', 'g_ra', 'hlat', 
#'hlon', 'hlong', 'mag', 'name', 'neverup', 'parallactic_angle', 
#'phase', 'ra', 'radius', 'rise_az', 'rise_time', 'set_az', 'set_time', 
#'size', 'sun_distance', 'transit_alt', 'transit_time', 'writedb']
  observer = {}
  add(observer,loc,['name','date'],str)
  add(observer,loc,['lat','lon'],rtd)

  bodydata = {}
  add(bodydata,body,['name','neverup','circumpolar','rise_time','transit_time','set_time'],str)
  add(bodydata,body,['alt','az','ra','dec','elong','radius','a_ra','a_dec','g_ra','g_dec','hlon','hlat','libration_lat','libration_long','colong','subsolar_lat','cmlI','cmlII'],rtd)
  add(bodydata,body,['mag','phase','sun_distance','earth_distance','size','x','y','z','moon_phase','earth_tilt','sun_tilt','earth_visible','sun_visible'],float)
  if cons:
    bodydata['constellation_abbr'] = cons[0]  
    bodydata['constellation'] = cons[1]  

  result = {'observer': observer, 'body': bodydata}
  return jsonify(result)


def add(dict, obj, attrlist, func):
  for attr in attrlist:
    if (hasattr(obj,attr)): dict[attr] = func(getattr(obj,attr))

def rtd(radians):
  return 180*float(radians)/math.pi

def errors(status, detail):
  return jsonify({'errors': [{'status': status, 'detail': detail}] })


if __name__ == '__main__':
  app.run(debug=True)

