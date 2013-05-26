
#from bottle import Bottle, route, abort, run, request, response, error, static_file
import bottle
import configuration
import dao
import os

application = app = bottle.Bottle()
conf = configuration.read()
static_path = os.path.join(conf['base_path'], '/static/')

@app.route('')
@app.route("/")
@app.route("/index.html")
def index():
    return bottle.static_file('index.html', root=static_path)

@app.route("/js/<filename:path>")
def js(filename):
    return bottle.static_file(filename, root=os.path.join(static_path, '/js/'))

@app.route("/css/<filename:path>")
def css(filename):
    return bottle.static_file(filename, root=os.path.join(static_path, '/css/'))

@app.route("/img/<filename:path>")
def img(filename):
    return bottle.static_file(filename, root=os.path.join(static_path, '/img/'))

@app.route("/data/hourly/<sensor:int>")
@app.route("/data/hourly/<sensor:int>/<start_date:int>")
@app.route("/data/hourly/<sensor:int>/<start_date:int>/<end_date:int>")
def hourly_data(sensor, start_date=None, end_date=None):
    return {"data": dao.RollUp.fetch('hour', sensor, start_date, end_date)}

@app.route("/data/daily/<sensor:int>")
@app.route("/data/daily/<sensor:int>/<start_date:int>")
@app.route("/data/daily/<sensor:int>/<start_date:int>/<end_date:int>")
def daily_data(sensor, start_date=None, end_date=None):
    return {"data": dao.RollUp.fetch('day', sensor, start_date, end_date)}

@app.route("/data/monthly/<sensor:int>")
@app.route("/data/monthly/<sensor:int>/<start_date:int>")
@app.route("/data/monthly/<sensor:int>/<start_date:int>/<end_date:int>")
def monthly_data(sensor, start_date=None, end_date=None):
    return {"data": dao.RollUp.fetch('month', sensor, start_date, end_date)}

@app.route("/data/sensors")
def sensors():
    return {"sensors": [(sensor[0], sensor[1]) for sensor in conf['sensors'] ]}

@app.error(404)
def error404(error):
    return "Method not available"

if __name__ == '__main__':
    bottle.run(app, host='localhost', port=8000, reloader=True)


