import os
import subprocess
import yaml
from flask import Flask, abort, make_response, request, jsonify

app = Flask(__name__)

TEST_ARGS = ['python2', '/opt/solution.py']


@app.errorhandler(500)
def _handle_exception(error):
    return error, 500


def _read_static_flag():

    try:
        with open('/etc/config.yml') as f:
            config = yaml.load(f)
            return config['flag']

    except KeyError:
        abort(500, 'Missing flag from config.yml. You have to implement a dynamic flag generation in the controller.')

    except FileNotFoundError as e:
        abort(500, 'Could not find /etc/config.yml. Please make sure it is in place.')

    except Exception as e:
        abort(500, 'An error occurred while loading config.yml. Details %s' % e)


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
        output = subprocess.check_output(TEST_ARGS, stderr=subprocess.STDOUT, universal_newlines=True)
        flag = _read_static_flag()

    except OSError as e:
        abort(500, 'File is not accessible: %s' % ' '.join(TEST_ARGS))

    except subprocess.CalledProcessError:
        abort(500, 'Failed to invoke %s' % ' '.join(TEST_ARGS))

    except Exception as e:
        abort(500, e)

    else:
        if output.find(flag) == -1:
            abort(500, 'The flag in config.yml does not match output.')

    return make_response('OK', 200)


@app.route('/' + os.environ['SECRET'], methods=['POST'])
def solution_check():
    submitted_solution = request.json['solution']

    if submitted_solution != 'flag':
        return jsonify(solved=False)

    return jsonify(solved=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=False)
