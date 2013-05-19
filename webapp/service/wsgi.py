
from bottle import Bottle, route, abort, run, request, response, error, static_file

application = app = Bottle()


@app.route('')
@app.route("/")
def index():
    return static_file('index.html', root=os.path.dirname(__file__))

@app.route("/nls")
def parse_nls():
    """Parse NLS input"""
    
    query = request.query['query'] or False
    if query is False:
        abort(500, "Missing query parameter")
    
    context = request.query.get('context', parser.Context.any)
    try:
        context = int(context)
    except ValueError:
        context = parser.Context.any

    response.add_header('Access-Control-Allow-Origin', '*')

    return parser.parse(query, context)

@app.error(404)
def error404(error):
    return "Method not available"

if __name__ == '__main__':
    run(app, host='localhost', port=8000, reloader=True)


