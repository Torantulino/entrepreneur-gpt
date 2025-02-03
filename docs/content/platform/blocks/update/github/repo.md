
# GitHub Repository Management Blocks

## GitHub List Tags

### What it is
A tool that retrieves all tags from a GitHub repository.

### What it does
Fetches and displays a list of all tags in a specified GitHub repository, including their names and URLs.

### How it works
Connects to GitHub, retrieves tag information from the specified repository, and presents each tag with its corresponding URL.

### Inputs
- GitHub Credentials: Authentication details for accessing GitHub
- Repository URL: The web address of the GitHub repository

### Outputs
- Tag Name: The name of each tag
- Tag URL: Direct link to browse the repository at that tag
- Error Message: Any error that occurred during the process

### Possible use case
Monitoring version tags of a software project to track releases and updates.

## GitHub List Branches

### What it is
A tool that retrieves all branches from a GitHub repository.

### What it does
Fetches and displays a list of all branches in a specified GitHub repository, including their names and URLs.

### How it works
Connects to GitHub, retrieves branch information from the specified repository, and presents each branch with its corresponding URL.

### Inputs
- GitHub Credentials: Authentication details for accessing GitHub
- Repository URL: The web address of the GitHub repository

### Outputs
- Branch Name: The name of each branch
- Branch URL: Direct link to browse the repository at that branch
- Error Message: Any error that occurred during the process

### Possible use case
Monitoring active development branches in a project to track different features or versions being worked on.

## GitHub List Discussions

### What it is
A tool that retrieves recent discussions from a GitHub repository.

### What it does
Fetches and displays a list of recent discussions from a specified GitHub repository.

### How it works
Connects to GitHub, retrieves discussion information, and presents each discussion with its title and URL.

### Inputs
- GitHub Credentials: Authentication details for accessing GitHub
- Repository URL: The web address of the GitHub repository
- Number of Discussions: How many recent discussions to retrieve (default: 5)

### Outputs
- Discussion Title: The title of each discussion
- Discussion URL: Direct link to the discussion
- Error Message: Any error that occurred during the process

### Possible use case
Monitoring community engagement and discussions about a project.

## GitHub List Releases

### What it is
A tool that retrieves all releases from a GitHub repository.

### What it does
Fetches and displays a list of all releases in a specified GitHub repository.

### How it works
Connects to GitHub, retrieves release information, and presents each release with its name and URL.

### Inputs
- GitHub Credentials: Authentication details for accessing GitHub
- Repository URL: The web address of the GitHub repository

### Outputs
- Release Name: The name of each release
- Release URL: Direct link to the release
- Error Message: Any error that occurred during the process

### Possible use case
Tracking official releases and their documentation for a software project.

## GitHub Read File

### What it is
A tool that reads the content of a file from a GitHub repository.

### What it does
Retrieves and displays the content of a specified file from a GitHub repository.

### How it works
Connects to GitHub, locates the specified file, and retrieves its content in both text and raw formats.

### Inputs
- GitHub Credentials: Authentication details for accessing GitHub
- Repository URL: The web address of the GitHub repository
- File Path: Location of the file within the repository
- Branch: Which branch to read from (default: master)

### Outputs
- Text Content: The file's content in readable text format
- Raw Content: The file's content in base64 encoded format
- File Size: Size of the file in bytes
- Error Message: Any error that occurred during the process

### Possible use case
Retrieving configuration files or documentation from a repository.

## GitHub Read Folder

### What it is
A tool that reads the contents of a folder from a GitHub repository.

### What it does
Retrieves and displays a list of all files and folders within a specified directory.

### How it works
Connects to GitHub, locates the specified folder, and lists all its contents with details.

### Inputs
- GitHub Credentials: Authentication details for accessing GitHub
- Repository URL: The web address of the GitHub repository
- Folder Path: Location of the folder within the repository
- Branch: Which branch to read from (default: master)

### Outputs
- Files: List of files with names, paths, and sizes
- Directories: List of subdirectories with names and paths
- Error Message: Any error that occurred during the process

### Possible use case
Exploring the structure of a project or finding specific files within a repository.

## GitHub Make Branch

### What it is
A tool that creates a new branch in a GitHub repository.

### What it does
Creates a new branch from an existing source branch in a repository.

### How it works
Connects to GitHub, copies the specified source branch, and creates a new branch with the desired name.

### Inputs
- GitHub Credentials: Authentication details for accessing GitHub
- Repository URL: The web address of the GitHub repository
- New Branch Name: Name for the branch to be created
- Source Branch Name: Name of the branch to copy from

### Outputs
- Status: Result of the branch creation operation
- Error Message: Any error that occurred during the process

### Possible use case
Creating a new feature branch for development work.

## GitHub Delete Branch

### What it is
A tool that deletes a branch from a GitHub repository.

### What it does
Removes a specified branch from the repository.

### How it works
Connects to GitHub and removes the specified branch from the repository.

### Inputs
- GitHub Credentials: Authentication details for accessing GitHub
- Repository URL: The web address of the GitHub repository
- Branch Name: Name of the branch to delete

### Outputs
- Status: Result of the branch deletion operation
- Error Message: Any error that occurred during the process

### Possible use case
Cleaning up old feature branches after merging work.

## GitHub Create File

### What it is
A tool that creates a new file in a GitHub repository.

### What it does
Creates a new file with specified content in a repository.

### How it works
Connects to GitHub and creates a new file at the specified location with the provided content.

### Inputs
- GitHub Credentials: Authentication details for accessing GitHub
- Repository URL: The web address of the GitHub repository
- File Path: Where to create the file
- Content: What to write in the file
- Branch: Which branch to create the file in
- Commit Message: Description of the change

### Outputs
- File URL: Web address of the created file
- Commit SHA: Unique identifier for the commit
- Error Message: Any error that occurred during the process

### Possible use case
Adding new documentation or configuration files to a project.

## GitHub Update File

### What it is
A tool that updates an existing file in a GitHub repository.

### What it does
Modifies the content of an existing file in a repository.

### How it works
Connects to GitHub, locates the specified file, and updates its content with the new version.

### Inputs
- GitHub Credentials: Authentication details for accessing GitHub
- Repository URL: The web address of the GitHub repository
- File Path: Location of the file to update
- Content: New content for the file
- Branch: Which branch contains the file
- Commit Message: Description of the change

### Outputs
- File URL: Web address of the updated file
- Commit SHA: Unique identifier for the commit
- Error Message: Any error that occurred during the process

### Possible use case
Updating version numbers or documentation in project files.

## GitHub Create Repository

### What it is
A tool that creates a new GitHub repository.

### What it does
Creates a new repository with specified settings and initial content.

### How it works
Connects to GitHub and creates a new repository with the provided configuration.

### Inputs
- GitHub Credentials: Authentication details for accessing GitHub
- Name: Name for the new repository
- Description: Description of the repository
- Private: Whether the repository should be private
- Auto Initialize: Whether to create an initial README file
- GitIgnore Template: Template for ignoring files

### Outputs
- Repository URL: Web address of the created repository
- Clone URL: Address for cloning the repository
- Error Message: Any error that occurred during the process

### Possible use case
Setting up a new project repository with proper initial configuration.

## GitHub List Stargazers

### What it is
A tool that retrieves all users who have starred a GitHub repository.

### What it does
Fetches and displays a list of users who have starred the repository.

### How it works
Connects to GitHub and retrieves information about users who have starred the repository.

### Inputs
- GitHub Credentials: Authentication details for accessing GitHub
- Repository URL: The web address of the GitHub repository

### Outputs
- Username: Name of each user who starred the repository
- Profile URL: Link to each user's GitHub profile
- Error Message: Any error that occurred during the process

### Possible use case
Analyzing community interest in a project or reaching out to engaged users.
