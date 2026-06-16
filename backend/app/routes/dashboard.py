from flask import Blueprint, jsonify

from ..services.dashboard_service import dashboard_summary
from ..services.students_service import get_renewal_reminders

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/health")
def health():
    return jsonify({"status": "ok"})


@dashboard_bp.get("/dashboard")
def dashboard():
    return jsonify(dashboard_summary())


@dashboard_bp.get("/reminders")
def reminders():
    return jsonify(get_renewal_reminders())
