import re
import json
from datetime import datetime
from flask import request, session

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

def detect_sql_injection(input_string):
    if not input_string:
        return False
    
    for pattern in SQL_INJECTION_PATTERNS:
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

def log_attack(attack_type, endpoint, payload, severity, details=None):
    user_id = session.get('user_id')
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    request_method = request.method
    
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
        details=details
    )
    
    return attack_id

def check_and_log_sql_injection(search_term, endpoint):
    if detect_sql_injection(search_term):
        log_attack(
            attack_type='sql_injection',
            endpoint=endpoint,
            payload=search_term,
            severity='high',
            details='SQL injection pattern detected in search query'
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
            details=', '.join(issues)
        )
        return True
    return False
