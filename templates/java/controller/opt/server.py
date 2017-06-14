from flask import Flask, jsonify, request, abort, make_response
from subprocess import STDOUT, check_output
from shutil import copyfile
import subprocess
import os

os.chdir('/home/user/test')

app = Flask(__name__)

@app.route('/%s/test' % os.environ['SECRET'], methods=['GET'])
def test():   
    output = ""
    error = ""
    # BUILD1: javac Program.java
    build1 = ['javac', 'Program.java']
    # BUILD2:	javac -cp .:junit.jar ProgramTest.java
    build2 = ['javac', '-cp', '.:junit.jar', 'ProgramTest.java'] 
    # TEST:	java -cp .:junit.jar:hamcrest.jar org.junit.runner.JUnitCore ProgramTest
    test = ['java', '-cp', '.:junit.jar:hamcrest.jar', 'org.junit.runner.JUnitCore', 'ProgramTest'] 
    try:
        copyfile('/opt/Solution.java', '/home/user/test/Program.java')
        output = subprocess.check_output(build1, stderr=subprocess.STDOUT).decode("utf-8")
        output = output + subprocess.check_output(build2, stderr=subprocess.STDOUT).decode("utf-8")
    except subprocess.CalledProcessError as exc:
        abort(500, "Error while building")
    except Exception as e:
        abort(500, str(e))
    try:
        output = subprocess.check_output(test, stderr=subprocess.STDOUT).decode("utf-8")
        if not "FAILURES!!!" in output:
            return make_response('OK', 200)
        abort(500, output)
    except subprocess.CalledProcessError as exc:
            output = exc.output.decode("utf-8")
            lines = output.splitlines()
            output = "Test(s) failed: \n"
            for line in lines:
                if len(line)>0:
                    if line[0].isdigit():
                        output = output + line + "\n"		
            abort(500, output)


@app.route('/' + os.environ['SECRET'], methods=['POST'])
def solution_check():
    output = ""
    error = ""
    # BUILD1: javac Program.java
    build1 = ['javac', 'Program.java']
    # BUILD2:	javac -cp .:junit.jar ProgramTest.java
    build2 = ['javac', '-cp', '.:junit.jar', 'ProgramTest.java'] 
    # TEST:	java -cp .:junit.jar:hamcrest.jar org.junit.runner.JUnitCore ProgramTest
    test = ['java', '-cp', '.:junit.jar:hamcrest.jar', 'org.junit.runner.JUnitCore', 'ProgramTest'] 
    try:
        copyfile('/home/user/solvable/Program.java', '/home/user/test/Program.java')
        output = subprocess.check_output(build1, stderr=subprocess.STDOUT).decode("utf-8")
        output = output + subprocess.check_output(build2, stderr=subprocess.STDOUT).decode("utf-8")
    except subprocess.CalledProcessError as exc:
        return jsonify(solved=False, message="Error(s) in your code! Build failed.")
    except Exception as e:
        return jsonify(solved=False, message=str(e))
    try:
        output = subprocess.check_output(test, stderr=subprocess.STDOUT).decode("utf-8")
        if not "FAILURES!!!" in output:
            return jsonify(solved=True)
        return jsonify(solved=False, message=output)
    except subprocess.CalledProcessError as exc:
            output = exc.output.decode("utf-8")
            lines = output.splitlines()
            output = "Test(s) failed: \n"
            for line in lines:
                if len(line)>0:
                    if line[0].isdigit():
                        output = output + line + "\n"		
            return jsonify(solved=False, message=output)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=False)
