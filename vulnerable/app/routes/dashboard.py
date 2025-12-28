from flask import Blueprint, render_template, session
from app.models import Valve, CommandLog, Schedule
from app.utils.auth_helpers import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    valves = Valve.get_all()
    
    total_valves = len(valves)
    operational = sum(1 for v in valves if v['status'] == 'operational')
    connected = sum(1 for v in valves if v['communication_status'] == 'connected')
    avg_open = sum(v['open_percentage'] for v in valves) / total_valves if total_valves > 0 else 0
    
    recent_logs = CommandLog.get_all(limit=10)
    pending_schedules = Schedule.get_pending()
    
    stats = {
        'total_valves': total_valves,
        'operational': operational,
        'connected': connected,
        'avg_open_percentage': round(avg_open, 1),
        'recent_logs_count': len(recent_logs),
        'pending_schedules_count': len(pending_schedules)
    }
    
    return render_template('dashboard.html', 
                         valves=valves[:20],
                         stats=stats,
                         recent_logs=recent_logs,
                         pending_schedules=pending_schedules[:5])

