from subprocess import Popen, PIPE
import os

process = Popen(["git", "rev-parse", "HEAD"], stdout=PIPE)
guid = process.communicate()[0].strip()

with open(os.path.join(os.path.dirname(__file__), '..', 'commit.py'), 'w') as f:
    f.write("LAST_COMMIT_GUID = '{0}'\n".format(guid))
