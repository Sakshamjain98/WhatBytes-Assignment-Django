import logging

from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    """DRF's handler for known errors; JSON (not an HTML page) for anything it doesn't handle."""
    response = exception_handler(exc, context)
    if response is not None:
        return response
    if isinstance(exc, IntegrityError):
        return Response({"detail": "This record conflicts with an existing one."}, status=status.HTTP_409_CONFLICT)
    logger.exception("Unhandled API error", exc_info=exc)
    return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
