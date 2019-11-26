from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

import face_recognizer









from flask_pymongo import PyMongo
app = Flask(__name__)


app.config['MONGO_URI']='mongodb://localhost/cis'
mongo = PyMongo(app)

app.config['SECRET_KEY'] = 'secret key'    
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'hello123'
app.config['MYSQL_DB'] = 'cis'

mysql = MySQL(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
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
            session['type']=user['type']

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
        return render_template('home.html', name=session['name'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/login/memberhome')

def memberhome():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('member.html', name=session['name'])
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
   session.pop('name',None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/login/home/criminaldetails',methods=['GET', 'POST'])
def criminalDetails():
    msg = ''

    if request.method == 'POST' and 'cri_id' in request.form and 'phno' in request.form  :
        # Create variables for easy access
        fname = request.form['firstname']
        lname = request.form['lastname']
        phno = request.form['phno']
        cri_id = request.form['cri_id']
        cri_sex = request.form['gender']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM criminal WHERE cri_id = %s and cri_phno = %s', (cri_id,phno))
        criminal1 = cursor.fetchone()
        #If account exists show error and validation checks
        if criminal1:
            msg = 'Offender already exists!'
          
        #elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):


            #msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', cri_id):

            msg = 'Username must contain only characters and numbers!'
        elif not cri_id or not phno :

            msg = 'Please fill out the form!'
        else:

            created_by = session['username']
            
            cursor.execute("""INSERT INTO criminal (cri_fname,cri_lname,cri_sex,cri_phno,cri_id,created_by) VALUES (%s,%s,%s,%s,%s,%s)""", (fname,lname,cri_sex,phno,cri_id,created_by))
            mysql.connection.commit()
            session['criminal']=cri_id
            msg = 'You have successfully uploaded!'
            if 'profile_image' in request.files:

                profile_image =request.files['profile_image']
                mongo.save_file(profile_image.filename, profile_image)
                mongo.db.criminal.insert({'cri_id':cri_id,'profile_image_name':profile_image.filename})
                return redirect(url_for('crimeDetails'))
            else:
                msg='Image not uploaded'
        
            
            


            # Account doesnt exists and the form data is valid, now insert new account into accounts tabl
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)

    return render_template('crim_reg.html',msg=msg)


@app.route('/login/home/crimedetails',methods=['GET', 'POST'])
def crimeDetails():
    msg = ''

    if request.method == 'POST' and 'fir_id' in request.form :
        # Create variables for easy access
        desc = request.form['desc']
        place = request.form['place']
        c_time = request.form['c_time']
        fir_id = request.form['fir_id']
        c_type = request.form['c_type']
        c_id = session['criminal']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        if not re.match(r'[A-Za-z0-9]+', fir_id):

            msg = 'Invalid fir ID'
        elif not fir_id or not place :

            msg = 'Please fill out the form!'
        else:

            
            cursor.execute("""INSERT INTO crime (crime_desc,crime_place,crime_time,fir_id,c_id,c_type) VALUES (%s,%s,%s,%s,%s,%s)""", (desc,place,c_time,fir_id,c_id,c_type))
            mysql.connection.commit()
            msg = 'You have successfully uploaded!'
            session['fir']=fir_id
            return redirect(url_for('dependentDetails'))


            # Account doesnt exists and the form data is valid, now insert new account into accounts tabl
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)

    return render_template('crime.html',msg=msg)

@app.route('/login/home/dependentdetails',methods=['GET', 'POST'])
def dependentDetails():
    msg = ''

    if request.method == 'POST' and 'phno' in request.form :
        # Create variables for easy access
        d_fname = request.form['fname']
        d_lname = request.form['lname']
        relation = request.form['relation']
        d_phno = request.form['phno']
        d_address = request.form['address']
        d_sex = request.form['gender']
        c_id = session['criminal']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
       
        if not d_phno or not d_address  :

            msg = 'Please fill out the form!'
        else:

            
            cursor.execute("""INSERT INTO dependents (d_fname,d_lname,relation,d_phno,d_address,d_sex,c_id) VALUES (%s,%s,%s,%s,%s,%s,%s)""", (d_fname,d_lname,relation,d_phno,d_address,d_sex,c_id))
            mysql.connection.commit()
            msg = 'You have successfully uploaded!'


            # Account doesnt exists and the form data is valid, now insert new account into accounts tabl
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)

    return render_template('dependent.html',msg=msg)


@app.route('/login/home/punishmentdetails',methods=['GET', 'POST'])
def punishmentDetails():
    msg = ''

    if request.method == 'POST' and 'p_type' in request.form :
        # Create variables for easy access
        desc = request.form['desc']
        p_type = request.form['p_type']
        if p_type=='prison':
            pr_address = request.form['pr_address']
            pr_time = request.form['pr_time']
        else:
            pr_address = None
            pr_time = None

        
        c_id = session['criminal']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        
        if not p_type or not desc :

            msg = 'Please fill out the form! '
        else:

            
            cursor.execute("""INSERT INTO punishment (p_desc,prison_address,prison_time,p_type,c_id) VALUES (%s,%s,%s,%s,%s)""", (desc,pr_address,pr_time,p_type,c_id))
            mysql.connection.commit()
            msg = 'You have successfully uploaded!'
            
            return redirect(url_for('home'))



       

    return render_template('punishment.html',msg=msg)


@app.route('/login/home/update', methods=['GET','PUT'])
def update():
    msg = ''
    
    if request.method == 'PUT':
     
        c_id = request.form['c_id']
     
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM criminal WHERE c_id = %s ', (c_id))
     
        criminal1 = cursor.fetchone()

  
        if criminal1:
            phno = request.form['phno']
            if not phno:
                msg="Please fill in phone number!"
            else:
                cursor.execute('UPDATE criminal SET cri_phno = %s WHERE cri_id = %s',(phno,c_id))
                mysql.connection.commit()
                msg="You have succesfully updated!"
           


        else:
           
            msg = 'Incorrect criminal ID'
 
    return render_template('updatecriminal.html', msg=msg)


@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)

@app.route('/profile')
def profile():
    
    cri_id = session['criminal']
    print(cri_id)
    user = mongo.db.criminal.find_one_or_404({'cri_id': cri_id}) 
    if session['type']=='admin':
        return f''' 
        <h1>{cri_id}</h1>
        <img src = "{url_for('file',filename=user['profile_image_name'])}">
        <ul>
        li><a href="http://localhost:5000/login/home">Go back home</a></li>
        </ul>'''
    else:
        return f''' 
        <h1>{cri_id}</h1>
        <img src = "{url_for('file',filename=user['profile_image_name'])}">
        <ul>
        li><a href="http://localhost:5000/login/memberhome">Go back home</a></li>
        </ul>'''

    


@app.route('/login/home/viewRecord',methods=['GET'])
def viewRecord():
    msg = ''
    searchword = request.args.get('crim_id', '')
    print(searchword)
    session['criminal'] = searchword
    if request.method=='GET' and searchword :
        cri_id = searchword
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM criminal WHERE cri_id LIKE %s', [cri_id])
      
        criminal1 = cursor.fetchone()
        cursor.execute('SELECT * FROM crime WHERE c_id LIKE %s', [cri_id])
        crime = cursor.fetchone()
        cursor.execute('SELECT * FROM punishment WHERE c_id LIKE %s',[cri_id])
        punishment= cursor.fetchone()
        cursor.execute('SELECT * FROM dependents WHERE c_id LIKE %s',[cri_id])
        dependent = cursor.fetchall()
        for row in dependent:
            print(row)
        if criminal1 and crime and punishment:
            return render_template('view.html',value=criminal1,value2=crime,value3=punishment,value4 = dependent)


        
        
        else:
            msg = "This ID does not exist"
            if session['type']=='admin':
                return render_template('notexist.html')
            else:
                return render_template('notexistmember.html')
    else:
        print('no')
        msg:'This record does not exist'
        return render_template('viewRecords.html',msg=msg)

        

    

    

@app.route('/login/home/viewAll', methods=['GET'])
def viewAll():

    if request.method == 'GET':


        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM criminal')
        criminal1 = cursor.fetchall()
        if criminal1:
            return render_template('viewAll.html',value=criminal1)
        else:
            msg = 'No criminal data in database'
            if session['type']=='admin':
                return render_template('home.html',msg=msg)
            else:
                return render_template('member.html',msg=msg)
            


@app.route('/login/home/facerec')
def facerec():
    identity = face_recognizer.face()
    print(identity)
    cri_id = identity
    if identity==None:
        if session['type']=='admin':
            return render_template('home.html',msg='No criminal record found')
        else:
            return render_template('member.html',msg='No criminal record found')
            
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM criminal WHERE cri_id = %s', [cri_id])
    criminal1 = cursor.fetchone()
    
    cursor.execute('SELECT * FROM crime WHERE c_id = %s', [cri_id])
    crime = cursor.fetchone()
    cursor.execute('SELECT * FROM punishment WHERE c_id =%s',[cri_id])
    punishment= cursor.fetchone()
    cursor.execute('SELECT * FROM dependents WHERE c_id LIKE %s',[cri_id])
    dependent = cursor.fetchall()
    if criminal1 and crime and punishment:
        session['criminal'] = criminal1['cri_id']
        return render_template('view.html',value=criminal1,value2=crime,value3=punishment,value4 = dependent)
    
    else:
        if session['type']=='admin':
            return render_template('notexist.html')
        else:
            return render_template('notexistmember.html')


           



if __name__=='__main__':
    app.run(debug = True) #debug = true makes sure that we dont have to reload the server everytime we make changes to the code. 
    #Just refresh the localhost:5000 see the changes made
