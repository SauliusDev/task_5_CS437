from flask import Blueprint, render_template, request
from app.models import CommandLog
from app.utils.auth_helpers import login_required

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/logs/commands')
@login_required
def command_logs():
    limit = request.args.get('limit', 100, type=int)
    logs = CommandLog.get_all(limit=limit)
    return render_template('logs.html', logs=logs, log_type='commands')

@logs_bp.route('/logs/failures')
@login_required
def failure_logs():
    limit = request.args.get('limit', 100, type=int)
    logs = CommandLog.get_failed(limit=limit)
    return render_template('logs.html', logs=logs, log_type='failures')

@logs_bp.route('/logs/timeouts')
@login_required
def timeout_logs():
    limit = request.args.get('limit', 100, type=int)
    logs = CommandLog.get_timeouts(limit=limit)
    return render_template('logs.html', logs=logs, log_type='timeouts')

