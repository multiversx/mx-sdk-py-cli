import bottle
from bottle import route, post, run, template, static_file, request
from pathlib import Path

app = bottle.Bottle()


@app.route("/")
def index():
    return template("dashboard.html")


@app.post("/contracts/deploy")
def contracts_deploy():
    try:
        data = request.json
        print(data)
    except:
        raise ValueError


@app.route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=_get_ide_folder("static"))


def run_ide(workspace):
    run(app, host="localhost", port=8081, debug=True)


def _get_ide_folder(subfolder):
    return Path(__file__).parent.joinpath(subfolder)


bottle.TEMPLATE_PATH.append(_get_ide_folder("views"))
