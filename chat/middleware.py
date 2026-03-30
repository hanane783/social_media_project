import jwt
from django.conf import settings
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async
from accounts.models import User


class JWTAuthMiddleware(BaseMiddleware):

    async def call(self, scope, receive, send):
        query_string = scope["query_string"].decode()

        token = None

        if "token=" in query_string:
            token = query_string.split("token=")[-1]

        if token:
            try:
                decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user = await sync_to_async(User.objects.get)(id=decoded["user_id"])
                scope["user"] = user
            except:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().call(scope, receive, send)