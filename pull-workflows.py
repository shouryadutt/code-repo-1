import yaml
import os
import subprocess

# Function to load the YAML file
def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Function to pull workflows from the template-repo
def pull_workflow(workflow_name, version_tag='main'):
    # Define the template repo URL (replace with your actual template repo URL)
    template_repo = "https://github.com/your-org/template-repo.git"
    
    # Clone the specific branch (defaulting to main) of the template repo
    subprocess.run([
        'git', 'clone', '--branch', version_tag, template_repo, 'template-repo'
    ], check=True)

    # Define the workflow file path in the template-repo
    workflow_path = os.path.join('template-repo', '.github', 'workflows', workflow_name)
    
    # Copy the workflow to the code-repo's .github/workflows directory
    os.makedirs('.github/workflows', exist_ok=True)
    subprocess.run(['cp', workflow_path, '.github/workflows/'], check=True)

    # Remove the cloned template-repo after pulling the workflows
    subprocess.run(['rm', '-rf', 'template-repo'])

# Function to process components and pull the necessary workflows
def process_components(yaml_data):
    components = yaml_data.get('components', [])
    
    # Default to the 'main' branch since versioning is not used
    version_tag = 'main'
    
    # Pull workflows based on the components defined in YAML
    if 'build' in components:
        print("Pulling build-workflow.yaml...")
        pull_workflow('build-workflow.yaml', version_tag)
        
    if 'deploy-dev-weblogic' in components:
        print("Pulling deploy-dev-weblogic.yaml...")
        pull_workflow('deploy-dev-weblogic.yaml', version_tag)

# Main execution
if __name__ == "__main__":
    # Load the components-config.yaml file
    yaml_data = load_yaml('components-config.yaml')
    
    # Pull the required workflows based on the YAML configuration
    process_components(yaml_data)
