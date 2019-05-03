import paramiko
import flask


def check(request: flask.Request):
    if request.method != 'POST':
        return flask.abort(400)

    data = request.get_json()
    solution = data.get("solution", "")

    with paramiko.SSHClient() as ssh_client:
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(data["host"], username=data.get("username", "controller"), password=data["password"])

        stdin, stdout, stderr = ssh_client.exec_command("uname -a")

        return flask.jsonify({
            "solved": True,
            "message": stdout.read(),  # optional
            "penalty": 0.0,  # optional
        })


def main(request: flask.Request):
    try:
        return check(request)

    except Exception as e:
        return flask.jsonify({"solved": False, "message": str(e)})
