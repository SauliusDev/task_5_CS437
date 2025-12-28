from flask import Blueprint, render_template, jsonify, request
from app.models import AttackLog
from app.utils.auth_helpers import admin_required

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/monitoring')
@admin_required
def index():
    stats = AttackLog.get_statistics()
    recent_attacks = AttackLog.get_all(limit=50)
    
    return render_template('monitoring.html', stats=stats, attacks=recent_attacks)

@monitoring_bp.route('/api/monitoring/stats')
@admin_required
def get_stats():
    stats = AttackLog.get_statistics()
    return jsonify(stats)

@monitoring_bp.route('/api/monitoring/attacks')
@admin_required
def get_attacks():
    limit = request.args.get('limit', 50, type=int)
    attacks = AttackLog.get_all(limit=limit)
    return jsonify(attacks)

