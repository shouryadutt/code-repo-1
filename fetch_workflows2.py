import requests
import os

def fetch_workflows(repo_name, branch_name, github_token):
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    # GitHub API URL to fetch the contents of the .github/workflows directory
    api_url = f'https://api.github.com/repos/{repo_name}/contents/.github/workflows?ref={branch_name}'
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        workflows = response.json()
        if not workflows:
            print(f"No workflows found in {repo_name} on branch {branch_name}.")
        else:
            print(f"Workflows in repository {repo_name} on branch {branch_name}:")
            for workflow in workflows:
                if workflow['type'] == 'file' and workflow['name'].endswith('.yml'):
                    workflow_name = workflow['name']
                    file_path = workflow['path']
                    print(f"- {workflow_name}")
                    download_workflow_file(repo_name, file_path, branch_name, github_token)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching workflows from {repo_name} on branch {branch_name}: {e}")

def download_workflow_file(repo_name, file_path, branch_name, github_token):
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    # GitHub raw content URL to fetch the workflow YAML content
    raw_url = f'https://raw.githubusercontent.com/{repo_name}/{branch_name}/{file_path}'
    try:
        workflow_yaml = requests.get(raw_url, headers=headers).text
        if workflow_yaml:
            save_workflow_to_file(file_path, workflow_yaml)
        else:
            print(f"Failed to download workflow file: {file_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching workflow file from {repo_name}: {e}")

def save_workflow_to_file(file_path, workflow_content):
    # Define the target directory as .github/workflows
    target_directory = ".github/workflows/"
    # Ensure the directory exists
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    # Extract the filename from the file path
    filename = file_path.split("/")[-1]
    # Save the workflow YAML content to the .github/workflows directory
    filepath = os.path.join(target_directory, filename)

    # Check if the file already exists
    if os.path.exists(filepath):
        # If it exists, check if the content is different
        with open(filepath, 'r') as file:
            existing_content = file.read()
            if existing_content == workflow_content:
                print(f"Workflow {filename} is already up to date. No changes made.")
                return
            else:
                print(f"Workflow {filename} content has changed. Overwriting the file.")
    else:
        print(f"File {filename} does not exist. Creating it.")

    # Write the content to the file
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