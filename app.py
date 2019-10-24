from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)



app.config['SECRET_KEY'] = 'secret key'    
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'hello123'
app.config['MYSQL_DB'] = 'cis'

mysql = MySQL(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        user = cursor.fetchone()
        cursor.execute('SELECT name FROM users WHERE username = %s AND password = %s',(username,password))

        # If account exists in accounts table in out database
        if user:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            #session['id'] = user['id']
            session['username'] = user['username']
            session['name']=user['name']

            # Redirect to home page

            if user['type']=='admin':
                return redirect(url_for('home'))
            else:
                return redirect(url_for('memberhome'))

        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

@app.route('/login/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html',  name = session['name'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/login/memberhome')
def memberhome():
    if 'loggedin' in session:
        return render_template('member.html',  name = session['name'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/login/register', methods=['GET', 'POST'])
def register():
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname']
        uname = request.form['username']
        password = request.form['password']
        email = request.form['email']
        typ = request.form['type']
                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (uname, password))
        user = cursor.fetchone()
        #If account exists show error and validation checks
        if user:
            msg = 'Account already exists!'
          
        #elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):


            #msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', uname):

            msg = 'Username must contain only characters and numbers!'
        elif not uname or not password or not email:

            msg = 'Please fill out the form!'
        else:

            created_by = session['username']
            cursor.execute('INSERT INTO users (name,username,password,email,created_by,type) VALUES (%s,%s, %s, %s,%s,%s)', (fullname,uname, password, email,created_by,typ))
            mysql.connection.commit()
            msg = 'You have successfully registered!'


            # Account doesnt exists and the form data is valid, now insert new account into accounts tabl
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/login/home/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/login/home/criminaldetails')
def criDetails():
    return render_template('crim_reg.html')


if __name__=='__main__':
    app.run(debug = True) #debug = true makes sure that we dont have to reload the server everytime we make changes to the code. 
    #Just refresh the localhost:5000 see the changes made