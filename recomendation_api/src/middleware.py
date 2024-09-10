import json
import logging

from fastapi.responses import ORJSONResponse
from fastapi import Request
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from core import config

settings = config.get_settings()


class BeforeRequest(BaseHTTPMiddleware):
    """Middleware для проверки наличия заголовка X-Request-Id в запросе."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        request_id = request.headers.get('X-Request-Id')
        if not request_id and not settings.debug:
            return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                  content={'detail': 'X-Request-Id is required'})
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования запросов и ответов."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method in ['POST', 'PUT', 'PATCH'] and 'auth' not in request.url.path:
            body = await request.body()
            try:
                json_body = json.loads(body.decode("utf-8"))
                logging.info(
                    f'method: {request.method}; '
                    f'url: {request.url}; '
                    f'body: {json_body}; '
                    f'headers: {request.headers};'
                )
            except json.JSONDecodeError:
                logging.info(
                    f'method: {request.method}; '
                    f'url: {request.url}; '
                    f'body: Received non-JSON body; '
                    f'headers: {request.headers};'
                )
        else:
            logging.info(
                f'method: {request.method}; '
                f'url: {request.url}; '
                f'headers: {request.headers};'
            )

        try:
            response = await call_next(request)
        except Exception as e:
            logging.error(f"Error processing request: {str(e)}")
            return Response("Internal server error", status_code=500)

        logging.info(f'Response: {response.status_code}')
        return response
