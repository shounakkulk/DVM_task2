import time
import uuid
import logging

logger = logging.getLogger(__name__)

class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        request_id = str(uuid.uuid4())
        request.request_id = request_id

        start_time = time.time()

        logger.info(
            "REQUEST START | ID=%s | Method=%s | Path=%s | User=%s", request_id, request.method, request.path, request.user if request.user.is_authenticated else "Anonymous",
        )


        try:
            response = self.get_response(request)

            duration = (time.time() - start_time) * 1000

            response["X-Request-ID"] = request_id

            logger.info(
                "REQUEST END | ID=%s | Status=%s | Duration=%.2f ms", request_id, response.status_code, duration,
            )

            return response

        except Exception:
            duration = (time.time() - start_time) * 1000

            logger.exception(
                "REQUEST FAILED | ID=%s | Duration=%.2f ms", request_id, duration,
            )

            raise

        # Code to be executed for each request/response after
        # the view is called.
