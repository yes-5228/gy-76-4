from .validation import require_fields
from ..storage import mutate, new_id, read_data


def list_teachers():
    return read_data()["teachers"]


def create_teacher(payload):
    require_fields(payload, ["name", "subject", "hourly_rate"])
    teacher = {
        "id": new_id("tea"),
        "name": payload["name"].strip(),
        "subject": payload["subject"].strip(),
        "hourly_rate": float(payload["hourly_rate"]),
    }

    def add(data):
        data["teachers"].append(teacher)
        return data

    mutate(add)
    return teacher
