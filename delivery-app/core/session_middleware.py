from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
import uuid
import json

SESSION_PREFIX = "session:"
SESSION_TTL = 3600


class SessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        redis = request.app.state.redis_client
        if not redis:
            raise RuntimeError("Redis client is not initialized")

        session_id = request.cookies.get("session_id")
        if not session_id:
            session_id = str(uuid.uuid4())
            response = Response()
            response.set_cookie(key="session_id", value=session_id, httponly=True)

        session_key = f"{SESSION_PREFIX}{session_id}"
        if not await redis.exists(session_key):
            await redis.set(session_key, json.dumps({}), ex=SESSION_TTL)

        request.state.session_id = session_id

        response = await call_next(request)
        return response
