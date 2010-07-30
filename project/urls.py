from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('cannonball.project.views',
    
    url(r'(?P<project_slug>[\w-]+)/view/(?P<branch_or_sha>[\w-]+)/(?P<path>.*)', 'walk_path', name='project-path'),
    url(r'(?P<project_slug>[\w-]+)/commit/(?P<commit_sha>[a-f0-9]{40})/$', 'commit_detail', name='commit-detail'),
    url(r'(?P<project_slug>[\w-]+)/$', 'project_detail', name='project-detail'),
    url(r'^$', 'project_list', name='project-list'), 
)
