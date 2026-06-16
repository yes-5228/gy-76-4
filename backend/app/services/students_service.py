from .validation import require_fields
from ..config import RENEWAL_THRESHOLD
from ..storage import mutate, new_id, read_data


def list_students():
    return read_data()["students"]


def create_student(payload):
    require_fields(payload, ["name", "guardian", "phone", "course"])
    remaining_hours = int(payload.get("remaining_hours", 0))
    student = {
        "id": new_id("stu"),
        "name": payload["name"].strip(),
        "guardian": payload["guardian"].strip(),
        "phone": payload["phone"].strip(),
        "course": payload["course"].strip(),
        "remaining_hours": max(0, remaining_hours),
        "status": payload.get("status", "active"),
    }

    def add(data):
        data["students"].append(student)
        return data

    mutate(add)
    return student


def get_renewal_reminders():
    students = read_data()["students"]
    return [
        {
            **student,
            "reason": "课时不足",
            "threshold": RENEWAL_THRESHOLD,
        }
        for student in students
        if student["status"] == "active" and student["remaining_hours"] <= RENEWAL_THRESHOLD
    ]
