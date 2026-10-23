from django.db import connection
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from .exceptions import error_body


@extend_schema(summary="Health check (includes database status)", responses={200: dict, 503: dict})
@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def health(request):
    try:
        connection.ensure_connection()
    except Exception:
        return Response({"status": "error", "database": "down"}, status=503)
    return Response({"status": "ok", "database": "up"})


# Django's own 404/500 pages (unknown routes, crashes outside DRF) as JSON. Only used when DEBUG=False.
def not_found(request, exception=None):
    return JsonResponse(error_body(404, f"Route {request.method} {request.path} not found"), status=404)


def server_error(request):
    return JsonResponse(error_body(500, "Internal server error."), status=500)
