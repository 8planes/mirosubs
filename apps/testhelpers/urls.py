from django.conf.urls.defaults import  patterns, url

urlpatterns = patterns('testhelpers.views',
    url(r'^load-teams-fixture/$', 'load_team_fixtures', name='load_team_fixture'),

)
