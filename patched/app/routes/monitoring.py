from flask import Blueprint, render_template, jsonify, request
from app.models import AttackLog, BlockedIP, SecurityAction, AutoResponseRule, UserLocked
from app.utils.auth_helpers import admin_required

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/monitoring')
@admin_required
def index():
    stats = AttackLog.get_statistics()
    recent_attacks = AttackLog.get_all(limit=50)
    high_risk_attacks = AttackLog.get_high_risk(threshold=70, limit=20)
    actionable_attacks = AttackLog.get_actionable(limit=20)
    blocked_ips = BlockedIP.get_all_active()
    locked_accounts = UserLocked.get_all_locked()
    recent_actions = SecurityAction.get_all(limit=20)
    auto_rules = AutoResponseRule.get_all()
    
    return render_template('monitoring.html', 
                         stats=stats, 
                         attacks=recent_attacks,
                         high_risk_attacks=high_risk_attacks,
                         actionable_attacks=actionable_attacks,
                         blocked_ips=blocked_ips,
                         locked_accounts=locked_accounts,
                         recent_actions=recent_actions,
                         auto_rules=auto_rules)

@monitoring_bp.route('/api/monitoring/stats')
@admin_required
def get_stats():
    stats = AttackLog.get_statistics()
    return jsonify(stats)

@monitoring_bp.route('/api/monitoring/attacks')
@admin_required
def get_attacks():
    limit = request.args.get('limit', 50, type=int)
    attack_type = request.args.get('type')
    risk_threshold = request.args.get('risk_threshold', type=int)
    
    if risk_threshold:
        attacks = AttackLog.get_high_risk(threshold=risk_threshold, limit=limit)
    elif attack_type:
        attacks = AttackLog.get_by_type(attack_type, limit=limit)
    else:
        attacks = AttackLog.get_all(limit=limit)
    
    return jsonify(attacks)

@monitoring_bp.route('/api/monitoring/actionable')
@admin_required
def get_actionable():
    attacks = AttackLog.get_actionable(limit=100)
    return jsonify(attacks)

