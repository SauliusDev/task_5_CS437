from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import User
from app.utils.monitoring import log_attack

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        ip_address = request.remote_addr
        
        user = User.authenticate(username, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['ip_address'] = ip_address
            
            User.update_last_login(user['id'])
            flash(f'Welcome back, {user["username"]}!', 'success')
            
            return redirect(url_for('dashboard.index'))
        else:
            log_attack(
                attack_type='login_brute_force',
                endpoint='/login',
                payload=f'username: {username}',
                severity='medium',
                details=f'Failed login attempt for user: {username}'
            )
            
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

