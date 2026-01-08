from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import User, FailedLoginTracker, UserLocked
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
        user_agent = request.headers.get('User-Agent', '')
        
        recent_failed_attempts_ip = FailedLoginTracker.get_recent_by_ip(ip_address, minutes=10)
        if len(recent_failed_attempts_ip) >= 10:
            flash('Too many failed login attempts. Please try again later.', 'danger')
            return render_template('login.html'), 429
        
        if username:
            recent_failed_attempts_user = FailedLoginTracker.get_recent_by_username(username, minutes=15)
            if len(recent_failed_attempts_user) >= 5:
                flash('Account temporarily locked due to multiple failed login attempts.', 'danger')
                return render_template('login.html'), 403
        
        user = User.authenticate(username, password)
        
        if user:
            user_locked = UserLocked.is_locked(user['id'])
            if user_locked:
                flash(f'Your account is locked: {user_locked["reason"]}', 'danger')
                return render_template('login.html'), 403
            
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['ip_address'] = ip_address
            
            User.update_last_login(user['id'])
            
            recent_failed = FailedLoginTracker.get_recent_by_username(username, minutes=15)
            if len(recent_failed) > 0:
                flash(f'Welcome back, {user["username"]}! Note: {len(recent_failed)} failed login attempt(s) detected.', 'warning')
            else:
                flash(f'Welcome back, {user["username"]}!', 'success')
            
            return redirect(url_for('dashboard.index'))
        else:
            attack_id = log_attack(
                attack_type='login_brute_force',
                endpoint='/login',
                payload=f'username: {username}',
                severity='medium',
                blocked=False,
                details=f'Failed login attempt for user: {username}'
            )
            
            FailedLoginTracker.create(
                username=username or 'unknown',
                ip_address=ip_address,
                user_agent=user_agent,
                attack_log_id=attack_id
            )
            
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

