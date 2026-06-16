from datetime import date

from .validation import require_fields
from ..storage import mutate, read_data


def calculate_payroll(month=None):
    target_month = month or date.today().strftime("%Y-%m")
    data = read_data()
    settlements = {(item["teacher_id"], item["month"]): item for item in data["payroll_settlements"]}

    rows = []
    for teacher in data["teachers"]:
        records = [
            item
            for item in data["attendance"]
            if item["teacher_id"] == teacher["id"] and item["checked_at"].startswith(target_month)
        ]
        total_hours = round(sum(float(item["hours"]) for item in records), 2)
        amount = round(total_hours * float(teacher["hourly_rate"]), 2)
        settlement = settlements.get((teacher["id"], target_month))
        rows.append(
            {
                "teacher_id": teacher["id"],
                "teacher_name": teacher["name"],
                "subject": teacher["subject"],
                "month": target_month,
                "total_hours": total_hours,
                "hourly_rate": teacher["hourly_rate"],
                "amount": amount,
                "status": settlement["status"] if settlement else "pending",
                "settled_at": settlement.get("settled_at") if settlement else None,
            }
        )
    return rows


def settle_payroll(payload):
    require_fields(payload, ["teacher_id", "month"])
    settlement = {
        "teacher_id": payload["teacher_id"],
        "month": payload["month"],
        "status": "settled",
        "settled_at": date.today().isoformat(),
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
            existing.update(settlement)
        else:
            data["payroll_settlements"].append(settlement)
        return data

    mutate(upsert)
    return settlement
