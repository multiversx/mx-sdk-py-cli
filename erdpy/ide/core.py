import bottle
from bottle import run, template, static_file, request
from pathlib import Path
from erdpy.projects import get_projects_in_workspace
from erdpy.ide.view_models import SmartContractViewModel
from erdpy.ide.bottle_plugins import EnableCors

app = bottle.Bottle()
app.install(EnableCors())
global_workspace = "./examples/contracts"


@app.route("/")
def index():
    return template("dashboard.html")


@app.route("/workspace/contracts")
def workspace_contracts():
    projects = get_projects_in_workspace(global_workspace)
    models = [SmartContractViewModel(project).__dict__ for project in projects]
    return dict(data=models)


def load_workspace_contracts():
    pass


@app.post("/contracts/deploy")
def contracts_deploy():
    try:
        data = request.json
        print(data)
    except Exception:
        raise ValueError


@app.route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=_get_ide_folder("static"))


def run_ide(workspace):
    global global_workspace
    global_workspace = workspace
    run(app, host="localhost", port=8081, debug=True)


def _get_ide_folder(subfolder):
    return Path(__file__).parent.joinpath(subfolder)


bottle.TEMPLATE_PATH.append(_get_ide_folder("views"))
