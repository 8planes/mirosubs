from subprocess import Popen, PIPE
import os
import re

def get_current_commit_hash(short=True):
    process = Popen(["git", "rev-parse", "HEAD"], stdout=PIPE)
    guid =  process.communicate()[0].strip()
    if guid:
        guid = guid[:8]
    return guid

def get_current_branch():
    process = Popen(["git", "branch"], stdout=PIPE)
    branches = process.communicate()[0].strip()
    branch = re.search(r"\* ([^\n]+)", branches).group(1)
    return branch
