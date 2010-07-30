import os 

from dulwich import objects

# from http://github.com/alex/pyvcs/raw/master/pyvcs/backends/git.py
def get_differing_files(repo, past, current):
    past_files = {}
    current_files = {}
    if past is not None:
        past_files = dict([(name, sha) for mode, name, sha in past.entries()])
    if current is not None:
        current_files = dict([(name, sha) for mode, name, sha in current.entries()])

    added = set(current_files) - set(past_files)
    removed = set(past_files) - set(current_files)
    changed = [o for o in past_files if o in current_files and past_files[o] != current_files[o]]

    for name in added:
        sha = current_files[name]
        yield name
        if isinstance(repo.get_object(sha), objects.Tree):
            for item in get_differing_files(repo, None, repo.get_object(sha)):
                yield os.path.join(name, item)

    for name in removed:
        sha = past_files[name]
        yield name
        if isinstance(repo.get_object(sha), objects.Tree):
            for item in get_differing_files(repo, repo.get_object(sha), None):
                yield os.path.join(name, item)

    for name in changed:
        past_sha = past_files[name]
        current_sha = current_files[name]
        if isinstance(repo.get_object(past_sha), objects.Tree):
            for item in get_differing_files(repo, repo.get_object(past_sha), repo.get_object(current_sha)):
                yield os.path.join(name, item)
        else:
            yield name
            
            
def file_contents(repo, path, commit=None):
       tree = repo[commit.tree]
       path = path.split(os.path.sep)
       path, filename = path[:-1], path[-1]
       while path:
           part = path.pop(0)
           for mode, name, hexsha in repo[tree.id].entries():
               if part == name:
                   tree = repo[hexsha]
                   break
       for mode, name, hexsha in tree.entries():
           if name == filename:
               return repo.get_object(hexsha) #.as_pretty_string()
       return None
       
       
def list_path(repo, commit, path):
    """Return the tree or blob object for a given path and commit object"""
    tree = repo[commit.tree]
    path = path.split(os.path.sep)
    path_list = []
    should_be_leaf = False

    if path == [u'']:
        return [tree, path_list]

    while path:  
        # TODO: check should_be_leaf and throw an exception if it's true    
        current_part = path.pop(0)
        for entry_mode, entry_name, entry_sha in repo[tree.id].entries():
            if current_part == entry_name:
                current_obj = repo[entry_sha]
                if current_obj.type_name == 'tree':
                    path_list.append({'name': entry_name, 'sha': entry_sha})
                    tree = current_obj
                    break
                elif current_obj.type_name == 'blob':
                    path_list.append({'name': entry_name, 'sha': entry_sha})
                    should_be_leaf = True # if we hit an object, we should be at the end of th path
                    break
        
    return [current_obj, path_list]
                    
                    
def generate_breadcrumbs(path_objects):
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
        
    
    
    
    
       
       