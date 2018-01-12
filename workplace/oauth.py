import asyncio

from aioauth_client import OAuth2Client
from aiohttp import web
from lxml import etree
from urllib.parse import urlencode, parse_qsl


class GoogleClient(OAuth2Client):

    """Support Google.

    * Dashboard: https://console.developers.google.com/project
    * Docs: https://developers.google.com/accounts/docs/OAuth2
    * API reference: https://developers.google.com/gdata/docs/directory
    * API explorer: https://developers.google.com/oauthplayground/
    """

    access_token_url = 'https://accounts.google.com/o/oauth2/token'
    authorize_url = 'https://accounts.google.com/o/oauth2/auth'
    base_url = 'https://www.googleapis.com/plus/v1/'
    name = 'google'
    user_info_url = 'https://www.googleapis.com/plus/v1/people/me'

    async def user_info(self, loop=None, **kwargs):
        """Load user information from provider."""
        if not self.user_info_url:
            raise NotImplementedError('The provider doesnt support user_info method.')

        response = await self.request('GET', self.user_info_url, loop=loop, **kwargs)
        if response.status / 100 > 2:
            raise web.HTTPBadRequest(
                reason='Failed to obtain User information. HTTP status code: %s' %
                       response.status)
        data = await response.read()
        user = dict(self.user_parse(data))
        return user, data

    @staticmethod
    def user_parse(data):
        """Parse information from provider."""
        yield 'id', data.get('sub') or data.get('id')
        yield 'username', data.get('nickname')
        yield 'first_name', data.get('name', {}).get('givenName')
        yield 'last_name', data.get('name', {}).get('familyName')
        yield 'locale', data.get('language')
        yield 'link', data.get('url')
        yield 'picture', data.get('image', {}).get('url')
        for email in data.get('emails', []):
            if email['type'] == 'account':
                yield 'email', email['value']


class FacebookClient(OAuth2Client):

    """Support Facebook.

    * Dashboard: https://developers.facebook.com/apps
    * Docs: http://developers.facebook.com/docs/howtos/login/server-side-login/
    * API reference: http://developers.facebook.com/docs/reference/api/
    * API explorer: http://developers.facebook.com/tools/explorer
    """

    access_token_url = 'https://graph.facebook.com/oauth/access_token'
    authorize_url = 'https://www.facebook.com/v2.11/dialog/oauth'
    base_url = 'https://graph.facebook.com/v2.11'
    name = 'facebook'
    user_info_url = 'https://graph.facebook.com/me'
    redirect_uri = 'http://localhost:8080/'

    def get_authorize_url(self, **params):
        """Return formatted authorize URL."""
        # params = super(InstagramClient, self).get_authorize_url(**params)
        params = dict(self.params, **params)
        params.update({'client_id': self.client_id, 'redirect_uri': self.redirect_uri, 'response_type': 'code'})
        # params.update({'client_id': self.client_id, 'redirect_uri': self.redirect_uri, 'response_type': 'token'})
        return self.authorize_url + '?' + urlencode(params)

    async def user_info(self, params=None, **kwargs):
        """Facebook required fields-param."""
        params = params or {}
        params['fields'] = 'id,email,first_name,last_name,name,link,locale,gender,location'
        return await super(FacebookClient, self).user_info(params=params, **kwargs)

    @staticmethod
    def user_parse(data):
        """Parse information from provider."""
        id_ = data.get('id')
        yield 'id', id_
        yield 'email', data.get('email')
        yield 'first_name', data.get('first_name')
        yield 'last_name', data.get('last_name')
        yield 'username', data.get('name')
        yield 'picture', 'http://graph.facebook.com/{0}/picture?type=large'.format(id_)
        yield 'link', data.get('link')
        yield 'locale', data.get('locale')
        yield 'gender', data.get('gender')

        location = data.get('location', {}).get('name')
        if location:
            split_location = location.split(', ')
            yield 'city', split_location[0].strip()
            if len(split_location) > 1:
                yield 'country', split_location[1].strip()


class InstagramClient(OAuth2Client):

    """Support Instagramm.

    * Dashboard: https://www.instagram.com/developer/clients/manage/
    * Docs: https://www.instagram.com/developer/authentication/
    * API reference: https://www.instagram.com/developer/
    """

    access_token_url = 'https://api.instagram.com/oauth/access_token'
    authorize_url = 'https://api.instagram.com/oauth/authorize'
    base_url = 'https://api.instagram.com/v1'
    name = 'instagram'
    user_info_url = 'https://api.instagram.com/v1/users/self'
    redirect_uri = 'http://localhost:8080/'

    def get_authorize_url(self, **params):
        """Return formatted authorize URL."""
        # params = super(InstagramClient, self).get_authorize_url(**params)
        params = dict(self.params, **params)
        params.update({'client_id': self.client_id, 'redirect_uri': self.redirect_uri, 'response_type': 'code'})
        # params.update({'client_id': self.client_id, 'redirect_uri': self.redirect_uri, 'response_type': 'token'})
        return self.authorize_url + '?' + urlencode(params)

    def get_user_id(self, details, response):
        # Sometimes Instagram returns 'user', sometimes 'data', but API docs
        # says 'data' http://instagram.com/developer/endpoints/users/#get_users
        user = response.get('user') or response.get('data') or {}
        return user.get('id')

    def get_user_details(self, response):
        """Return user details from Instagram account"""
        # Sometimes Instagram returns 'user', sometimes 'data', but API docs
        # says 'data' http://instagram.com/developer/endpoints/users/#get_users
        user = response.get('user') or response.get('data') or {}
        username = user['username']
        email = user.get('email', '')
        return {'username': username,
                'email': email}
