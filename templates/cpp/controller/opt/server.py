import html
from flask import Flask, abort, make_response, jsonify
import os
import pickle
from shutil import copyfile
import socket


CONNECT_TO = ('localhost', 7777)
SOLVABLE_SOLUTION = '/solvable/app/geomean.cpp'

app = Flask(__name__)


@app.errorhandler(500)
def _handle_exception(error):
    return error, 500


def recvall(sock, buffer_size=4096):
    data = []
    while True:
        part = sock.recv(buffer_size)
        data.append(part)
        if len(part) < buffer_size:
            break
    return b''.join(data)


def _run_solution_check():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(10)
        sock.connect(CONNECT_TO)
        received = recvall(sock)
        message = pickle.loads(received)
        return message['success'], message['output']


@app.route('/' + os.environ['SECRET'], methods=['POST'])
def solution_check():
    """
    This function is invoked when the user submits a solution and
    returns a JSON object whether their solution was correct.

    Please adjust if necessary.
    """
    try:
        success, output = _run_solution_check()
        result = output.replace("\u2018", "'").replace("\u2019", "'")
        result = html.escape(result)
        return jsonify(solved=(success == 1), message=result)
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
        # Move working solution `solution.cpp` to solvable
        copyfile('/usr/share/solution.cpp', SOLVABLE_SOLUTION)
    except Exception as e:
        abort(500, 'Could not copy solution file to solvable. Details: {}'.format(e))

    try:
        success, output = _run_solution_check()
    except Exception as e:
        abort(500, 'Could not run unit tests: {}'.format(e))
    else:
        if not success:
            abort(500, output)

    return make_response('OK', 200)

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=int(os.environ['CONTROLLER_PORT']),
            debug=(os.environ['DEBUG'].lower() == 'true'))
