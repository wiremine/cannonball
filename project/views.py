from StringIO import StringIO
from difflib import HtmlDiff
from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_list_or_404, get_object_or_404
from django.template import RequestContext
from django.views.generic.list_detail import object_list, object_detail
from django.core.urlresolvers import reverse

from dulwich.repo import Repo
from dulwich import objects

from pygments import highlight
from pygments.lexers import DiffLexer, guess_lexer, guess_lexer_for_filename
from pygments.formatters import HtmlFormatter

from cannonball.patch import unified_diff, write_blob_diff, lines
from cannonball.project.models import Project
from cannonball.utils import get_differing_files, file_contents, list_path, generate_breadcrumbs

def _get_repo(project_slug):
    project = get_object_or_404(Project, slug=project_slug)
    try:
        return [Repo(project.path_to_repo), project]
    except:
        raise Http404


def project_list(request):
    """List all the projects configured in this repo"""
    return object_list(
        request,
        queryset=Project.objects.all(),
        template_object_name='project'
    )


def project_detail(request, project_slug):
    """Show commits for this project."""
    repo, project = _get_repo(project_slug)

    try:
        repo = Repo(project.path_to_repo)
    except:
        return HttpResponse("Invalid repo path %s" % project.path_to_repo)
        
    commits = repo.revision_history(repo.head())
 
    branches = repo.refs.as_dict('refs/heads').keys()
 
    return render_to_response('project/project_detail.html', {
        'project': project,
        'commits': commits,
        'branches': branches,
    }, context_instance=RequestContext(request))
 
 
def commit_detail(request, project_slug, commit_sha):
    """Show details of a commit."""
    repo, project = _get_repo(project_slug)
    commit_obj = repo[commit_sha]

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

    return render_to_response('project/commit_detail.html', {
        'project': project,
        'object': commit_obj,
        'files': files, 
        'diffs': diffs,
        'css': css
    }, context_instance=RequestContext(request)) 
            
def walk_path(request, project_slug, branch_or_sha, path=None):
    """Lists the files and folders for a tree of a commit attached to the branch"""
    repo, project = _get_repo(project_slug)

    # Pick the right branch, trying to default to 'master' or whatever the first head is
    branches = repo.refs.as_dict('refs/heads')

    try:
        if branch_or_sha in branches.keys():
            commit = repo[branches[branch_or_sha]]
        else:
            commit = repo[branch_or_sha]
    except:
        return HttpResponseRedirect(reverse('project-detail', args=[project.slug]))

    # Get the object and it's related path
    try:
        [git_object, path_list] = list_path(repo, commit, path)
    except:
        raise Http404

    if git_object.type_name == 'tree':
        return _tree_detail(request, project, branch_or_sha, git_object, path_list, branches)
    elif git_object.type_name == 'blob':
        return _blob_detail(request, project, branch_or_sha, git_object, path_list, branches)


def _tree_detail(request, project, branch_name, git_object, path_list, branches):
    """Render a tree."""
    breadcrumbs = generate_breadcrumbs(path_list)
    return render_to_response('project/tree.html', {
        'project': project,
        'branch_name': branch_name,
        'object': git_object,
        'path': path_list,
        'breadcrumbs': breadcrumbs,
        'branches': branches,
    }, context_instance=RequestContext(request))    
    
    
def _blob_detail(request, project, branch_name, git_object, path_list, branches):
    """Render a blob. Pretty prints using Pygments"""
    breadcrumbs = generate_breadcrumbs(path_list)
    
    file_name = path_list[-1]['name']
    try:
        lexer = guess_lexer_for_filename(file_name, git_object.as_raw_string())
    except:
        lexer = guess_lexer(git_object.as_raw_string())
    formatter = HtmlFormatter(linenos=True)
    pretty_printed_file = highlight(git_object.as_raw_string(), lexer, formatter)
    
    return render_to_response('project/blob.html', {
        'project': project,
        'branch_name': branch_name,
        'object': git_object,
        'path': path_list,
        'breadcrumbs': breadcrumbs,
        'pretty_print': pretty_printed_file,
        'branches': branches,
    }, context_instance=RequestContext(request))
    
    
    
    
    