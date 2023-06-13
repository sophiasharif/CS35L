'''
To check that my script does not call upon any external commands,
I used the following command in a few different example repositories:

    $ strace -f -e trace=execve python3 topo_order_commits.py

There were no statements with execve, which confirmed that my script
is not making any command calls beyond what the Python interpreter itself executes.
'''


import os
import sys
import zlib
import random
from collections import deque
from copy import deepcopy

def error(msg: str) -> int:
    """ helper function to print errors to standard output"""
    print(msg, file=sys.stderr)
    return 1


def git_location() -> str:
    """
    STEP 1: discover the .git directory
    returns the location of the top-level git repository.
    (returns none if current directory does not reside within a git repo.)
    """

    curr_dir = os.getcwd()
    # run while until we reach the root directory
    while curr_dir != os.path.dirname(curr_dir):
        if os.path.isdir(f'{curr_dir}/.git'):
            return curr_dir
        curr_dir = os.path.dirname(curr_dir)

    return None


def git_local_branch_names(repo_path: str) -> list:
    """
    STEP 2: Get the list of local branch names
    """
    branch_dir = os.path.join(repo_path, '.git', 'refs', 'heads')

    branches = []
    for dirpath, dirnames, filenames in os.walk(branch_dir):
        for filename in filenames:
            branches.append(os.path.join(dirpath, filename))

    branch_names = [path[len(branch_dir) + 1:] for path in branches]

    return branch_names


def git_commit_hash(repo_path: str, branch: str):
    """get the commit hash of a branch"""
    branch_path = os.path.join(repo_path, '.git', 'refs', 'heads', branch)
    with open(branch_path, 'r') as file:
        commit_hash = file.readline().strip()
    return commit_hash


def git_parents(repo_path, commit_hash):
    """get the parents of a commit"""

    # find the object representing the commit
    object_path = os.path.join(repo_path, '.git', 'objects', commit_hash[:2], commit_hash[2:])

    # decompress and read commit data
    header = ""
    with open(object_path, 'rb') as file:
        data = zlib.decompress(file.read()).decode()
        # Separate the header from the commit message
    header, _ = data.split('\n\n', 1)


    # get all parents
    parent_hashes = []
    start = 0
    while True:
        parent_start = header.find("parent ", start)
        if parent_start == -1:  # no more parents found
            break
        parent_hash = header[parent_start+7:parent_start+47]  # commits are 40 chars long
        parent_hashes.append(parent_hash)
        start = parent_start + 47

    return parent_hashes


class CommitNode:
    def __init__(self, commit_hash: str):
        self.commit_hash = commit_hash
        self.parents = []
        self.children = []
        self.branches = []

    def __eq__(self, other):
        if isinstance(other, CommitNode):
            return self.commit_hash == other.commit_hash
        return False

    def __hash__(self):
        return hash(self.commit_hash)

    def __repr__(self):
        repr = f"\nNODE {self.commit_hash[:4]}\nPARENTS:"
        for parent in self.parents:
            repr += "\n    " + parent[:4]
        repr += "\nCHILDREN:"
        for child in self.children:
            repr += "\n    " + child[:4]
        repr += '\n'
        return repr

    def is_parent_of(self, commit):
        return commit in self.children

    def add_parent(self, parent):
        if parent not in self.parents:
            self.parents.append(parent)

    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)


class CommitGraph:

    def __init__(self, dict_graph):
        self.nodes = deepcopy(dict_graph)

    def get_parents(self, commit) -> set:
        if commit not in self.nodes:
            raise Exception(f"Commit {commit} does not exist in CommitGraph.")
        return self.nodes[commit].parents

    def get_children(self, commit) -> set:
        if commit not in self.nodes:
            raise Exception(f"Commit {commit} does not exist in CommitGraph.")
        return self.nodes[commit].children

    def remove_edge(self, child_hash, parent_hash):
        # remove parent_hash from child_hash's parents
        self.nodes[child_hash].parents.remove(parent_hash)
        # remove child_hash from parent_hash's children
        self.nodes[parent_hash].children.remove(child_hash)

    def root_commit_hash(self) -> str:
        # get random node
        current = random.choice(list(self.nodes.keys()))
        parents = self.get_parents(current)
        while len(parents) > 0:
            current = random.choice(list(parents))
            parents = self.get_parents(current)
        return current

    def remove(self, commit_hash):
        del self.nodes[commit_hash]


def git_commits_to_branches_map(branch_names, root_commits):
    commits_to_branches = {}

    for i in range(len(root_commits)):
        commit = root_commits[i]
        branch = branch_names[i]
        if commit in commits_to_branches:
            commits_to_branches[commit].append(branch)
        else:
            commits_to_branches[commit] = [branch]

    return commits_to_branches


def git_commit_graph(repo_path):
    """
    STEP 3: Build the commit graph
    """

    branch_names = git_local_branch_names(repo_path)
    root_commits = [git_commit_hash(repo_path, branch) for branch in branch_names]
    commits_to_branches = git_commits_to_branches_map(branch_names, root_commits)

    visited = {}

    for commit in root_commits:
        stack = [(commit, None)]  # The stack will contain pairs of (node, parent)

        while stack:
            current_hash, child_hash = stack.pop()

            # Check if current_hash has been visited before
            if current_hash not in visited:
                # Create a new node
                current_node = CommitNode(current_hash)

                # Handle parent-child relationships
                if child_hash:
                    current_node.add_child(child_hash)

                # Add branch names (if any)
                if current_hash in commits_to_branches:
                    current_node.branches = sorted(commits_to_branches[current_hash])

                # Add current node to visited
                visited[current_hash] = current_node

                # For each parent, add to the stack
                parent_hashes = git_parents(repo_path, current_hash)
                for parent_hash in parent_hashes:
                    current_node.add_parent(parent_hash)
                    stack.append((parent_hash, current_hash))

            elif child_hash:
                # If node has been visited and it has a child_hash, add relationships
                visited[current_hash].add_child(child_hash)
                visited[child_hash].add_parent(current_hash)

    return visited


def git_topological_sort(dict_graph):

    # set up data structures
    commit_graph = CommitGraph(dict_graph)
    sorted_commits = []
    no_prereqs = deque([commit_graph.root_commit_hash()])      # add very first commit to no_prereqs

    while len(no_prereqs) > 0:

        # add commit with no dependencies to sorted_commits
        current = no_prereqs.pop()
        sorted_commits.append(dict_graph[current])

        # get all children of current and eliminate their edges from the graph
        for child_hash in list(commit_graph.get_children(current)):
            commit_graph.remove_edge(child_hash, current)
            # if child doesn't have any more parents, add to sorted
            if len(commit_graph.get_parents(child_hash)) == 0:
                no_prereqs.append(child_hash)

    sorted_commits.reverse()
    return sorted_commits


def print_sorted_commits(sorted_commits):

    sticky_start = False
    for i in range(len(sorted_commits)):
        current = sorted_commits[i]
        next_commit = None
        if i < len(sorted_commits) - 1:
            next_commit = sorted_commits[i + 1]

        # if sticky_start, print children
        if sticky_start:
            print("=", *current.children)
            sticky_start = False

        # print hash (and branch names if any)
        if not current.branches:
            print(current.commit_hash)
        else:
            print(f"{current.commit_hash} ", *current.branches)

        # if next commit is current's parent, print a stick end.
        if (next_commit is not None) and (next_commit.commit_hash not in current.parents):
            print(*next_commit.parents, "=\n")
            sticky_start = True


def topo_order_commits():
    repo_path = git_location()
    if repo_path is None:
        exit(error("Not inside a Git repository"))
    commit_graph = git_commit_graph(repo_path)
    sorted_commits = git_topological_sort(commit_graph)
    print_sorted_commits(sorted_commits)


if __name__ == '__main__':
    topo_order_commits()
