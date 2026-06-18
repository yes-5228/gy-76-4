from flask import Blueprint, jsonify, request

from ..services.attendance_service import check_in, list_attendance, revoke_attendance

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.get("")
def index():
    return jsonify(list_attendance())


@attendance_bp.post("")
def create():
    try:
        record = check_in(request.get_json(silent=True) or {})
        return jsonify(record), 201
    except ValueError as error:
        return jsonify({"message": str(error)}), 400


@attendance_bp.delete("/<attendance_id>")
def revoke(attendance_id):
    try:
        record = revoke_attendance(attendance_id, request.get_json(silent=True) or {})
        return jsonify(record)
    except ValueError as error:
        return jsonify({"message": str(error)}), 400
