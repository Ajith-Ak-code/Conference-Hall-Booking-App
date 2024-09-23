from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hall_name = db.Column(db.String(100), nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
            return redirect(url_for('register'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Login failed. Check your username and password.')
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', bookings=bookings)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))


@app.route('/book', methods=['POST'])
@login_required
def book():
    hall_name = request.form['hall_name']
    booking_date = datetime.strptime(request.form['booking_date'], '%Y-%m-%dT%H:%M')
    if booking_date < datetime.now():
        flash('Booking date must be in the future!')
    else:
        new_booking = Booking(user_id=current_user.id, hall_name=hall_name, booking_date=booking_date)
        db.session.add(new_booking)
        db.session.commit()
        flash('Booking successful!')
    return redirect(url_for('dashboard'))


@app.route('/delete/<int:booking_id>', methods=['POST'])
@login_required
def delete(booking_id):
    booking = Booking.query.get(booking_id)
    if booking and booking.user_id == current_user.id:
        db.session.delete(booking)
        db.session.commit()
        flash('Booking deleted successfully.')
    else:
        flash('Booking not found or unauthorized.')
    return redirect(url_for('dashboard'))


@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True, port=8000)
