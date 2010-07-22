from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('cannonball.repo.views',
    # [project]/tree/[commmit-sha]/path-to-file/
    # [project]/blob/[commit-sha]/path-to-file/
    # [project]/commit/[commit-sha]/ 
    # [project]/tag/
    
    # [project]/[sha]/[path]

    url(r'commit/(?P<sha>[\w-]+)/', 'list_commit', name='repo-list-commit'),    
    url(r'(?P<sha>[\w-]+)/(?P<path>.*)', 'walk_path', name='repo-walk-path'),
    url(r'^$', 'list_commits', name='repo-list-commits'), 

)
