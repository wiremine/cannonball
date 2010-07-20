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
from pygments.lexers import DiffLexer

from cannonball.patch import unified_diff, write_blob_diff, lines
from cannonball.utils import get_differing_files, file_contents

def list_commits(request):
    repo = Repo('/Users/briant/Desktop/joniandfriends_org')
    head = repo.head()
    commits = repo.revision_history(head)

    return render_to_response('repo/commits.html', {
        'commits': commits
    }, context_instance=RequestContext(request))

    
def list_object(request, sha):
    repo = Repo('/Users/briant/Desktop/joniandfriends_org')
    repo_obj = repo.get_object(sha)
    
    if repo_obj.type_name == "commit":
        return list_commit(request, repo, repo_obj)
    elif repo_obj.type_name == 'tree':
        return list_tree(request, repo, repo_obj)
    elif repo_obj.type_name == 'blob': 
        return list_blob(request, repo, repo_obj)


def list_commit(request, repo, commit_obj):
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
        #highlighted_diff = highlight(output.getvalue(), DiffLexer(), HtmlFormatter())
        highlighted_diff = htmldiff.make_table(lines(a), lines(b))
        
        diffs.append(highlighted_diff)
        files.append(f)
    
    css = HtmlFormatter().get_style_defs('.highlight')
    
    return render_to_response('repo/object.html', {
        'object': commit_obj,
        'files': files, 
        'diffs': diffs,
        'css': css
    }, context_instance=RequestContext(request))        

    
def list_tree(request, repo, tree_obj):
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
    
def list_blob(request, repo, blob_obj):
    print type(tree_obj)
    return render_to_response('repo/blog.html', {
        'blob': blob_obj
    }, context_instance=RequestContext(request))
    
    
    
    
    
    
    
    
    