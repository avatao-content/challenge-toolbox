from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)


@app.route('/')
def main():	
	return render_template('index.html')

@app.route('/admin', methods=['POST', 'GET'])
def admin():
	if request.method == 'POST':		
		try:
			if request.form['username'] == 'admin' and request.form['password'] == 'admin':
				return render_template('admin.html')
			else:
				return render_template('login.html', error='Invalid username or password - Try to login with admin/admin!')
		except:
			return render_template('login.html', error='Invalid username or password - Try to login with admin/admin!')
	else:
		return render_template('login.html')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=False)
