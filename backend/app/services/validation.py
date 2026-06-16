def require_fields(payload, fields):
    missing = [field for field in fields if payload.get(field) in (None, "")]
    if missing:
        raise ValueError(f"缺少必要字段: {', '.join(missing)}")
