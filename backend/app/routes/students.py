from flask import Blueprint, jsonify, request

from ..services.students_service import create_student, list_students

students_bp = Blueprint("students", __name__)


@students_bp.get("")
def index():
    return jsonify(list_students())


@students_bp.post("")
def create():
    try:
        student = create_student(request.get_json(silent=True) or {})
        return jsonify(student), 201
    except ValueError as error:
        return jsonify({"message": str(error)}), 400
