from flask import Flask, render_template, request, redirect, url_for, session

from connection import mysql
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