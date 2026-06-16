import copy
import json
import os
from datetime import date
from threading import Lock
from uuid import uuid4

from .config import DATA_FILE

_lock = Lock()


def _default_data():
    today = date.today().isoformat()
    return {
        "students": [
            {
                "id": "stu-001",
                "name": "林小满",
                "guardian": "林女士",
                "phone": "13800010001",
                "course": "少儿编程",
                "remaining_hours": 6,
                "status": "active",
            },
            {
                "id": "stu-002",
                "name": "周一诺",
                "guardian": "周先生",
                "phone": "13800010002",
                "course": "创意美术",
                "remaining_hours": 3,
                "status": "active",
            },
            {
                "id": "stu-003",
                "name": "陈安安",
                "guardian": "陈女士",
                "phone": "13800010003",
                "course": "英语启蒙",
                "remaining_hours": 10,
                "status": "active",
            },
        ],
        "teachers": [
            {"id": "tea-001", "name": "王老师", "subject": "少儿编程", "hourly_rate": 120},
            {"id": "tea-002", "name": "赵老师", "subject": "创意美术", "hourly_rate": 100},
            {"id": "tea-003", "name": "刘老师", "subject": "英语启蒙", "hourly_rate": 110},
        ],
        "attendance": [
            {
                "id": "att-001",
                "student_id": "stu-001",
                "teacher_id": "tea-001",
                "course_name": "少儿编程",
                "hours": 2,
                "checked_at": today,
                "note": "Scratch 项目课",
            },
            {
                "id": "att-002",
                "student_id": "stu-002",
                "teacher_id": "tea-002",
                "course_name": "创意美术",
                "hours": 1,
                "checked_at": today,
                "note": "色彩练习",
            },
        ],
        "payroll_settlements": [],
    }


def _ensure_file():
    if os.path.exists(DATA_FILE):
        return

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(_default_data(), file, ensure_ascii=False, indent=2)


def read_data():
    with _lock:
        _ensure_file()
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)


def write_data(data):
    with _lock:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)


def mutate(mutator):
    data = read_data()
    updated = mutator(copy.deepcopy(data))
    write_data(updated)
    return updated


def new_id(prefix):
    return f"{prefix}-{uuid4().hex[:8]}"
