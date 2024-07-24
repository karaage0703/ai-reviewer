import os
from openai import OpenAI
import requests
import json
from system_prompt import reviewer_prompt

def get_pr_diff():
    """Retrieve the diff of the specified pull request.

    Returns:
        dict: The diff of the pull request by file.
    """
    repo = os.getenv('GITHUB_REPOSITORY')
    pr_number = os.getenv('PULL_REQUEST_NUMBER')
    token = os.getenv('GITHUB_TOKEN')
    diff_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.diff"
    }

    response = requests.get(diff_url, headers=headers)
    response.raise_for_status()

    diff = response.text
    return split_diff_by_file(diff)


def split_diff_by_file(diff):
    """Split the diff into individual files.

    Args:
        diff (str): The full diff of the pull request.

    Returns:
        dict: A dictionary where the keys are filenames and the values are the diffs for those files.
    """
    files_diff = {}
    current_file = None
    for line in diff.splitlines():
        if line.startswith('diff --git'):
            current_file = line.split(' b/')[-1]
            files_diff[current_file] = []
        if current_file:
            files_diff[current_file].append(line)

    # Convert list of lines back to single string
    for file in files_diff:
        files_diff[file] = '\n'.join(files_diff[file])

    return files_diff


def review_diff(diff):
    """Review the diff using the GPT-4 API.

    Args:
        diff (str): The diff to review.

    Returns:
        str: The review comments.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": reviewer_prompt },
            {"role": "user", "content": f"Please review the following pull request diff in Japanese:\n\n{diff}"}
        ],
        max_tokens=16384
    )

    return response.choices[0].message.content


def post_review_comments(comments, file_path):
    """Post the review comments to the pull request.

    Args:
        comments (str): The review comments.
        file_path (str): The path of the file being reviewed.
    """
    repo = os.getenv('GITHUB_REPOSITORY')
    pr_number = os.getenv('PULL_REQUEST_NUMBER')
    token = os.getenv('GITHUB_TOKEN')

    comments_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"
    commit_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/commits"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    pr_commits_response = requests.get(commit_url, headers=headers)
    pr_commits = pr_commits_response.json()
    last_commit = pr_commits[-1]['sha']

    data = {
        "body": comments,
        "commit_id" : last_commit,
        "path": file_path,
        "side": "RIGHT",
        "line": 1  # Assuming we always post comment on the first line of the diff for simplicity.
    }

    response = requests.post(comments_url, headers=headers, data=json.dumps(data))
    response.raise_for_status()


def main():
    """Main function to handle the pull request review."""
    diffs_by_file = get_pr_diff()
    for file_path, diff in diffs_by_file.items():
        review_comments = review_diff(diff)
        post_review_comments(review_comments, file_path)


if __name__ == "__main__":
    main()
