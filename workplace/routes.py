from . import views


async def setup(app):
    app.router.add_get('/', views.index, name='index')
    app.router.add_get('/test', views.index_test, name='index:test')
    app.router.add_get('/test/login', views.test_login, name='test_login')
    app.router.add_get('/oauth/login', views.oauth_login, name='oauth:login')
    app.router.add_get('/oauth/complete', views.oauth_complete, name='oauth:complete')
