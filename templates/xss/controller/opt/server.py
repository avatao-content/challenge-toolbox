import os
import subprocess
from flask import Flask, abort, make_response, jsonify, request
from urllib.parse import urlparse

app = Flask(__name__)


@app.errorhandler(500)
def _handle_exception(error):
    return error, 500


@app.route('/' + os.environ['SECRET'], methods=['POST'])
def solution_check():
    # If enable_flag_input == True in config.yml:
    #     This URL is replaced with the submitted one
    # Please use relative URL here:
    URL = '/guestbook.php'

    try:
        path = '/' + urlparse(request.json['solution']).path.lstrip('/')
        if not path == '/':
            URL = path + '?' + urlparse(request.json['solution']).query.rstrip('?')
        TEST_ARGS = ['/opt/phantomjs25', '/opt/check.js', URL]
        output = subprocess.check_output(TEST_ARGS, stderr=subprocess.STDOUT, universal_newlines=True, timeout=3)
    except OSError as e:
        return jsonify(solved=False, message='File is not accessible: %s' % ' '.join(TEST_ARGS))

    except subprocess.CalledProcessError:
        return jsonify(solved=False, message='Failed to invoke %s' % ' '.join(TEST_ARGS))

    except Exception as e:
        pass

    if 'XSS FOUND' in open('/opt/result.txt').read():
        return jsonify(solved=True, message='Successfully injected xss!')

    return jsonify(solved=False, message='No injection took place. Make sure your payload doesn\'t contain external URLs!')
    

@app.route('/%s/test' % os.environ['SECRET'], methods=['GET'])
def test():
    """
    This function is invoked automatically upon deployment to
    test if the challenge is working properly.

    Send HTTP 200 on success and HTTP 500 on failure. Use logging
    for error and information reporting.

    Please adjust if necessary.
    """

    URL = '/guestbook.php'

    try:
        # IF REFLECTED:
        #    Change URL here
        URL = URL # Solution URL
        # IF STORED:
        #     Inject payload here
        INJECT_ARGS=['curl', \
                 '--data', \
                 'name=test&message=%3Csvg%2Fonload%3D%22alert(1)%22&btnSign=Sign+Guestbook', \
                 'http://localhost:8888/guestbook.php']
        subprocess.check_output(INJECT_ARGS, stderr=subprocess.STDOUT, universal_newlines=True)
	# Comment the lines above if XSS is reflected
        TEST_ARGS = ['/opt/phantomjs25', '/opt/check.js', URL]
        output = subprocess.check_output(TEST_ARGS, stderr=subprocess.STDOUT, universal_newlines=True, timeout=3)
    except OSError as e:
        abort(500, 'File is not accessible: %s' % ' '.join(test_static))

    except subprocess.CalledProcessError:
        abort(500, 'Failed to invoke %s' % ' '.join(test_static))

    except Exception as e:
        abort(500, e)

    if 'XSS FOUND' in open('/opt/result.txt').read():
        return make_response('OK', 200)

    abort(500, 'No injection took place.')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ['CONTROLLER_PORT']),
            debug=(os.environ['DEBUG'].lower() == 'true'))
