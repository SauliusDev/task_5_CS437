from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import Valve, CommandLog, Schedule
from app.utils.auth_helpers import login_required, operator_or_admin_required
from app.utils.monitoring import check_and_log_sql_injection
from datetime import datetime
import random

valves_bp = Blueprint('valves', __name__)

@valves_bp.route('/valves')
@login_required
def list_valves():
    valves = Valve.get_all()
    return render_template('valves.html', valves=valves)

@valves_bp.route('/valve/<int:valve_id>')
@login_required
def valve_detail(valve_id):
    valve = Valve.get_by_id(valve_id)
    if not valve:
        flash('Valve not found', 'danger')
        return redirect(url_for('valves.list_valves'))
    
    logs = CommandLog.get_by_valve(valve_id, limit=20)
    
    return render_template('valve_detail.html', valve=valve, logs=logs)

@valves_bp.route('/valves/search', methods=['GET', 'POST'])
@login_required
def search_valves():
    if request.method == 'POST':
        search_term = request.form.get('search', '').strip()
        
        from flask import session
        from app.models import get_db_connection, User
        
        user = User.get_by_id(session.get('user_id'))
        
        if user and user['role'] == 'admin':
            check_and_log_sql_injection(search_term, '/valves/search')
            
            try:
                conn = get_db_connection()
                query = f"SELECT * FROM valves WHERE valve_name LIKE '%{search_term}%' OR location LIKE '%{search_term}%' ORDER BY valve_name"
                valves_raw = conn.execute(query).fetchall()
                conn.close()
                valves = [dict(v) for v in valves_raw]
            except Exception as e:
                flash(f'Search error: {str(e)}', 'danger')
                return redirect(url_for('valves.list_valves'))
        else:
            if check_and_log_sql_injection(search_term, '/valves/search'):
                flash('Invalid search query detected', 'danger')
                return redirect(url_for('valves.list_valves'))
            
            valves = Valve.search(search_term)
        
        return render_template('valves.html', valves=valves, search_term=search_term)
    
    return redirect(url_for('valves.list_valves'))

@valves_bp.route('/valve/<int:valve_id>/control', methods=['POST'])
@operator_or_admin_required
def control_valve(valve_id):
    valve = Valve.get_by_id(valve_id)
    if not valve:
        return jsonify({'error': 'Valve not found'}), 404
    
    action = request.form.get('action')
    target_percentage = request.form.get('target_percentage', type=int)
    
    if action == 'open':
        target_percentage = 100
        command = 'OPEN'
    elif action == 'close':
        target_percentage = 0
        command = 'CLOSE'
    elif action == 'adjust':
        command = 'ADJUST'
        if target_percentage is None or not (0 <= target_percentage <= 100):
            flash('Invalid target percentage', 'danger')
            return redirect(url_for('valves.valve_detail', valve_id=valve_id))
    elif action == 'sync':
        command = 'SYNC'
        target_percentage = valve['open_percentage']
    else:
        flash('Invalid action', 'danger')
        return redirect(url_for('valves.valve_detail', valve_id=valve_id))
    
    success = random.random() > 0.1
    response_time = random.randint(50, 500) if success else random.randint(1000, 5000)
    
    if success:
        Valve.update_status(valve_id, target_percentage, command, request.form.get('user_id', 1))
        CommandLog.create(
            valve_id=valve_id,
            command=command,
            user_id=request.form.get('user_id', 1),
            target_percentage=target_percentage,
            status='success',
            response_time_ms=response_time
        )
        flash(f'Valve {valve["valve_name"]} {command} command executed successfully', 'success')
    else:
        error_msg = random.choice(['Connection timeout', 'Hardware error', 'Invalid response'])
        CommandLog.create(
            valve_id=valve_id,
            command=command,
            user_id=request.form.get('user_id', 1),
            target_percentage=target_percentage,
            status='failed',
            response_time_ms=response_time,
            error_message=error_msg
        )
        flash(f'Valve {valve["valve_name"]} command failed: {error_msg}', 'danger')
    
    return redirect(url_for('valves.valve_detail', valve_id=valve_id))

@valves_bp.route('/schedules')
@login_required
def list_schedules():
    schedules = Schedule.get_all()
    valves = Valve.get_all()
    return render_template('schedules.html', schedules=schedules, valves=valves)

@valves_bp.route('/schedules/create', methods=['POST'])
@operator_or_admin_required
def create_schedule():
    valve_id = request.form.get('valve_id', type=int)
    scheduled_time = request.form.get('scheduled_time')
    command = request.form.get('command')
    target_percentage = request.form.get('target_percentage', type=int)
    
    if not valve_id or not scheduled_time or not command:
        flash('Missing required fields', 'danger')
        return redirect(url_for('valves.list_schedules'))
    
    try:
        scheduled_dt = datetime.fromisoformat(scheduled_time)
    except ValueError:
        flash('Invalid datetime format', 'danger')
        return redirect(url_for('valves.list_schedules'))
    
    if command == 'ADJUST' and (target_percentage is None or not (0 <= target_percentage <= 100)):
        flash('Invalid target percentage for ADJUST command', 'danger')
        return redirect(url_for('valves.list_schedules'))
    
    from flask import session
    Schedule.create(
        valve_id=valve_id,
        scheduled_time=scheduled_dt,
        command=command,
        target_percentage=target_percentage,
        created_by=session.get('user_id')
    )
    
    flash('Schedule created successfully', 'success')
    return redirect(url_for('valves.list_schedules'))

@valves_bp.route('/schedules/<int:schedule_id>/cancel', methods=['POST'])
@operator_or_admin_required
def cancel_schedule(schedule_id):
    Schedule.cancel(schedule_id)
    flash('Schedule cancelled', 'success')
    return redirect(url_for('valves.list_schedules'))

