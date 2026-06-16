from flask import Blueprint, jsonify, request

from ..services.teachers_service import create_teacher, list_teachers

teachers_bp = Blueprint("teachers", __name__)


@teachers_bp.get("")
def index():
    return jsonify(list_teachers())


@teachers_bp.post("")
def create():
    try:
        teacher = create_teacher(request.get_json(silent=True) or {})
        return jsonify(teacher), 201
    except ValueError as error:
        return jsonify({"message": str(error)}), 400
