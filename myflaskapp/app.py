from fileinput import filename
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, TextAreaField, validators, StringField, PasswordField
from passlib.hash import sha256_crypt
import os
import datetime
from werkzeug.utils import secure_filename
from text_summariser import generate_text_summary
from video_indexer import index_video
from functools import wraps

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 * 16 * 16
app.config["TEMPLATES_AUTO_RELOAD"] = True

# configMYSQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Manav@1512'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('Unauthorized, Please login.','danger')
            return redirect(url_for('login'))
    return wrap

class vSummaryForm(Form):
    vsubject = StringField('Subject', [validators.Length(min=1, max=50)])
    vdatee = StringField('Date(DD/MM/YYYY)', [validators.Length(min=10, max=25)])


@app.route('/v1', methods=['GET', 'POST'])
def upload_video():
    form = vSummaryForm(request.form)
    if request.method == 'POST':
        vsubject = form.vsubject.data
        vdatee = form.vdatee.data
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO vsummary (vteacher, vsubject, vdatee, path) VALUES (%s, %s, %s, %s)",
                    (session['username'], vsubject, vdatee, [filename]))
        mysql.connection.commit()
        cur.close()
        # print('upload_video filename: ' + filename)
        flash('Video successfully uploaded AND ADDED TO DB and displayed below')

    return render_template('upload.html', form=form)


@app.route('/display_track/<filename>')
def display_track(filename):
    # print('display_video filename: ' + filename)
    filename = filename[:-3] + 'vtt'
    # print(filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/display_video/<filename>')
def display_video(filename):
    # print('display_video filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


@app.route('/')
def index():
    return render_template('home.html')


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, password) VALUES (%s, %s, %s, %s)",
                    (name, email, username, password))

        mysql.connection.commit()

        cur.close()
        flash('You have been registered.Happy learning!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()

        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            data = cur.fetchone()
            password = data['password']
            userroll = data['userroll']

            if sha256_crypt.verify(password_candidate, password):
                # password matched
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                if userroll == 't':
                    session['userroll'] = True
                else:
                    session['userroll'] = False
                return redirect(url_for('dashboard'))

            else:
                error = 'Invalid Login'
                return render_template('login.html', error=error)
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
        cur.close()

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
# @is_logged_in
def dashboard():
    cur = mysql.connection.cursor()

    # Get link
    result = cur.execute("SELECT * FROM summary")
    summary = cur.fetchall()

    result1 = cur.execute("SELECT * FROM vsummary")
    vsummary = cur.fetchall()

    for i in range(len(vsummary)):

        filename = vsummary[i]['path']

        try:
            with open(UPLOAD_FOLDER + filename[:-3] +'txt') as f:
                lines = f.read()

            chaps = lines.split('\n')

            chapters = []
            for chap in chaps:
                chapt = chap.split(';')
                if len(chapt)!=3:
                    continue

                date_time = datetime.datetime.strptime(chapt[-2], "%H:%M:%S.%f")
                start = (date_time - datetime.datetime(1900, 1, 1)).total_seconds()

                date_time = datetime.datetime.strptime(chapt[-1], "%H:%M:%S.%f")
                end = (date_time - datetime.datetime(1900, 1, 1)).total_seconds()

                chapters.append({'title':chapt[0],'start':start,'end':end})

            vsummary[i]['chapters'] = chapters
        except:
            vsummary[i]['chapters'] = []



    if result > 0 and result1 > 0:
        return render_template('dashboard.html', summary=summary, vsummary=vsummary)
    else:
        msg = 'No records found'
        return render_template('dashboard.html', msg=msg)

    cur.close()


class SummaryForm(Form):
    subject = StringField('Subject', [validators.Length(min=1, max=50)])
    datee = StringField('Date(DD/MM/YYYY)', [validators.Length(min=10, max=25)])
    link = TextAreaField('Link', [validators.Length(min=5)])


@app.route('/add_link', methods=['GET', 'POST'])
def add_link():
    form = SummaryForm(request.form)
    if request.method == 'POST' and form.validate():
        subject = form.subject.data
        datee = form.datee.data
        link = form.link.data

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO summary(teacher, subject, datee, link) VALUES (%s, %s, %s, %s)",
                    (session['username'], subject, datee, link))
        mysql.connection.commit()
        cur.close()
        flash('The video recording of the lecture has been uploaded to the database!', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_link.html', form=form)


# @app.route('/preblah')
# def my_form():
#     return render_template('test.html')


# @app.route('/blah', methods=['POST'])
# def dynamic_page():
#     a = request.form['a']

#     result = akaa(a)
#     return 'the result is %s' % result

# @app.route('/indexing_process')
# def indexing_process():

#     return "Please wait while the Video is being Indexed"

@app.route('/generate_summary', methods=['POST'])
def generate_summary():

    if request.method == 'POST':

        link = request.form.get('generate')
        # print(link)

        cur = mysql.connection.cursor()
        result = cur.execute('SELECT id FROM summary where link like "'+link+'";')
        id = cur.fetchall()[0]['id']

        filename = 'l'+str(id) + '-summ.txt'

        if os.path.exists('static/summary/' + filename):  

            with open('static/summary/' + filename) as f:
                result = f.read()

        else:
            result = generate_text_summary(link)

            with open('static/summary/' + filename,"w") as myfile:
                myfile.write(result)

        # return 'The Summary is ' + result
        return render_template('summary.html',summ=result)

@app.route('/video_indexer', methods=['POST'])
def video_indexer():

    if request.method == 'POST':

        path = request.form.get('index')
        filename = path

        if not os.path.exists(UPLOAD_FOLDER + filename[:-3] +'txt'):
            index_video('static/uploads/'+filename)

        cur = mysql.connection.cursor()
        result = cur.execute('SELECT * FROM vsummary where path like "'+path+'";')
        vsummary = cur.fetchall()[0]

        with open(UPLOAD_FOLDER + filename[:-3] +'txt') as f:
            lines = f.read()

        chaps = lines.split('\n')

        chapters = []
        for chap in chaps:
            chapt = chap.split(';')
            if len(chapt)!=3:
                continue

            date_time = datetime.datetime.strptime(chapt[-2], "%H:%M:%S.%f")
            start = (date_time - datetime.datetime(1900, 1, 1)).total_seconds()

            date_time = datetime.datetime.strptime(chapt[-1], "%H:%M:%S.%f")
            end = (date_time - datetime.datetime(1900, 1, 1)).total_seconds()

            chapters.append({'title':chapt[0],'start':start,'end':end})

        vsummary['chapters'] = chapters

        return render_template('indexed_video.html',v=vsummary)
            
        # print(path)

        # redirect('/indexing_process')

        

        # flash('Indexing is Done')

        # return redirect('/dashboard')
        # return render_template('indexed_video.html',v=request.form.get('index'))

# @app.route('/indexed_video',methods=['POST'])
# def indexed_video():
#     if request.method == 'POST':

        # return render_template('indexed_video.html',path='aiml.mp4')



if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
