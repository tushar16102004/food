import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong secret key

# Configure file upload settings
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# In-memory data storage (for demonstration purposes)
users = {}
donations = []

@app.route('/')
def index():
    return render_template('index.html', donations=donations)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('Username already exists')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        users[username] = hashed_password
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('donate'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin':
            session['username'] = username
            return redirect(url_for('admin'))

        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            return redirect(url_for('donate'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin':
            session['username'] = username
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password')

    return render_template('adminlogin.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        donor_name = session['username']
        food_item = request.form['food_item']
        quantity = request.form['quantity']
        location = request.form['location']
        image = request.files.get('image')

        if donor_name and food_item and quantity and location:
            donation = {
                'donor_name': donor_name,
                'food_item': food_item,
                'quantity': quantity,
                'location': location,
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'acknowledged': False,
                'image_url': None
            }

            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                donation['image_url'] = url_for('static', filename='uploads/' + filename)

            donations.append(donation)
        return redirect(url_for('index'))

    return render_template('donate.html')

@app.route('/admin')
def admin():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('admin.html', donations=donations)

@app.route('/acknowledge/<int:donation_id>')
def acknowledge(donation_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if 0 <= donation_id < len(donations):
        donations[donation_id]['acknowledged'] = True
    return redirect(url_for('admin'))

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
