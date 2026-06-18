from datetime import date

from .validation import require_fields
from ..storage import mutate, new_id, read_data


def calculate_payroll(month=None):
    target_month = month or date.today().strftime("%Y-%m")
    data = read_data()
    settlements = {(item["teacher_id"], item["month"]): item for item in data["payroll_settlements"]}
    adjustments = data["payroll_adjustments"]

    rows = []
    for teacher in data["teachers"]:
        records = [
            item
            for item in data["attendance"]
            if item["teacher_id"] == teacher["id"]
            and item["checked_at"].startswith(target_month)
            and not item.get("revoked", False)
        ]
        total_hours = round(sum(float(item["hours"]) for item in records), 2)
        current_amount = round(total_hours * float(teacher["hourly_rate"]), 2)

        settlement = settlements.get((teacher["id"], target_month))
        teacher_adjustments = [
            a for a in adjustments if a["teacher_id"] == teacher["id"] and a["month"] == target_month
        ]
        adjustment_amount = round(sum(float(a["amount_diff"]) for a in teacher_adjustments), 2)
        adjustment_hours = round(sum(float(a["hours_diff"]) for a in teacher_adjustments), 2)

        if settlement:
            settled_amount = float(settlement["amount"])
            settled_hours = float(settlement["total_hours"])
            final_amount = round(settled_amount + adjustment_amount, 2)
            final_hours = round(settled_hours + adjustment_hours, 2)
            diff_amount = round(current_amount - settled_amount - adjustment_amount, 2)
        else:
            settled_amount = None
            settled_hours = None
            final_amount = current_amount
            final_hours = total_hours
            diff_amount = 0

        rows.append(
            {
                "teacher_id": teacher["id"],
                "teacher_name": teacher["name"],
                "subject": teacher["subject"],
                "month": target_month,
                "total_hours": final_hours,
                "current_hours": total_hours,
                "settled_hours": settled_hours,
                "adjustment_hours": adjustment_hours,
                "hourly_rate": teacher["hourly_rate"],
                "amount": final_amount,
                "current_amount": current_amount,
                "settled_amount": settled_amount,
                "adjustment_amount": adjustment_amount,
                "diff_amount": diff_amount,
                "status": settlement["status"] if settlement else "pending",
                "settled_at": settlement.get("settled_at") if settlement else None,
                "adjustments": teacher_adjustments,
                "is_locked": settlement is not None,
            }
        )
    return rows


def settle_payroll(payload):
    require_fields(payload, ["teacher_id", "month"])
    target_month = payload["month"]
    teacher_id = payload["teacher_id"]

    data = read_data()
    teacher = next((t for t in data["teachers"] if t["id"] == teacher_id), None)
    if not teacher:
        raise ValueError("教师不存在")

    records = [
        item
        for item in data["attendance"]
        if item["teacher_id"] == teacher_id
        and item["checked_at"].startswith(target_month)
        and not item.get("revoked", False)
    ]
    total_hours = round(sum(float(item["hours"]) for item in records), 2)
    amount = round(total_hours * float(teacher["hourly_rate"]), 2)

    settlement = {
        "teacher_id": teacher_id,
        "month": target_month,
        "status": "settled",
        "settled_at": date.today().isoformat(),
        "total_hours": total_hours,
        "hourly_rate": teacher["hourly_rate"],
        "amount": amount,
        "attendance_ids": [r["id"] for r in records],
    }

    def upsert(data):
        existing = next(
            (
                item
                for item in data["payroll_settlements"]
                if item["teacher_id"] == settlement["teacher_id"] and item["month"] == settlement["month"]
            ),
            None,
        )
        if existing:
            raise ValueError("该月份已结算，无法重复结算")
        else:
            data["payroll_settlements"].append(settlement)
        return data

    mutate(upsert)
    return settlement


def revoke_settlement(payload):
    require_fields(payload, ["teacher_id", "month"])
    teacher_id = payload["teacher_id"]
    target_month = payload["month"]

    def do_revoke(data):
        settlement_idx = next(
            (
                idx
                for idx, item in enumerate(data["payroll_settlements"])
                if item["teacher_id"] == teacher_id and item["month"] == target_month
            ),
            None,
        )
        if settlement_idx is None:
            raise ValueError("该月份未结算，无法撤回")

        del data["payroll_settlements"][settlement_idx]

        data["payroll_adjustments"] = [
            a for a in data["payroll_adjustments"]
            if not (a["teacher_id"] == teacher_id and a["month"] == target_month)
        ]

        return data

    mutate(do_revoke)
    return {"teacher_id": teacher_id, "month": target_month, "revoked": True}


def build_adjustment(teacher_id, month, attendance_id, hours_diff, amount_diff, reason):
    return {
        "id": new_id("adj"),
        "teacher_id": teacher_id,
        "month": month,
        "attendance_id": attendance_id,
        "hours_diff": round(float(hours_diff), 2),
        "amount_diff": round(float(amount_diff), 2),
        "reason": reason,
        "created_at": date.today().isoformat(),
    }


def is_settled(teacher_id, month):
    data = read_data()
    return any(
        s["teacher_id"] == teacher_id and s["month"] == month and s["status"] == "settled"
        for s in data["payroll_settlements"]
    )


def get_settlement(teacher_id, month):
    data = read_data()
    return next(
        (s for s in data["payroll_settlements"] if s["teacher_id"] == teacher_id and s["month"] == month),
        None,
    )


def list_settled_months():
    data = read_data()
    return [
        {
            "teacher_id": s["teacher_id"],
            "month": s["month"],
            "settled_at": s["settled_at"],
        }
        for s in data["payroll_settlements"]
        if s["status"] == "settled"
    ]


def list_adjustments(teacher_id=None, month=None):
    data = read_data()
    adjustments = data["payroll_adjustments"]
    if teacher_id:
        adjustments = [a for a in adjustments if a["teacher_id"] == teacher_id]
    if month:
        adjustments = [a for a in adjustments if a["month"] == month]
    return adjustments
