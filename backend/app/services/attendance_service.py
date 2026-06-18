from datetime import date

from .validation import require_fields
from .payroll_service import get_settlement, build_adjustment
from ..storage import mutate, new_id, read_data


def list_attendance():
    data = read_data()
    students = {student["id"]: student for student in data["students"]}
    teachers = {teacher["id"]: teacher for teacher in data["teachers"]}
    return [_with_names(record, students, teachers) for record in sorted(data["attendance"], key=lambda item: item["checked_at"], reverse=True)]


def _find_settlement_in_data(data, teacher_id, month):
    return next(
        (s for s in data["payroll_settlements"] if s["teacher_id"] == teacher_id and s["month"] == month and s["status"] == "settled"),
        None,
    )


def check_in(payload):
    require_fields(payload, ["student_id", "teacher_id", "course_name", "hours"])
    hours = float(payload["hours"])
    if hours <= 0:
        raise ValueError("课时必须大于 0")

    checked_at = payload.get("checked_at") or date.today().isoformat()
    month = checked_at[:7]
    teacher_id = payload["teacher_id"]

    attendance_id = new_id("att")
    course_name = payload["course_name"].strip()
    note = payload.get("note", "").strip()
    student_id = payload["student_id"]

    adjustment_created = [False]
    adjustment_amount = [0.0]

    def add_record_and_adjustment(data):
        student = next((item for item in data["students"] if item["id"] == student_id), None)
        teacher = next((item for item in data["teachers"] if item["id"] == teacher_id), None)
        if not student:
            raise ValueError("学员不存在")
        if not teacher:
            raise ValueError("教师不存在")
        if student["remaining_hours"] < hours:
            raise ValueError("学员剩余课时不足")

        student["remaining_hours"] = round(student["remaining_hours"] - hours, 2)

        attendance_record = {
            "id": attendance_id,
            "student_id": student_id,
            "teacher_id": teacher_id,
            "course_name": course_name,
            "hours": hours,
            "checked_at": checked_at,
            "note": note,
            "revoked": False,
            "revoked_at": None,
        }
        data["attendance"].append(attendance_record)

        settlement = _find_settlement_in_data(data, teacher_id, month)
        if settlement:
            hourly_rate = float(settlement["hourly_rate"])
            amt = round(hours * hourly_rate, 2)
            adjustment = build_adjustment(
                teacher_id=teacher_id,
                month=month,
                attendance_id=attendance_id,
                hours_diff=hours,
                amount_diff=amt,
                reason=f"结算后新增签到：{course_name}（{checked_at}）",
            )
            data["payroll_adjustments"].append(adjustment)
            attendance_record["adjustment_created"] = True
            attendance_record["adjustment_amount"] = amt
            adjustment_created[0] = True
            adjustment_amount[0] = amt

        return data

    mutate(add_record_and_adjustment)

    result = {
        "id": attendance_id,
        "student_id": student_id,
        "teacher_id": teacher_id,
        "course_name": course_name,
        "hours": hours,
        "checked_at": checked_at,
        "note": note,
        "revoked": False,
        "revoked_at": None,
    }
    if adjustment_created[0]:
        result["adjustment_created"] = True
        result["adjustment_amount"] = adjustment_amount[0]
    return result


def revoke_attendance(attendance_id, payload=None):
    payload = payload or {}
    reason = payload.get("reason", "").strip()

    adjustment_created = [False]
    adjustment_amount = [0.0]

    def do_revoke_and_adjustment(data):
        target_record = next((r for r in data["attendance"] if r["id"] == attendance_id), None)
        if not target_record:
            raise ValueError("签到记录不存在")
        if target_record.get("revoked"):
            raise ValueError("该签到记录已被撤销")

        student = next((s for s in data["students"] if s["id"] == target_record["student_id"]), None)
        hours = float(target_record["hours"])
        month = target_record["checked_at"][:7]
        teacher_id = target_record["teacher_id"]

        target_record["revoked"] = True
        target_record["revoked_at"] = date.today().isoformat()
        target_record["revoke_reason"] = reason

        if student:
            student["remaining_hours"] = round(student["remaining_hours"] + hours, 2)

        settlement = _find_settlement_in_data(data, teacher_id, month)
        if settlement:
            hourly_rate = float(settlement["hourly_rate"])
            amt = round(-hours * hourly_rate, 2)
            hrs = -hours
            adjustment = build_adjustment(
                teacher_id=teacher_id,
                month=month,
                attendance_id=attendance_id,
                hours_diff=hrs,
                amount_diff=amt,
                reason=f"结算后撤销签到：{target_record['course_name']}（{target_record['checked_at']}）",
            )
            data["payroll_adjustments"].append(adjustment)
            target_record["adjustment_created"] = True
            target_record["adjustment_amount"] = amt
            adjustment_created[0] = True
            adjustment_amount[0] = amt

        return data

    mutate(do_revoke_and_adjustment)

    data = read_data()
    record = next((r for r in data["attendance"] if r["id"] == attendance_id), None)
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
