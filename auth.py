from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from app import db, login_manager
from models import User

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/setup', methods=['GET', 'POST'])
def setup():
    # Check if any users exist
    if User.query.first():
        flash('Setup already completed. Please login.', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('setup.html')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('setup.html')

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('setup.html')

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Admin user created successfully. Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('setup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('sync.dashboard'))

        flash('Invalid username or password', 'error')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))