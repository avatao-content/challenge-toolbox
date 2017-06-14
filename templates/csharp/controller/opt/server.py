from flask import Flask, jsonify, request, abort, make_response
from subprocess import STDOUT, check_output
from shutil import copyfile
import subprocess
import os

os.chdir('/nunit/bin')

app = Flask(__name__)

@app.route('/%s/test' % os.environ['SECRET'], methods=['GET'])
def test():   
    output = ""
    error = ""
    build = ['xbuild', '/home/user/App/App.sln']
    test = ['mono', 'nunit3-console.exe', '/home/user/App/Test/Test.csproj']
    try:
        copyfile('/opt/Solution.cs', '/home/user/App/App/Program.cs')
        output = str(subprocess.check_output(build, stderr=subprocess.STDOUT))
        if not "0 Error(s)" in output:
            abort(500, "Error while building")
    except Exception as e:
        abort(500, "Error while building")
    try:
        subprocess.call(test)
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
    output = ""
    error = ""
    build = ['xbuild', '/home/user/App/App.sln']
    test = ['mono', 'nunit3-console.exe', '/home/user/App/Test/Test.csproj']
    try:
        copyfile('/home/user/solvable/Program.cs', '/home/user/App/App/Program.cs')
        output = str(subprocess.check_output(build, stderr=subprocess.STDOUT))
        if not "0 Error(s)" in output:
            return jsonify(solved=False, message="Error while building. \
Make sure, your code doesn't have syntax errors and you have implemented the function!")
    except Exception as e:
        return jsonify(solved=False, message="Error while building. \
Make sure, your code doesn't have syntax errors and you have implemented the function!")
    try:
        subprocess.call(test)
        with open('/nunit/bin/TestResult.xml', 'r') as f:
            for line in f.read().splitlines():
                if '<test-case' in line:
                    if line.split('"')[9] == "Failed":
                        error = error + line.split('"')[3] + " FAILED\n"
        if error == "":
            return jsonify(solved=True)
        else:
            return jsonify(solved=False, message=error)
                  
    except Exception as e:
        return jsonify(solved=False, message=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=False)
