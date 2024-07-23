# ai-reviewer
ai reviewer

This repository contains a GitHub Actions workflow and Python script to automatically review pull requests using the GPT-4 API. The workflow is designed to be triggered manually, and it fetches the diff or files changed in a pull request, sends the changes to the GPT-4 API for review, and posts the review comments back to the pull request.

## Features

- Automatically reviews pull requests using GPT-4o.
- Posts review comments back to the pull request on GitHub.
- Can be triggered manually using GitHub Actions.

## Prerequisites

- Python 3.8+
- Docker (optional, for containerized execution)

## Setup

### 1. Clone the repository

```sh
$ git clone https://github.com/karaage0703/ai-reviewer
$ cd ai-reviewer
```

### 2. Set up environment variables

Execute following commands and set the following environment variables:

```env
export OPENAI_API_KEY=your_openai_api_key
export GITHUB_TOKEN=your_github_token
export GITHUB_REPOSITORY=your_github_repository
export PULL_REQUEST_NUMBER=your_pull_request_number
```

- `OPENAI_API_KEY`: Your OpenAI API key.
- `GITHUB_TOKEN`: Your GitHub personal access token with repo permissions.
- `GITHUB_REPOSITORY`: The repository in the format `owner/repo`.
- `PULL_REQUEST_NUMBER`: The pull request number to review.

### 3. Install dependencies

If running locally without Docker, install the necessary Python packages:

```sh
pip install -r scripts/requirements.txt
```

### 4. Run the review script

```sh
python scripts/review_pr.py
```

## Docker Setup

You can use Docker.

## GitHub Actions Setup

The provided GitHub Actions workflow can be used to trigger the review bot manually.

### 1. Create the GitHub Actions workflow

Create a file at `.github/workflows/pr-review.yml` with the following content:

```yaml
name: PR Review

on:
  workflow_dispatch:
    inputs:
      pull_request_number:
        description: 'The number of the pull request to review'
        required: true
        type: number

jobs:
  review:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r scripts/requirements.txt

    - name: Run review script
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        GITHUB_REPOSITORY: ${{ github.repository }}
        PULL_REQUEST_NUMBER: ${{ github.event.inputs.pull_request_number }}
      run: python scripts/review_pr.py
```

### 2. Add GitHub Secrets

Add the following secrets to your GitHub repository settings:

- `OPENAI_API_KEY`: Your OpenAI API key.
- `GITHUB_TOKEN`: Your GitHub personal access token.

### 3. Trigger the workflow manually

Go to the Actions tab in your GitHub repository, select the `PR Review` workflow, and click on `Run workflow`. Enter the pull request number to start the review process.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
