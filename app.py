import os
import extractMetaData
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, json, session
from flask.ext.mysql import MySQL
from werkzeug import secure_filename, FileStorage, generate_password_hash, check_password_hash
#from werkzeug.datastructures import FileStorage

mysql = MySQL()
app = Flask(__name__)

app.secret_key = 'hidden hahahaha'

app.config['MYSQL_DATABASE_USER'] ='root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'Media'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

''' use to communicate with MySQL
@app.route("/Authenticate")
def Authenticate():
    username = request.args.get('UserName')
    password = request.args.get('Password')
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from User where Username='" + username + "' and Password='" + password + "'")
    data = cursor.fetchone()
    if data is None:
     return "Username or Password is wrong"
    else:
     return "Logged in successfully"
'''

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# defines upload path and allowed file types. May not need at this point
'''
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['jpg', 'jpeg', 'png'])

def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']
'''
# main page
@app.route("/")
def index():
	return render_template("index.html")
	
@app.route("/showSignUp")
def showSignUp():
	return render_template('signup.html')
	
@app.route("/signUp",methods=['POST','GET'])
def signUp():
	try:
	
		_name = request.form['inputName']
		_email = request.form['inputEmail']
		_password = request.form['inputPassword']
	
	
	
		if _name and _email and _password:
	
			conn = mysql.connect()
			cursor = conn.cursor()
			_hashed_password = generate_password_hash(_password)
			cursor.callproc('sp_createUser1',(_name,_email,_hashed_password))
			data = cursor.fetchall()
		
			if len(data) is 0:
				conn.commit()
				return json.dumps({'message':'User created successfully !'})
			else:
				return json.dumps({'error':str(data[0])})
		else:
			return json.dumps({'html':'<span>Enter the required fields</span>'})
			
	except Exception as e:
		return json.dumps({'error':str(e)})
	finally:
		cursor.close()
		conn.close()
		
			
			
			
#		return json.dumps({'html':'<span>All fields good !!</span>'})
#	else:
#		return json.dumps({'html':'<span>Enter the required fields</span>'})

@app.route("/showSignin")
def showSignin():
	if session.get('user'):
		return render_template('userHome.html')
	else:
		return render_template('signin.html')
	
@app.route("/validateLogin",methods=['POST'])
def validateLogin():
	try:
		_username = request.form['inputEmail']
		_password = request.form['inputPassword']
		
		
		con = mysql.connect()
		cursor = con.cursor()
		cursor.callproc('sp_validateLogin',(_username,))
		data = cursor.fetchall()
		
		if len(data) > 0:
			if check_password_hash(str(data[0][3]),_password):
				session['user'] = data[0][0]
				return redirect('/userHome')
			else:
				return render_template('error.html',error = 'Wrong Email or Password.')
		else:
			return render_template('error.html',error =  'Wrong Email or Password.')
		
	except Exception as e:
		return render_template('error.html',error = str(e))
	finally:
		cursor.close()
		con.close()
		
@app.route("/userHome")
def userHome():
	if session.get('user'):
		return render_template("userHome.html")
	else:
		return render_template('error.html',error = 'Unauthorized Access')
		
@app.route("/logout")
def logout():
	session.pop('user',None)
	return redirect('/')
		
@app.route("/Submit")
def submit():
	return render_template("upload.html")


@app.route("/upload", methods=['POST'])
def upload():
	target = os.path.join(APP_ROOT, 'images/')
	print(target)
	
	if not os.path.isdir(target):
		os.mkdir(target)
	
	
		
	for file in request.files.getlist("file"):
		print(file)
		filename = file.filename
		destination = "/".join([target, filename])
		print(destination)
		file.save(destination)

	return render_template("complete.html")	

@app.route("/Finish")
def finish():
	
	for filename in os.listdir("/images"):
		img = open(os.path.join("/images", filename), "r")
		out = img.txt
		extractMetaData.getMetaData(img, out)
		
	
	return render_template("finished.html")

# Figure out how to use metadata module to parse file upload
#extractMetaData.getMetaData(storage.stream.read(), out.txt)	





	
if __name__ == "__main__":
	app.run()
