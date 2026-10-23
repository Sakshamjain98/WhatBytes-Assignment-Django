import uuid

from django.conf import settings
from django.http import JsonResponse

from .exceptions import error_body
from .log import request_id


class RequestIDMiddleware:
    """Tags each request with X-Request-Id (reused from the client if sent) and puts it in every log line."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        rid = request.headers.get("X-Request-Id") or uuid.uuid4().hex
        token = request_id.set(rid)
        try:
            response = self.get_response(request)
        finally:
            request_id.reset(token)
        response["X-Request-Id"] = rid
        return response


class BodySizeLimitMiddleware:
    """413 for bodies over DATA_UPLOAD_MAX_MEMORY_SIZE.

    Django only enforces that limit for form data; DRF's JSON parser reads the raw stream.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            length = int(request.META.get("CONTENT_LENGTH") or 0)
        except ValueError:
            length = 0
        # shortcut: trusts Content-Length; chunked uploads without it are left to the reverse proxy's body limit
        if length > settings.DATA_UPLOAD_MAX_MEMORY_SIZE:
            return JsonResponse(error_body(413, "Request body is too large."), status=413)
        return self.get_response(request)
