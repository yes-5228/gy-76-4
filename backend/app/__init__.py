from flask import Flask
from flask_cors import CORS

from .routes.attendance import attendance_bp
from .routes.dashboard import dashboard_bp
from .routes.payroll import payroll_bp
from .routes.students import students_bp
from .routes.teachers import teachers_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(students_bp, url_prefix="/api/students")
    app.register_blueprint(teachers_bp, url_prefix="/api/teachers")
    app.register_blueprint(attendance_bp, url_prefix="/api/attendance")
    app.register_blueprint(payroll_bp, url_prefix="/api/payroll")

    return app
