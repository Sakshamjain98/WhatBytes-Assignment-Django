import logging

from django.core.exceptions import RequestDataTooBig
from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

ERROR_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    406: "NOT_ACCEPTABLE",
    409: "CONFLICT",
    413: "PAYLOAD_TOO_LARGE",
    415: "UNSUPPORTED_MEDIA_TYPE",
    429: "TOO_MANY_REQUESTS",
    500: "INTERNAL_ERROR",
}


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "This record conflicts with an existing one."
    default_code = "conflict"


def error_body(status_code, message, details=None, code=None):
    """Every error response has the shape {"error": {"code", "message", "details"?}}."""
    error = {"code": code or ERROR_CODES.get(status_code, "ERROR"), "message": message}
    if details:
        error["details"] = details
    return {"error": error}


def _flatten(detail, field=""):
    """Turn DRF's nested validation errors into [{"field": "a.b", "message": "..."}]."""
    if isinstance(detail, dict):
        for key, value in detail.items():
            name = "" if key == api_settings.NON_FIELD_ERRORS_KEY else str(key)
            yield from _flatten(value, ".".join(p for p in (field, name) if p))
    elif isinstance(detail, list):
        for i, value in enumerate(detail):
            nested = isinstance(value, (dict, list))
            yield from _flatten(value, ".".join(p for p in (field, str(i)) if p) if nested else field)
    else:
        yield {"field": field or None, "message": str(detail)}


def api_exception_handler(exc, context):
    """DRF's handler for known errors, reshaped to the common error body; JSON 500 for anything else."""
    if isinstance(exc, RequestDataTooBig):
        return Response(error_body(413, "Request body is too large."), status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
    response = exception_handler(exc, context)
    if response is not None:
        if isinstance(exc, ValidationError):
            response.data = error_body(400, "Validation failed", list(_flatten(exc.detail)), code="VALIDATION_ERROR")
        else:
            detail = response.data.get("detail", response.data) if isinstance(response.data, dict) else response.data
            response.data = error_body(response.status_code, str(detail))
        return response
    if isinstance(exc, IntegrityError):
        return Response(error_body(409, Conflict.default_detail), status=status.HTTP_409_CONFLICT)
    logger.exception("Unhandled API error", exc_info=exc)
    return Response(error_body(500, "Internal server error."), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
