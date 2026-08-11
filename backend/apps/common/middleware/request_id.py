import uuid

REQUEST_ID_HEADER = "HTTP_X_REQUEST_ID"
RESPONSE_REQUEST_ID_HEADER = "X-Request-ID"


class RequestIdMiddleware:
    """
    Ensures every request has a request_id for structured logs and Celery tasks.

    Accepts inbound X-Request-ID or generates a UUID4.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.META.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        request.request_id = request_id

        response = self.get_response(request)
        response[RESPONSE_REQUEST_ID_HEADER] = request_id
        return response
