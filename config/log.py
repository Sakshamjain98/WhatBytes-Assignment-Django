import contextvars
import logging

# Set per request by config.middleware.RequestIDMiddleware. Kept apart from the middleware because
# LOGGING loads this module before Django (and DRF) are ready.
request_id = contextvars.ContextVar("request_id", default="-")


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id.get()
        return True
