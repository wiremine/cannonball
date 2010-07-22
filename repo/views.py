from StringIO import StringIO
from difflib import HtmlDiff

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_list_or_404, get_object_or_404
from django.template import RequestContext
from django.views.generic.list_detail import object_list, object_detail

from dulwich.repo import Repo
from dulwich import objects

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import DiffLexer, guess_lexer, guess_lexer_for_filename, PythonLexer

from cannonball.patch import unified_diff, write_blob_diff, lines
from cannonball.utils import get_differing_files, file_contents, list_path

def list_commits(request):
    repo = Repo('/Users/briant/Desktop/joniandfriends_org')
    head = repo.head()
    commits = repo.revision_history(head)
    
    # TODO: cache commits in db, so we can paginate 
    # TODO: get branch
    
    # Gets heads
    print repo.refs.as_dict('refs/heads')

    # Gets tags
    print repo.refs.as_dict('refs/tags')

    return render_to_response('repo/commit_list.html', {
        'commits': commits
    }, context_instance=RequestContext(request))


def list_commit(request, sha=None):
    repo = Repo('/Users/briant/Desktop/joniandfriends_org')
    commit_obj = repo[sha or repo.head()]
    
    parent_obj = repo.get_object(commit_obj.parents[0])
    parent_tree = repo.get_object(parent_obj.tree)
    current_tree = repo.get_object(commit_obj.tree)

    htmldiff = HtmlDiff()

    files = []
    diffs = []
    for f in get_differing_files(repo, parent_tree, current_tree):
        a = file_contents(repo, f, parent_obj)
        b = file_contents(repo, f, commit_obj)

        output = StringIO()
        write_blob_diff(output, 
            (f, 775, a), (f, 775, b)
        )
        highlighted_diff = highlight(output.getvalue(), DiffLexer(), HtmlFormatter(linenos=True))

        diffs.append(highlighted_diff)
        files.append(f)

    css = HtmlFormatter().get_style_defs('.highlight')

    return render_to_response('repo/commit_detail.html', {
        'object': commit_obj,
        'files': files, 
        'diffs': diffs,
        'css': css
    }, context_instance=RequestContext(request))
    
    
def _generate_breadcrumbs(path_objects):
    """Generate a list of breacrumbs using the given path_objects dict."""
    # radio/migrations/blahblah.py
    # radio = radio
    # migrations = radio/migrations
    # blahblah.py = []
    crumbs = []
    for i in range(0,len(path_objects)):
        path_name = path_objects[i]['name']
        path = []
        for j in range(0,i+1):
            path.append(path_objects[j]['name'])
        crumbs.append({'name': path_name, 'path': "/".join(path)})
    return crumbs

def walk_path(request, sha=None, path=None):
    repo = Repo('/Users/briant/Desktop/joniandfriends_org')
    [git_object, path_list] = list_path(repo, sha, path)
    breadcrumbs = _generate_breadcrumbs(path_list)
    return render_to_response('repo/%s.html' % git_object.type_name, {
        'object': git_object,
        'path': path_list,
        'breadcrumbs': breadcrumbs,
        'sha': sha
    }, context_instance=RequestContext(request))       


# commmit-sha/path
def list_tree(request, repo, tree_obj, path):
    print path
    
    files = []
    folders = []
    for mode, name, sha in tree_obj.entries():
        if isinstance(repo.get_object(sha), objects.Tree):
            folders.append(name)
        if isinstance(repo.get_object(sha), objects.Blob):
            files.append(name)

    return render_to_response('repo/tree.html', {
        'tree': tree_obj,
        'files': files,
        'folders': folders
    }, context_instance=RequestContext(request))    
    
    
def list_blob(request, repo, blob_obj, path):
    print path 
    
    blob_text = blob_obj.as_pretty_string()
    
    lexer = guess_lexer(blob_text)
    highlighted_text = highlight(blob_text, PythonLexer(), HtmlFormatter())    
    
    css = HtmlFormatter().get_style_defs('.highlight')
    
    return render_to_response('repo/blob.html', {
        'blob': blob_obj,
        'highlighted_text': highlighted_text,
        'css': css,
    }, context_instance=RequestContext(request))
    
    
    
    
    
    
    
    
    