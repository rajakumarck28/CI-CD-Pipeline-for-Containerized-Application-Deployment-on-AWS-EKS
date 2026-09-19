from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
import bcrypt
import os

app = Flask(__name__)

# =====================================
# MYSQL CONFIGURATION FOR DOCKER
# =====================================

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'mysql-db')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'root123')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'authapp')

mysql = MySQL(app)

# =====================================
# HOME PAGE
# =====================================

@app.route('/')
def home():
    return render_template('login.html')

# =====================================
# REGISTER PAGE
# =====================================

@app.route('/register')
def register_page():
    return render_template('register.html')

# =====================================
# REGISTER USER
# =====================================

@app.route('/register-user', methods=['POST'])
def register_user():

    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    # HASH PASSWORD
    hashed_password = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    cur = mysql.connection.cursor()

    sql = '''
    INSERT INTO users(username, email, password)
    VALUES(%s, %s, %s)
    '''

    try:
        cur.execute(sql, (username, email, hashed_password))
        mysql.connection.commit()

        return "Registration Successful"

    except Exception as e:
        return f"Registration Failed: {str(e)}"

    finally:
        cur.close()

# =====================================
# LOGIN USER
# =====================================

@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    cur = mysql.connection.cursor()

    sql = "SELECT * FROM users WHERE username=%s"

    cur.execute(sql, (username,))

    user = cur.fetchone()

    cur.close()

    if user:

        stored_password = user[3]

        # VERIFY PASSWORD
        if bcrypt.checkpw(
            password.encode('utf-8'),
            stored_password.encode('utf-8')
        ):

            return redirect('/dashboard')

        else:
            return "Invalid Password"

    return "User Not Found"

# =====================================
# DASHBOARD
# =====================================

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# =====================================
# FORGOT PASSWORD PAGE
# =====================================

@app.route('/forgot')
def forgot_page():
    return render_template('forgot.html')

# =====================================
# RESET PASSWORD
# =====================================

@app.route('/forgot-password', methods=['POST'])
def forgot_password():

    email = request.form['email']
    new_password = request.form['newpassword']

    hashed_password = bcrypt.hashpw(
        new_password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    cur = mysql.connection.cursor()

    sql = '''
    UPDATE users
    SET password=%s
    WHERE email=%s
    '''

    try:
        cur.execute(sql, (hashed_password, email))
        mysql.connection.commit()

        if cur.rowcount > 0:
            return "Password Updated Successfully"
        else:
            return "Email Not Found"

    except Exception as e:
        return f"Password Reset Failed: {str(e)}"

    finally:
        cur.close()

# =====================================
# HEALTH CHECK
# =====================================

@app.route('/health')
def health():
    return "Application Running Successfully"

# =====================================
# RUN APPLICATION
# =====================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
