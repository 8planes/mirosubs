import os

from utils.git_helpers import get_current_branch, get_current_commit_hash

    
def main():
    guid = get_current_commit_hash()
    branch = get_current_branch()
    with open(os.path.join(os.path.dirname(__file__), '..', 'commit.py'), 'w') as f:
        f.write("LAST_COMMIT_GUID = '{0}/{1}'\n".format(branch, guid[:8]))

if __name__ == '__main__':
    main()
