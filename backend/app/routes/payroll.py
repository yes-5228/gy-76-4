from flask import Blueprint, jsonify, request

from ..services.payroll_service import calculate_payroll, settle_payroll

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
