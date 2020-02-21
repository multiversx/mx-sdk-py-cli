import bottle
from bottle import route, post, run, template, static_file, request
from pathlib import Path


@route("/")
def index():
    return template("dashboard.html")

@post("/contracts/deploy")
def contracts_deploy():
    try:
        data = request.json
        print(data)
    except:
        raise ValueError

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=_get_ide_folder("static"))


def run_ide(project):
    bottle.TEMPLATE_PATH.append(_get_ide_folder("views"))
    run(host="localhost", port=9876)


def _get_ide_folder(subfolder):
    return Path(__file__).parent.joinpath(subfolder)
