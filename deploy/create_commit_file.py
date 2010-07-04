from subprocess import Popen, PIPE
import os
import re

process = Popen(["git", "rev-parse", "HEAD"], stdout=PIPE)
guid = process.communicate()[0].strip()

process = Popen(["git", "branch"], stdout=PIPE)
branches = process.communicate()[0].strip()
branch = re.search(r"\* ([^\n]+)", branches).group(1)

with open(os.path.join(os.path.dirname(__file__), '..', 'commit.py'), 'w') as f:
    f.write("LAST_COMMIT_GUID = '{0}/{1}'\n".format(branch, guid[:8]))
