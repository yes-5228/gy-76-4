from flask import Blueprint, jsonify, request

from ..services.payroll_service import calculate_payroll, settle_payroll, revoke_settlement, list_adjustments, list_settled_months

payroll_bp = Blueprint("payroll", __name__)


@payroll_bp.get("")
def index():
    return jsonify(calculate_payroll(request.args.get("month")))


@payroll_bp.post("/settle")
def settle():
    try:
        settlement = settle_payroll(request.get_json(silent=True) or {})
        return jsonify(settlement)
    except ValueError as error:
        return jsonify({"message": str(error)}), 400


@payroll_bp.delete("/settle")
def settle_revoke():
    try:
        result = revoke_settlement(request.get_json(silent=True) or {})
        return jsonify(result)
    except ValueError as error:
        return jsonify({"message": str(error)}), 400


@payroll_bp.get("/adjustments")
def adjustments():
    teacher_id = request.args.get("teacher_id")
    month = request.args.get("month")
    return jsonify(list_adjustments(teacher_id=teacher_id, month=month))


@payroll_bp.get("/settled-months")
def settled_months():
    return jsonify(list_settled_months())
