from flask import Blueprint, jsonify, request

from ..services.attendance_service import check_in, list_attendance

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
