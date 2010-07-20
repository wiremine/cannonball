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