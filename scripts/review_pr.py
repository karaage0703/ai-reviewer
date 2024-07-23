import os
from openai import OpenAI
import requests
import json


def get_pr_diff():
    """Retrieve the diff of the specified pull request.

    Returns:
        str: The diff of the pull request.
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

    return response.text


def review_diff(diff):
    """Review the diff using the GPT-4 API.

    Args:
        diff (str): The diff to review.

    Returns:
        str: The review comments.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a code review assistant."},
            {"role": "user", "content": f"Please review the following pull request diff in Japanese:\n\n{diff}"}
        ],
        max_tokens=1024
    )

    return response.choices[0].message.content


def post_review_comments(comments):
    """Post the review comments to the pull request.

    Args:
        comments (str): The review comments.
    """
    repo = os.getenv('GITHUB_REPOSITORY')
    pr_number = os.getenv('PULL_REQUEST_NUMBER')
    token = os.getenv('GITHUB_TOKEN')
    comments_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "body": comments
    }

    response = requests.post(comments_url, headers=headers, json=data)
    response.raise_for_status()


def main():
    """Main function to handle the pull request review."""
    diff = get_pr_diff()
    review_comments = review_diff(diff)
    post_review_comments(review_comments)


if __name__ == "__main__":
    main()
