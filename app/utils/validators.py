from marshmallow import ValidationError
from functools import wraps
from flask import request, jsonify

def validate_request(schema):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                validated_data = schema().load(request.get_json() or {})
                request.validated_data = validated_data
                return f(*args, **kwargs)
            except ValidationError as err:
                return jsonify({"error": "Validation failed", "details": err.messages}), 400
        return wrapper
    return decorator