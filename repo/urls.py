from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('cannonball.repo.views',
    url(r'(?P<sha>[\w-]+)/', 'list_object', name='repo-show-object'),
    url(r'^$', 'list_commits', name='repo-list-commits'), 

)
