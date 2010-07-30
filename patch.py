# patch.py -- For dealing with packed-style patches.
# Copyright (C) 2009 Jelmer Vernooij <jelmer@samba.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; version 2
# of the License or (at your option) a later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.

"""Classes for dealing with git am-style patches.

These patches are basically unified diffs with some extra metadata tacked 
on.
"""

from difflib import SequenceMatcher
import rfc822
import subprocess
import time

from dulwich.objects import (
    Commit,
    )

def write_commit_patch(f, commit, contents, progress, version=None):
    """Write a individual file patch.

    :param commit: Commit object
    :param progress: Tuple with current patch number and total.
    :return: tuple with filename and contents
    """
    (num, total) = progress
    f.write("From %s %s\n" % (commit.id, time.ctime(commit.commit_time)))
    f.write("From: %s\n" % commit.author)
    f.write("Date: %s\n" % time.strftime("%a, %d %b %Y %H:%M:%S %Z"))
    f.write("Subject: [PATCH %d/%d] %s\n" % (num, total, commit.message))
    f.write("\n")
    f.write("---\n")
    try:
        p = subprocess.Popen(["diffstat"], stdout=subprocess.PIPE, 
                             stdin=subprocess.PIPE)
    except OSError, e:
        pass # diffstat not available?
    else:
        (diffstat, _) = p.communicate(contents)
        f.write(diffstat)
        f.write("\n")
    f.write(contents)
    f.write("-- \n")
    if version is None:
        from dulwich import __version__ as dulwich_version
        f.write("Dulwich %d.%d.%d\n" % dulwich_version)
    else:
        f.write("%s\n" % version)


def get_summary(commit):
    """Determine the summary line for use in a filename.
    
    :param commit: Commit
    :return: Summary string
    """
    return commit.message.splitlines()[0].replace(" ", "-")


def unified_diff(a, b, fromfile='', tofile='', n=3):
    """difflib.unified_diff that doesn't write any dates or trailing spaces.

    Based on the same function in Python2.6.5-rc2's difflib.py
    """
    started = False
    for group in SequenceMatcher(None, a, b).get_grouped_opcodes(n):
        if not started:
            yield '--- %s\n' % fromfile
            yield '+++ %s\n' % tofile
            started = True
        i1, i2, j1, j2 = group[0][1], group[-1][2], group[0][3], group[-1][4]
        yield "@@ -%d,%d +%d,%d @@\n" % (i1+1, i2-i1, j1+1, j2-j1)
        for tag, i1, i2, j1, j2 in group:
            if tag == 'equal':
                for line in a[i1:i2]:
                    yield ' ' + line
                continue
            if tag == 'replace' or tag == 'delete':
                for line in a[i1:i2]:
                    if not line[-1] == '\n':
                        line += '\n\\ No newline at end of file\n'
                    yield '-' + line
            if tag == 'replace' or tag == 'insert':
                for line in b[j1:j2]:
                    if not line[-1] == '\n':
                        line += '\n\\ No newline at end of file\n'
                    yield '+' + line


def lines(blob):
    if blob is not None:
        return blob.data.splitlines(True)
    else:
        return []

def write_blob_diff(f, (old_path, old_mode, old_blob), 
                       (new_path, new_mode, new_blob)):
    """Write diff file header.

    :param f: File-like object to write to
    :param (old_path, old_mode, old_blob): Previous file (None if nonexisting)
    :param (new_path, new_mode, new_blob): New file (None if nonexisting)
    """
    def blob_id(blob):
        if blob is None:
            return "0" * 7
        else:
            return blob.id[:7]

    if old_path is None:
        old_path = "/dev/null"
    else:
        old_path = "a/%s" % old_path
    if new_path is None:
        new_path = "/dev/null"
    else:
        new_path = "b/%s" % new_path
    f.write("diff --git %s %s\n" % (old_path, new_path))
    if old_mode != new_mode:
        if new_mode is not None:
            if old_mode is not None:
                f.write("old mode %o\n" % old_mode)
            f.write("new mode %o\n" % new_mode) 
        else:
            f.write("deleted mode %o\n" % old_mode)
    f.write("index %s..%s %o\n" % (
        blob_id(old_blob), blob_id(new_blob), new_mode))
    if old_blob and old_blob.type_name == 'blob':
        old_contents = lines(old_blob)
    else:
        old_contents = ""
    if new_blob and new_blob.type_name == 'blob':
        new_contents = lines(new_blob)
    else:
        new_contents = ""
    f.writelines(unified_diff(old_contents, new_contents, 
        old_path, new_path))


def git_am_patch_split(f):
    """Parse a git-am-style patch and split it up into bits.

    :param f: File-like object to parse
    :return: Tuple with commit object, diff contents and git version
    """
    msg = rfc822.Message(f)
    c = Commit()
    c.author = msg["from"]
    c.committer = msg["from"]
    if msg["subject"].startswith("[PATCH"):
        subject = msg["subject"].split("]", 1)[1][1:]
    else:
        subject = msg["subject"]
    c.message = subject
    for l in f:
        if l == "---\n":
            break
        c.message += l
    diff = ""
    for l in f:
        if l == "-- \n":
            break
        diff += l
    version = f.next().rstrip("\n")
    return c, diff, version