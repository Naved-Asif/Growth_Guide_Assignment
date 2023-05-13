from flask import Flask, render_template, request, send_file, session,redirect, flash
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = "Shalimar@2"

# Define the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define the admin login credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

# Check if a user is authenticated or not
def is_authenticated():
    if 'username' in session and session['username'] == ADMIN_USERNAME:
        return True
    else:
        return False

@app.context_processor
def inject_functions():
    return dict(
        is_authenticated=is_authenticated
    )

# Home Page
@app.route('/')
def home():
    if not is_authenticated():
        return redirect('/admin_login')
    else:
        return render_template('dashboard.html')

# Admin Login Page
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['username'] = ADMIN_USERNAME
            flash('You are now logged in', 'success')
            return redirect('/dashboard')
        else:
            return render_template('admin_login.html', error=True)
    else:
        return render_template('admin_login.html', error=False)

# Upload Page
@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if not is_authenticated():
        return redirect('/admin_login')
    else:
        return render_template('dashboard.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not is_authenticated():
        return redirect('/admin_login')
    else:
        if request.method == 'POST':
            file = request.files['file']
            if file:
                if not os.path.isdir(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect('/')
        return render_template('upload.html')


# File List Page
@app.route('/files')
def files():
    if not is_authenticated():
        return redirect('/admin_login')
    else:
        file_list = os.listdir(app.config['UPLOAD_FOLDER'])
        return render_template('files.html', files=file_list)

@app.route('/download/<filename>')
def download_file(filename):
    if not is_authenticated():
        return redirect('/admin_login')
    else:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

#open_file

@app.route('/open/<filename>')
def open_file(filename):
    if not is_authenticated():
        return redirect('/admin_login')
    else:
        encodings = ["utf-8-sig", "cp1252", "iso-8859-1", "latin1"]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if filename.endswith('.csv'):
            try:
                for encoding in encodings:
                    df = pd.read_csv(file_path,encoding=encoding)
            except:
                flash("ERROR while reading a while")
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            return "Invalid file format"
        return render_template('table.html',title=filename, table=df.to_html())
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect('/admin_login')

if __name__ == '__main__':
    app.run(port=8080,debug=True)
