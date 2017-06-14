from flask import Flask, jsonify, request
import os

app = Flask(__name__)

@app.route('/' + os.environ['SECRET'], methods=['POST'])
def solution_check():
    try:
        submitted_solution = request.json['solution']
        if submitted_solution == "doctor@177.143.65.198":
                 return jsonify(solved=True)
        else:
                 return jsonify(solved=False)
    except:
        return jsonify(solved=False, message="Exception!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=False)
