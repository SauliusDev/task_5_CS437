from flask import Flask
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.valves import valves_bp
from app.routes.upload import upload_bp
from app.routes.monitoring import monitoring_bp
from app.routes.logs import logs_bp
from app.routes.security_actions import security_actions_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(valves_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(monitoring_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(security_actions_bp)

from app.utils.security_middleware import security_checks, log_404_handler

@app.before_request
def before_request_security():
    return security_checks()

@app.errorhandler(404)
def handle_404(error):
    return log_404_handler(error)

