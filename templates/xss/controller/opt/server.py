import os
import subprocess
from flask import Flask, abort, make_response, jsonify
import yaml

app = Flask(__name__)

TEST_ARGS = ['/opt/phantomjs', '/opt/solution.js']


@app.errorhandler(500)
def _handle_exception(error):
    return error, 500


@app.route('/' + os.environ['SECRET'], methods=['POST'])
def solution_check():
    """
    This function is invoked every time a user solution is submitted. 

    Please adjust if necessary.
    """
    try:
        #runs the solution.js
        output = subprocess.check_output(TEST_ARGS, stderr=subprocess.STDOUT, universal_newlines=True, timeout=3)

    except OSError as e:
        return jsonify(solved=False, message='File is not accessible: %s' % ' '.join(TEST_ARGS))

    except subprocess.CalledProcessError:
        return jsonify(solved=False, message='Failed to invoke %s' % ' '.join(TEST_ARGS))

    except Exception as e:
        if open('/opt/result.txt').read().find('XSS FOUND') == -1:
            return jsonify(solved=False, message='No injection took place. Make sure your payload doesn\'t contain external links!')
        return jsonify(solved=True, message='successfully injected xss')

    if open('/opt/result.txt').read().find('XSS FOUND') == -1:
        return jsonify(solved=False, message='No injection took place. Make sure your payload doesn\'t contain external links!')

    return jsonify(solved=True, message='successfully injected xss')
    

@app.route('/%s/test' % os.environ['SECRET'], methods=['GET'])
def test():
    """
    This function is invoked automatically upon deployment to
    test if the challenge is working properly.

    Send HTTP 200 on success and HTTP 500 on failure. Use logging
    for error and information reporting.

    Please adjust if necessary.
    """

    #injects the payload into the site
    inject_args=['curl', '--data', '"name=test&message=%3Csvg%2Fonload%3D%22alert(1)%22&btnSign=Sign+Guestbook"', 
    'http://localhost:8888/action.php']
    subprocess.check_output(inject_args,stderr=subprocess.STDOUT,universal_newlines=True)    

    try:
        output = subprocess.check_output(TEST_ARGS, stderr=subprocess.STDOUT, universal_newlines=True)

    except OSError as e:
        abort(500, 'File is not accessible: %s' % ' '.join(TEST_ARGS))

    except subprocess.CalledProcessError:
        abort(500, 'Failed to invoke %s' % ' '.join(TEST_ARGS))

    except Exception as e:
        abort(500, e)

    else:
        if open('/opt/result.txt').read().find('XSS FOUND') == -1:
            abort(500, 'No injection took place.')

    return make_response('OK', 200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ['CONTROLLER_PORT']),
            debug=(os.environ['DEBUG'].lower() == 'true'))
