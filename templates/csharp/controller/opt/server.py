from flask import Flask, jsonify, request, abort, make_response
from subprocess import STDOUT, check_output
from shutil import copyfile
import subprocess
import os
import cgi

os.chdir('/nunit/bin')

app = Flask(__name__)

@app.route('/%s/test' % os.environ['SECRET'], methods=['GET'])
def test():   
    BUILD = ['xbuild', '/home/user/App/App.sln']
    TEST = ['mono', 'nunit3-console.exe', '/home/user/App/Test/Test.csproj']
    try:
        copyfile('/home/user/solvable/Program.cs', '/home/user/App/App/Program.cs')
        output = subprocess.check_output(BUILD, stderr=subprocess.STDOUT).decode("utf-8")
    except subprocess.CalledProcessError as exc:
        output = exc.output.decode("utf-8").replace("/home/user/App/", "").split("->\n\n")[1].lstrip("\t").lstrip(":").lstrip()
        abort(500, output)
    try:
        subprocess.call(TEST)
        with open('/nunit/bin/TestResult.xml', 'r') as f:
            for line in f.read().splitlines():
                if '<test-case' in line:
                    if line.split('"')[9] == "Failed":
                        error = error + line.split('"')[3] + " FAILED\n"
        if error == "":
            return make_response('OK', 200)
        else:
            abort(500, error)                 
    except Exception as e:
        abort(500, e)


@app.route('/' + os.environ['SECRET'], methods=['POST'])
def solution_check():
    BUILD = ['xbuild', '/home/user/App/App.sln']
    TEST = ['mono', 'nunit3-console.exe', '/home/user/App/Test/Test.csproj']
    try:
        copyfile('/home/user/solvable/Program.cs', '/home/user/App/App/Program.cs')
        output = subprocess.check_output(BUILD, stderr=subprocess.STDOUT).decode("utf-8")
    except subprocess.CalledProcessError as exc:
        output = exc.output.decode("utf-8").replace("/home/user/App/", "").split("->\n\n")[1].lstrip("\t").lstrip(":").lstrip()
        error = "<pre><code>" + cgi.escape(output) + "</code></pre>"
        return jsonify(solved=False, message=error)
    try:
        subprocess.call(TEST)
        error = ""
        # Parsing output
        with open('/nunit/bin/TestResult.xml', 'r') as f:
            for line in f.read().splitlines():
                if '<test-case' in line:
                    if line.split('"')[9] == "Failed":
                        error = error + line.split('"')[3] + " FAILED\n"
        if error == "":
            return jsonify(solved=True)
        return jsonify(solved=False, message=error)
                  
    except Exception as e:
        return jsonify(solved=False, message=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ['CONTROLLER_PORT']),
            debug=(os.environ['DEBUG'].lower() == 'true'))
