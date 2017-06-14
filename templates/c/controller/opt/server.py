import os
import socket
import struct
from flask import Flask, abort, make_response, jsonify
from shutil import copyfile


CONNECT_TO = ('localhost', 7777)
app = Flask(__name__)


@app.errorhandler(500)
def _handle_exception(error):
    return error, 500


def _run_solution_check():

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect(CONNECT_TO)
    success = struct.unpack('h', sock.recv(2))[0]
    size = struct.unpack('I', sock.recv(4))[0]
    output = sock.recv(size, socket.MSG_WAITALL).decode('utf-8')
    sock.close()

    return success, output


@app.route('/' + os.environ['SECRET'], methods=['POST'])
def solution_check():
    """
    This function is invoked when the user submits a solution and
    returns a JSON object whether his solution was correct.

    Please adjust if necessary.
    """
    try:
        success, output = _run_solution_check()
        return jsonify(solved=(success == 1), message=output)
    except Exception as e:
        return jsonify(solved=False, message=str(e))


@app.route('/%s/test' % os.environ['SECRET'], methods=['GET'])
def test():
    """
    This function is invoked automatically upon deployment to
    test if the challenge is working properly.

    Send HTTP 200 on success and HTTP 500 on failure. Use logging
    for error and information reporting.

    Please adjust if necessary.
    """

    try:
        # Move working solution `solution.c` to /solvable/app/app.c
        copyfile('/usr/share/solution.c', '/solvable/app/app.c')
    except Exception as e:
        abort(500, 'Could not copy solution file to solvable. Details: %s' % e)

    try:
        success, output = _run_solution_check()
    except Exception as e:
        abort(500, 'Could not run unit tests: %s' % e)
    else:
        if not success:
            abort(500, output)

    return make_response('OK', 200)

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=int(os.environ['CONTROLLER_PORT']),
            debug=(os.environ['DEBUG'].lower() == 'true'))
