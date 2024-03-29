from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

def api_error_response(status_code, message=None):
    """Provide error codes for non-browser API usage."""

    payload = {"error": HTTP_STATUS_CODES.get(status_code, "Unknown error")}
    if message:
        payload["message"] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


def bad_request(message):
    return api_error_response(400, message)