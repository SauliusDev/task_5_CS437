from datetime import datetime, timedelta
from app.models import AutoResponseRule, BlockedIP, SecurityAction, FailedLoginTracker, UserLocked, AttackLog

def check_and_execute_auto_response(attack_id, attack_type, ip_address, user_id, risk_score):
    rules = AutoResponseRule.get_by_attack_type(attack_type)
    
    for rule in rules:
        if should_trigger_rule(rule, attack_type, ip_address, user_id, risk_score):
            execute_action(rule['action_type'], rule, attack_id, ip_address, user_id, attack_type)

def should_trigger_rule(rule, attack_type, ip_address, user_id, risk_score):
    trigger_condition = rule['trigger_condition']
    threshold = rule['threshold']
    time_window = rule['time_window_minutes']
    
    if trigger_condition == 'failed_attempts':
        recent_attempts = FailedLoginTracker.get_recent_by_ip(ip_address, minutes=time_window)
        return len(recent_attempts) >= threshold
    
    elif trigger_condition == 'failed_login_per_user':
        if not user_id:
            return False
        from app.models import User
        user = User.get_by_id(user_id)
        if user:
            recent_attempts = FailedLoginTracker.get_recent_by_username(user['username'], minutes=time_window)
            return len(recent_attempts) >= threshold
        return False
    
    elif trigger_condition == 'attack_count':
        recent_attacks = AttackLog.get_recent_by_ip(ip_address, minutes=time_window)
        attack_type_count = len([a for a in recent_attacks if a['attack_type'] == attack_type])
        return attack_type_count >= threshold
    
    elif trigger_condition == 'requests_per_minute':
        recent_attacks = AttackLog.get_recent_by_ip(ip_address, minutes=1)
        return len(recent_attacks) >= threshold
    
    elif trigger_condition == 'risk_score':
        return risk_score >= threshold
    
    return False

def execute_action(action_type, rule, attack_id, ip_address, user_id, attack_type_name):
    if action_type == 'block_ip':
        execute_block_ip(ip_address, rule, attack_id, attack_type_name)
    
    elif action_type == 'lock_account':
        if user_id:
            execute_lock_account(user_id, rule, attack_id, attack_type_name)
    
    elif action_type == 'alert_admin':
        execute_alert_admin(ip_address, user_id, rule, attack_id, attack_type_name)
    
    elif action_type == 'rate_limit':
        execute_rate_limit(ip_address, rule, attack_id, attack_type_name)

def execute_block_ip(ip_address, rule, attack_id, attack_type_name):
    existing_block = BlockedIP.is_blocked(ip_address)
    if existing_block:
        return
    
    time_window = rule['time_window_minutes']
    blocked_until = datetime.now() + timedelta(hours=24)
    
    reason = f"Auto-blocked: {attack_type_name} - Rule: {rule['rule_name']}"
    
    BlockedIP.create(
        ip_address=ip_address,
        reason=reason,
        blocked_until=blocked_until,
        auto_unblock=True,
        attack_log_id=attack_id
    )
    
    SecurityAction.create(
        action_type='block_ip',
        target=ip_address,
        reason=reason,
        attack_log_id=attack_id,
        automated=True
    )
    
    AttackLog.mark_action_taken(attack_id, f'ip_blocked_auto_24h')

def execute_lock_account(user_id, rule, attack_id, attack_type_name):
    existing_lock = UserLocked.is_locked(user_id)
    if existing_lock:
        return
    
    locked_until = datetime.now() + timedelta(hours=2)
    reason = f"Auto-locked: {attack_type_name} - Rule: {rule['rule_name']}"
    
    security_action_id = SecurityAction.create(
        action_type='lock_account',
        target=f"user_id:{user_id}",
        reason=reason,
        attack_log_id=attack_id,
        automated=True
    )
    
    UserLocked.lock_user(
        user_id=user_id,
        reason=reason,
        locked_until=locked_until,
        security_action_id=security_action_id
    )
    
    AttackLog.mark_action_taken(attack_id, f'account_locked_auto_2h')

def execute_alert_admin(ip_address, user_id, rule, attack_id, attack_type_name):
    reason = f"Alert: {attack_type_name} - Rule: {rule['rule_name']} - IP: {ip_address}"
    
    SecurityAction.create(
        action_type='alert_admin',
        target=f"ip:{ip_address}",
        reason=reason,
        attack_log_id=attack_id,
        automated=True
    )
    
    AttackLog.mark_action_taken(attack_id, 'admin_alerted')

def execute_rate_limit(ip_address, rule, attack_id, attack_type_name):
    blocked_until = datetime.now() + timedelta(minutes=30)
    reason = f"Rate limited: {attack_type_name} - Rule: {rule['rule_name']}"
    
    existing_block = BlockedIP.is_blocked(ip_address)
    if not existing_block:
        BlockedIP.create(
            ip_address=ip_address,
            reason=reason,
            blocked_until=blocked_until,
            auto_unblock=True,
            attack_log_id=attack_id
        )
        
        SecurityAction.create(
            action_type='block_ip',
            target=ip_address,
            reason=reason,
            attack_log_id=attack_id,
            automated=True
        )
    
    AttackLog.mark_action_taken(attack_id, 'rate_limited_30min')

def cleanup_expired_blocks():
    BlockedIP.cleanup_expired()

def cleanup_old_logs():
    FailedLoginTracker.cleanup_old(days=7)
