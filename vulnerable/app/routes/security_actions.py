from flask import Blueprint, request, jsonify, session
from app.models import BlockedIP, SecurityAction, UserLocked, AutoResponseRule, AttackLog
from app.utils.auth_helpers import admin_required
from datetime import datetime, timedelta

security_actions_bp = Blueprint('security_actions', __name__)

@security_actions_bp.route('/api/security/block-ip', methods=['POST'])
@admin_required
def block_ip():
    data = request.get_json()
    ip_address = data.get('ip_address')
    reason = data.get('reason', 'Manually blocked by admin')
    duration_hours = data.get('duration_hours', 24)
    
    if not ip_address:
        return jsonify({'error': 'IP address is required'}), 400
    
    existing = BlockedIP.is_blocked(ip_address)
    if existing:
        return jsonify({'error': 'IP address is already blocked'}), 400
    
    blocked_until = datetime.now() + timedelta(hours=duration_hours) if duration_hours > 0 else None
    
    BlockedIP.create(
        ip_address=ip_address,
        reason=reason,
        blocked_until=blocked_until,
        auto_unblock=False,
        blocked_by_user_id=session.get('user_id')
    )
    
    SecurityAction.create(
        action_type='block_ip',
        target=ip_address,
        reason=reason,
        executed_by=session.get('user_id'),
        automated=False
    )
    
    return jsonify({
        'success': True,
        'message': f'IP {ip_address} has been blocked',
        'blocked_until': blocked_until.isoformat() if blocked_until else 'permanent'
    })

@security_actions_bp.route('/api/security/unblock-ip', methods=['POST'])
@admin_required
def unblock_ip():
    data = request.get_json()
    ip_address = data.get('ip_address')
    
    if not ip_address:
        return jsonify({'error': 'IP address is required'}), 400
    
    BlockedIP.unblock(ip_address)
    
    SecurityAction.create(
        action_type='unblock_ip',
        target=ip_address,
        reason='Manually unblocked by admin',
        executed_by=session.get('user_id'),
        automated=False
    )
    
    return jsonify({
        'success': True,
        'message': f'IP {ip_address} has been unblocked'
    })

@security_actions_bp.route('/api/security/lock-account', methods=['POST'])
@admin_required
def lock_account():
    data = request.get_json()
    user_id = data.get('user_id')
    reason = data.get('reason', 'Manually locked by admin')
    duration_hours = data.get('duration_hours', 0)
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    from app.models import User
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    existing = UserLocked.is_locked(user_id)
    if existing:
        return jsonify({'error': 'User is already locked'}), 400
    
    locked_until = datetime.now() + timedelta(hours=duration_hours) if duration_hours > 0 else None
    
    security_action_id = SecurityAction.create(
        action_type='lock_account',
        target=f"user_id:{user_id} ({user['username']})",
        reason=reason,
        executed_by=session.get('user_id'),
        automated=False
    )
    
    UserLocked.lock_user(
        user_id=user_id,
        reason=reason,
        locked_until=locked_until,
        locked_by=session.get('user_id'),
        security_action_id=security_action_id
    )
    
    return jsonify({
        'success': True,
        'message': f'User {user["username"]} has been locked',
        'locked_until': locked_until.isoformat() if locked_until else 'permanent'
    })

@security_actions_bp.route('/api/security/unlock-account', methods=['POST'])
@admin_required
def unlock_account():
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    from app.models import User
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    UserLocked.unlock_user(user_id)
    
    SecurityAction.create(
        action_type='unlock_account',
        target=f"user_id:{user_id} ({user['username']})",
        reason='Manually unlocked by admin',
        executed_by=session.get('user_id'),
        automated=False
    )
    
    return jsonify({
        'success': True,
        'message': f'User {user["username"]} has been unlocked'
    })

@security_actions_bp.route('/api/security/clear-sessions', methods=['POST'])
@admin_required
def clear_sessions():
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    from app.models import User
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    SecurityAction.create(
        action_type='clear_sessions',
        target=f"user_id:{user_id} ({user['username']})",
        reason='Sessions cleared by admin',
        executed_by=session.get('user_id'),
        automated=False
    )
    
    return jsonify({
        'success': True,
        'message': f'Sessions cleared for user {user["username"]}'
    })

@security_actions_bp.route('/api/security/blocked-ips', methods=['GET'])
@admin_required
def get_blocked_ips():
    blocked_ips = BlockedIP.get_all_active()
    return jsonify(blocked_ips)

@security_actions_bp.route('/api/security/actions-history', methods=['GET'])
@admin_required
def get_actions_history():
    limit = request.args.get('limit', 100, type=int)
    actions = SecurityAction.get_all(limit=limit)
    return jsonify(actions)

@security_actions_bp.route('/api/security/reverse-action/<int:action_id>', methods=['POST'])
@admin_required
def reverse_action(action_id):
    actions = SecurityAction.get_all(limit=1000)
    action = next((a for a in actions if a['id'] == action_id), None)
    
    if not action:
        return jsonify({'error': 'Action not found'}), 404
    
    if action['reversed_at']:
        return jsonify({'error': 'Action already reversed'}), 400
    
    if action['action_type'] == 'block_ip':
        ip_address = action['target']
        BlockedIP.unblock(ip_address)
    
    elif action['action_type'] == 'lock_account':
        import re
        match = re.search(r'user_id:(\d+)', action['target'])
        if match:
            user_id = int(match.group(1))
            UserLocked.unlock_user(user_id)
    
    SecurityAction.reverse_action(action_id, session.get('user_id'))
    
    return jsonify({
        'success': True,
        'message': 'Action has been reversed'
    })

@security_actions_bp.route('/api/security/configure-auto-response', methods=['POST'])
@admin_required
def configure_auto_response():
    data = request.get_json()
    rule_id = data.get('rule_id')
    action = data.get('action')
    
    if not rule_id or not action:
        return jsonify({'error': 'Rule ID and action are required'}), 400
    
    if action == 'toggle':
        AutoResponseRule.toggle_enabled(rule_id)
        return jsonify({'success': True, 'message': 'Rule toggled'})
    
    elif action == 'update_threshold':
        threshold = data.get('threshold')
        if not threshold:
            return jsonify({'error': 'Threshold is required'}), 400
        AutoResponseRule.update_threshold(rule_id, threshold)
        return jsonify({'success': True, 'message': 'Threshold updated'})
    
    return jsonify({'error': 'Invalid action'}), 400

@security_actions_bp.route('/api/security/auto-response-rules', methods=['GET'])
@admin_required
def get_auto_response_rules():
    rules = AutoResponseRule.get_all()
    return jsonify(rules)

@security_actions_bp.route('/api/security/attack-details/<int:attack_id>', methods=['GET'])
@admin_required
def get_attack_details(attack_id):
    attacks = AttackLog.get_all(limit=10000)
    attack = next((a for a in attacks if a['id'] == attack_id), None)
    
    if not attack:
        return jsonify({'error': 'Attack not found'}), 404
    
    chains = AttackLog.get_attack_chains(attack_id)
    
    return jsonify({
        'attack': attack,
        'related_attacks': chains
    })

@security_actions_bp.route('/api/security/locked-accounts', methods=['GET'])
@admin_required
def get_locked_accounts():
    locked = UserLocked.get_all_locked()
    return jsonify(locked)
