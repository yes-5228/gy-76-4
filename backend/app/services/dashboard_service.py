from datetime import date

from ..config import RENEWAL_THRESHOLD
from ..storage import read_data
from .payroll_service import calculate_payroll


def dashboard_summary():
    data = read_data()
    current_month = date.today().strftime("%Y-%m")
    month_attendance = [item for item in data["attendance"] if item["checked_at"].startswith(current_month)]
    payroll = calculate_payroll(current_month)

    return {
        "total_students": len(data["students"]),
        "active_students": len([item for item in data["students"] if item["status"] == "active"]),
        "renewal_count": len(
            [
                item
                for item in data["students"]
                if item["status"] == "active" and item["remaining_hours"] <= RENEWAL_THRESHOLD
            ]
        ),
        "month_consumed_hours": round(sum(float(item["hours"]) for item in month_attendance), 2),
        "month_payroll_amount": round(sum(float(item["amount"]) for item in payroll), 2),
        "recent_attendance": sorted(data["attendance"], key=lambda item: item["checked_at"], reverse=True)[:5],
    }
