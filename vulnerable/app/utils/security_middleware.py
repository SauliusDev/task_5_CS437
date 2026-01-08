from flask import request, session, jsonify, abort
from functools import wraps
from app.models import BlockedIP, UserLocked
from app.utils.monitoring import (
    check_and_log_suspicious_agent,
    check_and_log_rate_limit,
    check_and_log_session_anomaly,
    check_and_log_cookie_manipulation,
    log_404_for_brute_force_detection,
    log_unauthorized_access
)

def check_ip_blocked():
    ip_address = request.remote_addr
    blocked = BlockedIP.is_blocked(ip_address)
    
    if blocked:
        return jsonify({
            'error': 'Access Denied',
            'message': 'Your IP address has been blocked',
            'reason': blocked['reason'],
            'contact': 'Please contact the administrator if you believe this is an error'
        }), 403
    
    return None

def check_user_locked():
    user_id = session.get('user_id')
    
    if user_id:
        locked = UserLocked.is_locked(user_id)
        
        if locked:
            session.clear()
            return jsonify({
                'error': 'Account Locked',
                'message': 'Your account has been locked',
                'reason': locked['reason'],
                'locked_until': locked.get('locked_until', 'Indefinitely')
            }), 403
    
    return None

def track_ip_in_session():
    if 'user_id' in session and 'ip_address' not in session:
        session['ip_address'] = request.remote_addr

def security_checks():
    ip_blocked = check_ip_blocked()
    if ip_blocked:
        return ip_blocked
    
    user_locked = check_user_locked()
    if user_locked:
        return user_locked
    
    track_ip_in_session()
    
    check_and_log_suspicious_agent(request.path)
    
    if not request.path.startswith('/static'):
        check_and_log_cookie_manipulation()
    
    return None

def rate_limit_check(endpoint_prefix):
    if request.path.startswith(endpoint_prefix):
        if check_and_log_rate_limit(request.path):
            return jsonify({
                'error': 'Rate Limit Exceeded',
                'message': 'Too many requests. Please slow down.'
            }), 429
    
    return None

def log_404_handler(error):
    log_404_for_brute_force_detection(request.path)
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found'
    }), 404

def require_role(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = session.get('role', 'guest')
            
            if user_role != required_role and user_role != 'admin':
                log_unauthorized_access(request.path, required_role)
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
