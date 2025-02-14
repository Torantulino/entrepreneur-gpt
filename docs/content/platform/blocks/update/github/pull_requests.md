
# GitHub Pull Request Management Blocks

## List Pull Requests

### What it is
A tool that retrieves a list of all pull requests from a specified GitHub repository.

### What it does
Fetches and displays information about all open pull requests, including their titles and URLs.

### How it works
Connects to GitHub, accesses the specified repository, and retrieves the list of pull requests.

### Inputs
- Repository URL: The web address of the GitHub repository
- GitHub Credentials: Authentication details to access the repository

### Outputs
- Pull Request List: Collection of pull requests with their titles and URLs
- Error Message: Information about any issues that occurred

### Possible use case
Monitoring active development work by viewing all ongoing pull requests in a project.

## Make Pull Request

### What it is
A tool for creating new pull requests in a GitHub repository.

### What it does
Creates a new pull request with specified details, including title, description, and branch information.

### How it works
Takes your provided information and submits it to GitHub to create a new pull request.

### Inputs
- Repository URL: The web address of the GitHub repository
- Title: Name of the pull request
- Body: Detailed description of the changes
- Head Branch: The branch containing your changes
- Base Branch: The branch you want to merge into
- GitHub Credentials: Authentication details

### Outputs
- Pull Request Number: Unique identifier for the created PR
- Pull Request URL: Web address of the new PR
- Error Message: Information about any issues

### Possible use case
Automating the creation of pull requests for regular code updates or maintenance tasks.

## Read Pull Request

### What it is
A tool that retrieves detailed information about a specific pull request.

### What it does
Fetches and displays comprehensive information about a pull request, including its content and changes.

### How it works
Retrieves the pull request details from GitHub and presents them in an organized format.

### Inputs
- Pull Request URL: Web address of the specific pull request
- Include Changes Flag: Option to include code changes
- GitHub Credentials: Authentication details

### Outputs
- Title: Name of the pull request
- Body: Full description
- Author: Creator of the pull request
- Changes: Code modifications (if requested)
- Error Message: Information about any issues

### Possible use case
Reviewing pull request details before approving changes or providing feedback.

## Assign PR Reviewer

### What it is
A tool for assigning reviewers to pull requests.

### What it does
Adds a specified user as a reviewer to a pull request.

### How it works
Updates the pull request's reviewer list with the specified username.

### Inputs
- Pull Request URL: Web address of the specific pull request
- Reviewer Username: GitHub username of the reviewer
- GitHub Credentials: Authentication details

### Outputs
- Status: Success or failure message
- Error Message: Information about any issues

### Possible use case
Automatically assigning team members to review code changes.

## Unassign PR Reviewer

### What it is
A tool for removing reviewers from pull requests.

### What it does
Removes a specified reviewer from a pull request.

### How it works
Updates the pull request to remove the specified reviewer from the reviewer list.

### Inputs
- Pull Request URL: Web address of the specific pull request
- Reviewer Username: GitHub username to remove
- GitHub Credentials: Authentication details

### Outputs
- Status: Success or failure message
- Error Message: Information about any issues

### Possible use case
Reassigning reviews when a team member is unavailable or when restructuring review assignments.

## List PR Reviewers

### What it is
A tool that shows all assigned reviewers for a pull request.

### What it does
Retrieves and displays a list of all users assigned to review a specific pull request.

### How it works
Fetches the reviewer information from GitHub and presents it in an organized list.

### Inputs
- Pull Request URL: Web address of the specific pull request
- GitHub Credentials: Authentication details

### Outputs
- Reviewer List: Collection of reviewer usernames and profile URLs
- Error Message: Information about any issues

### Possible use case
Checking who is responsible for reviewing a particular pull request.
