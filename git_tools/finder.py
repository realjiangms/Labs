import subprocess
import sys

def run_script(commit_hash, script_path, repo_dir, *script_args):
    subprocess.run(['git', 'checkout', commit_hash], cwd=repo_dir, check=True)
    result = subprocess.run([script_path] + list(script_args), cwd=repo_dir, capture_output=True, text=True)
    return result.returncode == 0, result.stdout

def is_commit_valid(commit_hash, repo_dir):
    result = subprocess.run(['git', 'cat-file', '-e', commit_hash], cwd=repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def get_commit_order(repo_dir, commit1, commit2):
    result = subprocess.run(['git', 'rev-list', f'{commit1}..{commit2}'], cwd=repo_dir, capture_output=True, text=True)
    if result.stdout:
        return commit1, commit2
    else:
        return commit2, commit1

def find_middle_commit(repo_dir, start_commit, end_commit):
    commits = subprocess.run(['git', 'rev-list', '--ancestry-path', f'{start_commit}..{end_commit}'], cwd=repo_dir, check=True, capture_output=True, text=True).stdout.strip().splitlines()
    if not commits:
        return None
    middle_index = len(commits) // 2
    return commits[middle_index]

def find_commit_pair(repo_dir, start_commit, end_commit, script_path, script_args):
    start_commit, end_commit = get_commit_order(repo_dir, start_commit, end_commit)

    if not is_commit_valid(start_commit, repo_dir):
        print(f"Error: Start commit {start_commit} does not exist.")
        sys.exit(1)
    if not is_commit_valid(end_commit, repo_dir):
        print(f"Error: End commit {end_commit} does not exist.")
        sys.exit(1)

    start_result, start_output = run_script(start_commit, script_path, repo_dir, *script_args)
    end_result, end_output = run_script(end_commit, script_path, repo_dir, *script_args)

    if start_result == end_result:
        print("Error: The script results for start and end commits are the same.")
        sys.exit(1)

    left, right = start_commit, end_commit
    while True:
        middle_commit = find_middle_commit(repo_dir, left, right)
        if not middle_commit or middle_commit == left or middle_commit == right:
            print(f"Found commits where the script result changes:")
            print(f"Commit 1: {left}")
            print("Output of the script on Commit 1:")
            print(start_output)
            print(f"Commit 2: {right}")
            print("Output of the script on Commit 2:")
            print(end_output)
            break

        middle_result, middle_output = run_script(middle_commit, script_path, repo_dir, *script_args)
        if middle_result == start_result:
            left, start_output = middle_commit, middle_output
        else:
            right, end_output = middle_commit, middle_output

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python find_commit_diff.py <repo_dir> <commit1> <commit2> <script_path> [script_args...]")
        sys.exit(1)

    repo_dir = sys.argv[1]
    commit1 = sys.argv[2]
    commit2 = sys.argv[3]
    script_path = sys.argv[4]
    script_args = sys.argv[5:]

    find_commit_pair(repo_dir, commit1, commit2, script_path, script_args)
