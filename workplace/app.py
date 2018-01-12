import base64
import aiohttp_jinja2
import jinja2

from aiohttp import web
from aiohttp.web import middleware
from aiohttp_session import get_session, setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aioauth_client import GoogleClient

from . import models, redis, routes, settings


@middleware
async def user_middleware(request, handler):
    session = await get_session(request=request)
    request.user = None
    request.info = None

    if 'display_name' in session:
        request.id = session['google_id']
        request.displayName = session['display_name']
        request.email = session['email']
    else:
        return web.HTTPFound(request.app.config.OAUTH_REDIRECT_PATH)
    response = await handler(request)
    return response


async def close_redis(app):
    app.redis.close()
    await app.redis.wait_closed()


async def build_application():
    app = web.Application()

    setup(app=app, storage=EncryptedCookieStorage(
        secret_key=base64.urlsafe_b64decode(settings.SECRET_KEY)))
    app.middlewares.append(user_middleware)

    app.config = settings
    aiohttp_jinja2.setup(app=app, loader=jinja2.PackageLoader('workplace', 'templates'))

    await models.setup(app)
    app.on_cleanup.append(models.close)

    await redis.setup(app)
    app.on_shutdown.append(redis.close)

    await routes.setup(app)

    return app
