from flask import Flask, render_template, request, redirect, session, flash
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL
import datetime
import re
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key="keep it a secret"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    is_valid = True
    email_is_good = EMAIL_REGEX.match(request.form['email'])
    if len(request.form['fname']) < 2:
        is_valid = False
        flash("Please enter first name")
    if len(request.form['lname']) <2:
        is_valid = False
        flash("Please enter last name")
    if email_is_good is None:
        is_valid = False
        flash("Email invalid")
    mysql = connectToMySQL('login_registration')
    unique_email_query = "SELECT COUNT(*) FROM users WHERE email = (%(em)s);"
    data = {
        'em': request.form['email']
    }    
    db_response = mysql.query_db(unique_email_query, data)
    print(db_response)
    if len(db_response)> 0:
        flash('Email already exists!') 
    if len(request.form['password']) < 8:
        is_valid = False
        flash("Enter valid passsword!")
    if (request.form['confirm_pass']) != (request.form['password']):
        is_valid = False
        flash("Passwords dont match!")
    if is_valid:
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        mysql = connectToMySQL('login_registration')
        query = "INSERT INTO `login_registration`.`users` (`first_name`, `last_name`, `email`,`password` ) VALUES (%(fn)s, %(ln)s, %(em)s, %(pw)s );"
        data = {
            'fn': request.form['fname'],
            'ln': request.form['lname'],
            'em': request.form['email'],
            'pw': pw_hash
        }
        db = mysql.query_db(query, data)
        session['uid'] = db
        session['username'] =  request.form['fname']
        return redirect('/success')
    return redirect('/')

@app.route ('/login', methods=['POST'])
def login():
    email_is_good = EMAIL_REGEX.match(request.form['l_email'])
    if email_is_good is None:
        is_valid = False
        flash("Login Failed")
        return redirect('/')
    if request.form['l_email'] == "":
        flash("Login Failed")
        return redirect('/')
    mysql = connectToMySQL('login_registration')
    login_query = "SELECT * FROM users WHERE email=%(em)s;"
    login_data = {
        'em': request.form['l_email'],
    }
    login_d = mysql.query_db(login_query, login_data)
    userid = login_d[0]['users_id']
    is_valid = True
    x=bcrypt.check_password_hash(login_d[0]['password'], request.form['l_pass'])
    if x == False:
        flash("Login Failed")
        return redirect('/')
    if is_valid:
        session['uid'] = userid
        session['username'] =  login_d[0]['first_name']
        return redirect('/success')
    return redirect('/')

@app.route('/success')
def success():
    if 'username' in session:
        return render_template('success.html')
    else:
        return redirect('/')
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



if __name__ =="__main__":
    app.run(debug=True)