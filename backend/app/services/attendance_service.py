from datetime import date

from .validation import require_fields
from .payroll_service import get_settlement, build_adjustment
from ..storage import mutate, new_id, read_data


def list_attendance():
    data = read_data()
    students = {student["id"]: student for student in data["students"]}
    teachers = {teacher["id"]: teacher for teacher in data["teachers"]}
    return [_with_names(record, students, teachers) for record in sorted(data["attendance"], key=lambda item: item["checked_at"], reverse=True)]


def check_in(payload):
    require_fields(payload, ["student_id", "teacher_id", "course_name", "hours"])
    hours = float(payload["hours"])
    if hours <= 0:
        raise ValueError("课时必须大于 0")

    checked_at = payload.get("checked_at") or date.today().isoformat()
    month = checked_at[:7]
    teacher_id = payload["teacher_id"]

    attendance_record = {
        "id": new_id("att"),
        "student_id": payload["student_id"],
        "teacher_id": teacher_id,
        "course_name": payload["course_name"].strip(),
        "hours": hours,
        "checked_at": checked_at,
        "note": payload.get("note", "").strip(),
        "revoked": False,
        "revoked_at": None,
    }

    settlement = get_settlement(teacher_id, month)

    def add_record_and_adjustment(data):
        student = next((item for item in data["students"] if item["id"] == attendance_record["student_id"]), None)
        teacher = next((item for item in data["teachers"] if item["id"] == attendance_record["teacher_id"]), None)
        if not student:
            raise ValueError("学员不存在")
        if not teacher:
            raise ValueError("教师不存在")
        if student["remaining_hours"] < hours:
            raise ValueError("学员剩余课时不足")

        student["remaining_hours"] = round(student["remaining_hours"] - hours, 2)
        data["attendance"].append(attendance_record)

        if settlement:
            hourly_rate = float(settlement["hourly_rate"])
            amount_diff = round(hours * hourly_rate, 2)
            adjustment = build_adjustment(
                teacher_id=teacher_id,
                month=month,
                attendance_id=attendance_record["id"],
                hours_diff=hours,
                amount_diff=amount_diff,
                reason=f"结算后新增签到：{attendance_record['course_name']}（{checked_at}）",
            )
            data["payroll_adjustments"].append(adjustment)
            attendance_record["adjustment_created"] = True
            attendance_record["adjustment_amount"] = amount_diff

        return data

    mutate(add_record_and_adjustment)
    return attendance_record


def revoke_attendance(attendance_id, payload=None):
    payload = payload or {}
    data = read_data()
    record = next((r for r in data["attendance"] if r["id"] == attendance_id), None)
    if not record:
        raise ValueError("签到记录不存在")
    if record.get("revoked"):
        raise ValueError("该签到记录已被撤销")

    month = record["checked_at"][:7]
    teacher_id = record["teacher_id"]
    hours = float(record["hours"])

    settlement = get_settlement(teacher_id, month)

    def do_revoke_and_adjustment(data):
        student = next((s for s in data["students"] if s["id"] == record["student_id"]), None)
        target_record = next((r for r in data["attendance"] if r["id"] == attendance_id), None)

        target_record["revoked"] = True
        target_record["revoked_at"] = date.today().isoformat()
        target_record["revoke_reason"] = payload.get("reason", "").strip()

        if student:
            student["remaining_hours"] = round(student["remaining_hours"] + hours, 2)

        if settlement:
            hourly_rate = float(settlement["hourly_rate"])
            amount_diff = round(-hours * hourly_rate, 2)
            hours_diff = -hours
            adjustment = build_adjustment(
                teacher_id=teacher_id,
                month=month,
                attendance_id=attendance_id,
                hours_diff=hours_diff,
                amount_diff=amount_diff,
                reason=f"结算后撤销签到：{record['course_name']}（{record['checked_at']}）",
            )
            data["payroll_adjustments"].append(adjustment)
            target_record["adjustment_created"] = True
            target_record["adjustment_amount"] = amount_diff

        return data

    mutate(do_revoke_and_adjustment)

    record["revoked"] = True
    record["revoked_at"] = date.today().isoformat()
    if settlement:
        hourly_rate = float(settlement["hourly_rate"])
        record["adjustment_created"] = True
        record["adjustment_amount"] = round(-hours * hourly_rate, 2)
    return record


def _with_names(record, students, teachers):
    student = students.get(record["student_id"], {})
    teacher = teachers.get(record["teacher_id"], {})
    result = {
        **record,
        "student_name": student.get("name", "未知学员"),
        "teacher_name": teacher.get("name", "未知教师"),
    }
    month = record["checked_at"][:7]
    settlement = get_settlement(record["teacher_id"], month)
    result["month_is_settled"] = settlement is not None
    return result
