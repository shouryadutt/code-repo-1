import requests
import os
def fetch_workflows(repo_name, branch_name, github_token):
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    # GitHub API URL to fetch workflows from the repo
    api_url = f'https://api.github.com/repos/{repo_name}/actions/workflows?ref={branch_name}'
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        workflows = response.json().get('workflows', [])
        if not workflows:
            print(f"No workflows found for {repo_name} on branch {branch_name}.")
        else:
            print(f"Workflows in repository {repo_name} on branch {branch_name}:")
            for workflow in workflows:
                workflow_name = workflow['name']
                workflow_id = workflow['id']
                print(f"- {workflow_name} (ID: {workflow_id})")
                download_workflow_file(repo_name, workflow_id, branch_name, github_token)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching workflows from {repo_name} on branch {branch_name}: {e}")
def download_workflow_file(repo_name, workflow_id, branch_name, github_token):
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    # GitHub API URL to fetch workflow content by ID
    api_url = f'https://api.github.com/repos/{repo_name}/actions/workflows/{workflow_id}/timing'
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        workflow_file_url = response.json().get('path')
        if not workflow_file_url:
            print(f"No workflow file found for workflow ID {workflow_id}.")
            return
        # GitHub API URL to fetch the raw workflow YAML content
        raw_url = f'https://raw.githubusercontent.com/{repo_name}/{branch_name}/{workflow_file_url}'
        workflow_yaml = requests.get(raw_url, headers=headers).text
        if workflow_yaml:
            save_workflow_to_file(workflow_file_url, workflow_yaml)
        else:
            print(f"Failed to download workflow file: {workflow_file_url}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching workflow file from {repo_name}: {e}")
def save_workflow_to_file(workflow_file_url, workflow_content):
    # Define the target directory as .github/workflows
    target_directory = ".github/workflows/"
    # Ensure the directory exists
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
    # Extract the filename from the file URL
    filename = workflow_file_url.split("/")[-1]
    # Save the workflow YAML content to the .github/workflows directory
    filepath = os.path.join(target_directory, filename)
    with open(filepath, 'w') as file:
        file.write(workflow_content)
    print(f"Workflow saved to {filepath}")
if __name__ == "__main__":
    # List of repositories and branches provided as environment variables
    repo_branch_list = os.getenv('REPO_BRANCH_LIST')
    # GitHub token from environment
    github_token = os.getenv('GITHUB_TOKEN')
    if repo_branch_list and github_token:
        # Parse the repo_branch_list from a string (comma-separated pairs)
        repo_branch_list = [item.split(':') for item in repo_branch_list.split(',')]
        for repo_name, branch_name in repo_branch_list:
            print(f"Fetching workflows for {repo_name} on branch {branch_name}...")
            fetch_workflows(repo_name, branch_name, github_token)
    else:
        print("Please provide REPO_BRANCH_LIST and GITHUB_TOKEN.")