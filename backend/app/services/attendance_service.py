from datetime import date

from .validation import require_fields
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

    attendance_record = {
        "id": new_id("att"),
        "student_id": payload["student_id"],
        "teacher_id": payload["teacher_id"],
        "course_name": payload["course_name"].strip(),
        "hours": hours,
        "checked_at": payload.get("checked_at") or date.today().isoformat(),
        "note": payload.get("note", "").strip(),
    }

    def add_record(data):
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
        return data

    mutate(add_record)
    return attendance_record


def _with_names(record, students, teachers):
    student = students.get(record["student_id"], {})
    teacher = teachers.get(record["teacher_id"], {})
    return {
        **record,
        "student_name": student.get("name", "未知学员"),
        "teacher_name": teacher.get("name", "未知教师"),
    }
