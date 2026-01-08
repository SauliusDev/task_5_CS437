import re
import json
from datetime import datetime, timedelta
from flask import request, session
from collections import defaultdict

SQL_INJECTION_PATTERNS = [
    r"(\bUNION\b.*\bSELECT\b)",
    r"(\bOR\b\s+\d+\s*=\s*\d+)",
    r"('|\")(\s*OR\s*\1\s*=\s*\1)",
    r"(;|\-\-|\/\*|\*\/)",
    r"(\bDROP\b|\bDELETE\b|\bINSERT\b|\bUPDATE\b)",
    r"('.*--)",
    r"('\s*;\s*--)",
]

SUSPICIOUS_EXTENSIONS = [
    '.php', '.php3', '.php4', '.php5', '.phtml',
    '.py', '.sh', '.bat', '.exe', '.cmd',
    '.jsp', '.asp', '.aspx', '.rb', '.pl'
]

PATH_TRAVERSAL_PATTERNS = [
    r'\.\.[/\\]',
    r'\.\.%2[fF]',
    r'%2e%2e[/\\]',
    r'\.\.\\',
]

XSS_PATTERNS = [
    r'<script[^>]*>',
    r'javascript:',
    r'onerror\s*=',
    r'onload\s*=',
    r'<iframe[^>]*>',
    r'eval\(',
    r'expression\(',
]

SUSPICIOUS_USER_AGENTS = [
    'nikto', 'sqlmap', 'nmap', 'masscan', 'burp', 'metasploit',
    'havij', 'acunetix', 'wpscan', 'dirbuster', 'gobuster', 'ffuf'
]

ADMIN_ENDPOINTS = [
    '/admin', '/monitoring', '/api/security', '/upload'
]

request_tracking = defaultdict(list)

def calculate_risk_score(attack_type, ip_address, user_id, endpoint):
    base_scores = {
        'sql_injection': 80,
        'login_brute_force': 70,
        'privilege_escalation': 90,
        'file_upload_abuse': 75,
        'session_hijacking': 85,
        'cookie_manipulation': 70,
        'directory_brute_force': 50,
        'rate_limit_violation': 40,
        'path_traversal': 80,
        'xss_attempt': 60,
        'csrf_attempt': 65,
        'unauthorized_access': 70,
        'size_bypass': 60,
        'mime_bypass': 70,
        'encrypted_payload': 55,
        'suspicious_activity': 50
    }
    
    risk_score = base_scores.get(attack_type, 50)
    
    from app.models import AttackLog
    recent_attacks = AttackLog.get_recent_by_ip(ip_address, minutes=60)
    if recent_attacks and len(recent_attacks) > 3:
        risk_score = min(100, risk_score + (len(recent_attacks) * 5))
    
    if any(admin_ep in endpoint for admin_ep in ADMIN_ENDPOINTS):
        risk_score = min(100, risk_score + 10)
    
    return risk_score

def classify_attack(attack_type, endpoint, payload):
    if attack_type in ['directory_brute_force', 'unauthorized_access']:
        category = 'reconnaissance'
        stage = 'reconnaissance'
    elif attack_type in ['sql_injection', 'file_upload_abuse', 'xss_attempt', 'login_brute_force']:
        category = 'exploitation'
        stage = 'exploitation'
    elif attack_type in ['privilege_escalation', 'session_hijacking', 'cookie_manipulation']:
        category = 'post_exploitation'
        stage = 'post_exploitation'
    else:
        category = 'general_attack'
        stage = 'unknown'
    
    return category, stage

def recommend_action(attack_type, risk_score, attack_count):
    if attack_type == 'login_brute_force' and attack_count >= 5:
        return 'block_ip_temporary', ['Navigate to /monitoring', 'Find IP in blocked list', 'Click Unblock button']
    elif attack_type == 'sql_injection':
        return 'block_ip_permanent', ['Navigate to /monitoring', 'Go to Blocked IPs', 'Select IP and click Unblock']
    elif attack_type == 'privilege_escalation':
        return 'block_ip_and_alert', ['Check /monitoring for alerts', 'Review security actions', 'Unblock if false positive']
    elif attack_type == 'rate_limit_violation' and risk_score > 60:
        return 'rate_limit', ['Navigate to /monitoring', 'View rate limited IPs', 'Remove from rate limit list']
    elif risk_score >= 80:
        return 'block_ip_and_alert', ['Check /monitoring', 'Review blocked IPs', 'Unblock after investigation']
    elif risk_score >= 60:
        return 'alert_admin', ['Review alert in /monitoring', 'Mark as resolved']
    else:
        return 'log_only', ['No action needed', 'Monitoring for pattern']
    
    return 'log_only', ['Review in monitoring dashboard']

def detect_sql_injection(input_string):
    if not input_string:
        return False
    
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, input_string, re.IGNORECASE):
            return True
    return False

def detect_xss(input_string):
    if not input_string:
        return False
    
    for pattern in XSS_PATTERNS:
        if re.search(pattern, input_string, re.IGNORECASE):
            return True
    return False

def detect_path_traversal(input_string):
    if not input_string:
        return False
    
    for pattern in PATH_TRAVERSAL_PATTERNS:
        if re.search(pattern, input_string, re.IGNORECASE):
            return True
    return False

def detect_file_upload_abuse(filename, content_type, file_size):
    issues = []
    
    filename_lower = filename.lower()
    for ext in SUSPICIOUS_EXTENSIONS:
        if ext in filename_lower:
            issues.append(f'suspicious_extension:{ext}')
    
    if '..' in filename or '/' in filename or '\\' in filename:
        issues.append('path_traversal_attempt')
    
    double_ext_pattern = r'\.\w+\.\w+$'
    if re.search(double_ext_pattern, filename):
        issues.append('double_extension')
    
    if file_size > 10 * 1024 * 1024:
        issues.append('oversized_file')
    
    return issues

def detect_suspicious_user_agent():
    user_agent = request.headers.get('User-Agent', '').lower()
    for suspicious in SUSPICIOUS_USER_AGENTS:
        if suspicious in user_agent:
            return True, suspicious
    return False, None

def detect_directory_brute_force(ip_address):
    key = f"404_{ip_address}"
    current_time = datetime.now()
    
    if key not in request_tracking:
        request_tracking[key] = []
    
    request_tracking[key].append(current_time)
    
    recent_requests = [t for t in request_tracking[key] if current_time - t < timedelta(minutes=5)]
    request_tracking[key] = recent_requests
    
    if len(recent_requests) >= 20:
        return True, len(recent_requests)
    
    return False, len(recent_requests)

def detect_rate_limit_violation(ip_address, endpoint):
    key = f"rate_{ip_address}_{endpoint}"
    current_time = datetime.now()
    
    if key not in request_tracking:
        request_tracking[key] = []
    
    request_tracking[key].append(current_time)
    
    recent_requests = [t for t in request_tracking[key] if current_time - t < timedelta(minutes=1)]
    request_tracking[key] = recent_requests
    
    if len(recent_requests) > 100:
        return True, len(recent_requests)
    
    return False, len(recent_requests)

def detect_session_anomaly(user_id, ip_address):
    if not user_id or not session:
        return False, None
    
    session_ip = session.get('ip_address')
    if session_ip and session_ip != ip_address:
        return True, f"IP changed from {session_ip} to {ip_address}"
    
    return False, None

def detect_cookie_manipulation():
    cookies = request.cookies
    session_cookie = cookies.get('session')
    
    if session_cookie:
        if len(session_cookie) > 1000:
            return True, "Oversized session cookie"
        
        if any(char in session_cookie for char in ['<', '>', '"', "'"]):
            return True, "Suspicious characters in cookie"
    
    return False, None

def detect_privilege_escalation(user_role, endpoint):
    if user_role == 'operator' and any(admin_ep in endpoint for admin_ep in ADMIN_ENDPOINTS):
        return True, f"Operator attempting to access admin endpoint: {endpoint}"
    
    return False, None

def get_request_details():
    details = {
        'headers': dict(request.headers),
        'args': dict(request.args),
        'form': dict(request.form),
        'method': request.method,
        'path': request.path,
        'remote_addr': request.remote_addr,
    }
    return json.dumps(details)

def log_attack(attack_type, endpoint, payload, severity, blocked=False, details=None, 
               classification=None, recommended_action=None, risk_score=None, 
               related_attack_id=None, response_status=None):
    user_id = session.get('user_id')
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    request_method = request.method
    
    if risk_score is None:
        risk_score = calculate_risk_score(attack_type, ip_address, user_id, endpoint)
    
    if classification is None:
        category, stage = classify_attack(attack_type, endpoint, payload)
        classification = f"{category}_{stage}"
    
    if recommended_action is None:
        from app.models import AttackLog
        recent_count = len(AttackLog.get_recent_by_ip(ip_address, minutes=60))
        action, reverse_steps = recommend_action(attack_type, risk_score, recent_count)
        recommended_action = action
        reverse_action_steps = json.dumps(reverse_steps)
    else:
        reverse_action_steps = json.dumps(['Review in monitoring dashboard', 'Take appropriate action'])
    
    raw_request_data = get_request_details()
    
    from app.models import AttackLog
    attack_id = AttackLog.create(
        attack_type=attack_type,
        endpoint=endpoint,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        request_method=request_method,
        payload=payload,
        severity=severity,
        blocked=blocked,
        details=details,
        classification=classification,
        recommended_action=recommended_action,
        risk_score=risk_score,
        related_attack_id=related_attack_id,
        raw_request_data=raw_request_data,
        response_status=response_status,
        reverse_action_steps=reverse_action_steps
    )
    
    from app.utils.auto_response import check_and_execute_auto_response
    check_and_execute_auto_response(attack_id, attack_type, ip_address, user_id, risk_score)
    
    return attack_id

def check_and_log_sql_injection(search_term, endpoint):
    if detect_sql_injection(search_term):
        log_attack(
            attack_type='sql_injection',
            endpoint=endpoint,
            payload=search_term,
            severity='high',
            blocked=True,
            details='SQL injection pattern detected in search query'
        )
        return True
    return False

def check_and_log_xss(input_data, endpoint, field_name='input'):
    if detect_xss(input_data):
        log_attack(
            attack_type='xss_attempt',
            endpoint=endpoint,
            payload=f'{field_name}: {input_data}',
            severity='high',
            blocked=True,
            details=f'XSS pattern detected in {field_name}'
        )
        return True
    return False

def check_and_log_path_traversal(path, endpoint):
    if detect_path_traversal(path):
        log_attack(
            attack_type='path_traversal',
            endpoint=endpoint,
            payload=path,
            severity='high',
            blocked=True,
            details='Path traversal pattern detected'
        )
        return True
    return False

def check_and_log_file_upload(filename, content_type, file_size, endpoint):
    issues = detect_file_upload_abuse(filename, content_type, file_size)
    
    if issues:
        attack_type = 'file_upload_abuse'
        if 'oversized_file' in issues:
            attack_type = 'size_bypass'
        if 'double_extension' in issues or 'suspicious_extension' in str(issues):
            attack_type = 'mime_bypass'
        
        log_attack(
            attack_type=attack_type,
            endpoint=endpoint,
            payload=f'filename:{filename}, size:{file_size}, type:{content_type}',
            severity='high',
            blocked=True,
            details=', '.join(issues)
        )
        return True
    return False

def check_and_log_suspicious_agent(endpoint):
    is_suspicious, agent_name = detect_suspicious_user_agent()
    if is_suspicious:
        log_attack(
            attack_type='suspicious_activity',
            endpoint=endpoint,
            payload=f'User-Agent: {agent_name}',
            severity='medium',
            blocked=False,
            details=f'Suspicious user agent detected: {agent_name}'
        )
        return True
    return False

def check_and_log_rate_limit(endpoint):
    ip_address = request.remote_addr
    is_violation, count = detect_rate_limit_violation(ip_address, endpoint)
    
    if is_violation:
        log_attack(
            attack_type='rate_limit_violation',
            endpoint=endpoint,
            payload=f'{count} requests in 1 minute',
            severity='medium',
            blocked=True,
            details=f'Rate limit exceeded: {count} requests'
        )
        return True
    return False

def check_and_log_privilege_escalation(endpoint):
    user_role = session.get('role', 'guest')
    is_escalation, details = detect_privilege_escalation(user_role, endpoint)
    
    if is_escalation:
        log_attack(
            attack_type='privilege_escalation',
            endpoint=endpoint,
            payload=f'Role: {user_role}',
            severity='critical',
            blocked=True,
            details=details
        )
        return True
    return False

def check_and_log_session_anomaly():
    user_id = session.get('user_id')
    ip_address = request.remote_addr
    
    is_anomaly, details = detect_session_anomaly(user_id, ip_address)
    
    if is_anomaly:
        log_attack(
            attack_type='session_hijacking',
            endpoint=request.path,
            payload=f'User ID: {user_id}',
            severity='high',
            blocked=True,
            details=details
        )
        return True
    return False

def check_and_log_cookie_manipulation():
    is_manipulated, details = detect_cookie_manipulation()
    
    if is_manipulated:
        log_attack(
            attack_type='cookie_manipulation',
            endpoint=request.path,
            payload='Cookie tampering detected',
            severity='high',
            blocked=True,
            details=details
        )
        return True
    return False

def log_404_for_brute_force_detection(path):
    ip_address = request.remote_addr
    is_brute_force, count = detect_directory_brute_force(ip_address)
    
    if is_brute_force and count % 20 == 0:
        log_attack(
            attack_type='directory_brute_force',
            endpoint=path,
            payload=f'{count} 404 errors in 5 minutes',
            severity='medium',
            blocked=False,
            details=f'Directory brute force detected: {count} failed requests'
        )
        return True
    return False

def log_unauthorized_access(endpoint, required_role):
    user_role = session.get('role', 'guest')
    log_attack(
        attack_type='unauthorized_access',
        endpoint=endpoint,
        payload=f'User role: {user_role}, Required: {required_role}',
        severity='medium',
        blocked=True,
        details=f'Unauthorized access attempt to {endpoint}'
    )