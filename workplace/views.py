import aiohttp_jinja2
from aiohttp import web
from aiohttp_session import get_session
from aioauth_client import GoogleClient
from psycopg2._psycopg import IntegrityError

from . import models


async def index(request):
    if not request.displayName:
        return web.Response(text='Login required.')
    return web.Response(text='{} - {} - {}'.format(request.id, request.displayName, request.email))


async def oauth_login(request):
    client = GoogleClient(
        client_id=request.app.config.OAUTH_ID,
        client_secret=request.app.config.OAUTH_SECRET
    )
    if 'code' not in request.GET:
        return web.HTTPFound(client.get_authorize_url(
            redirect_uri=request.app.config.REDIRECT_URI,
            scope='email profile'
        ))
    token, data = await client.get_access_token(
        request.GET['code'],
        redirect_uri=request.app.config.REDIRECT_URI
    )
    session = await get_session(request)
    session['token'] = token

    return web.HTTPFound(request.app.router['oauth:complete'].url_for())


async def oauth_complete(request):
    session = await get_session(request=request)
    if session['token'] is None:
        return web.HTTPFound(request.app.router['oauth:login'].url_for())

    client = GoogleClient(
        client_id=request.app.config.OAUTH_ID,
        client_secret=request.app.config.OAUTH_SECRET,
        access_token=session['token']
    )
    user, info = await client.user_info()
    google_id = info['id']
    display_name = info['displayName']
    email = info['emails'][0]['value']

    async with request.app.db.acquire() as conn:
        try:
            await conn.execute(models.UserGoogle.__table__.insert().values(google_id=google_id,
                                                                           google_user=display_name,
                                                                           google_email=email))
        except IntegrityError:
            await conn.execute(models.UserGoogle.__table__.update().
                               where(models.UserGoogle.__table__.c.google_email == email).
                               values(google_id=google_id,
                                      google_user=display_name,
                                      google_email=email))

    session['display_name'] = display_name
    session['google_id'] = google_id
    session['email'] = email
    return web.HTTPFound(request.app.router['index'].url_for())


@aiohttp_jinja2.template('index_test.html')
async def index_test(request):
    if not request.user:
        return {'user_id': 'empty'}
    return {'user_id': request.user}


@aiohttp_jinja2.template('test_login.html')
async def test_login(request):
    return {'user_id': 'and'}
 