import traceback

import flask
import paramiko


def check(request: flask.Request):
    if request.method != 'POST':
        return flask.abort(400)

    data = request.get_json()
    # If flag input is enabled, get the user's flag.
    solution = data.get("solution", "")

    with paramiko.SSHClient() as ssh_client:
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(data["host"], username="controller", password=data["password"])

        # Run some pretty commands ...
        stdin, stdout, stderr = ssh_client.exec_command("uname -a")

        return flask.jsonify({
            "solved": True,  # set this!
            "message": stdout.read().decode('utf-8'),  # optional
            "multiplier": 1.0,  # optional [0.0-1.0]
        })


def main(request: flask.Request):
    # TODO: Validate the source of the request!
    try:
        return check(request)

    except Exception as e:
        # You probably do NOT want to print exceptions in production...
        return flask.jsonify({"solved": False, "message": traceback.format_exc()})
