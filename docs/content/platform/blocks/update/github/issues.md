
# GitHub Issue Management Blocks

## GitHub Comment
### What it is
A tool for adding comments to GitHub issues or pull requests.

### What it does
Posts new comments on existing GitHub issues or pull requests automatically.

### How it works
Takes your comment text and adds it to the specified issue or pull request using your GitHub credentials.

### Inputs
- GitHub Credentials: Your authentication details for GitHub
- Issue URL: The web address of the issue or pull request
- Comment: The text you want to post as a comment

### Outputs
- Comment ID: A unique identifier for your posted comment
- Comment URL: Direct link to view your comment
- Error Message: Information if something goes wrong

### Possible use case
Automatically responding to bug reports with status updates or requesting more information from users.

## GitHub Make Issue
### What it is
A tool for creating new issues in GitHub repositories.

### What it does
Creates new issues with customized titles and descriptions in any GitHub repository you have access to.

### How it works
Uses your provided information to create a new issue in the specified repository with your desired title and description.

### Inputs
- GitHub Credentials: Your authentication details for GitHub
- Repository URL: The web address of the GitHub repository
- Title: The heading for your new issue
- Body: The main content of your issue

### Outputs
- Issue Number: The unique identifier for your new issue
- Issue URL: Direct link to view your issue
- Error Message: Information if something goes wrong

### Possible use case
Automatically creating standardized bug reports or feature requests based on user feedback.

## GitHub Read Issue
### What it is
A tool for retrieving information from existing GitHub issues.

### What it does
Fetches and provides the contents and details of any specified GitHub issue.

### How it works
Retrieves the title, description, and creator information from a given issue URL.

### Inputs
- GitHub Credentials: Your authentication details for GitHub
- Issue URL: The web address of the issue you want to read

### Outputs
- Title: The heading of the issue
- Body: The main content of the issue
- User: The username of who created the issue
- Error Message: Information if something goes wrong

### Possible use case
Monitoring specific issues for updates or collecting issue information for reporting.

## GitHub List Issues
### What it is
A tool for getting a list of all issues in a GitHub repository.

### What it does
Retrieves and lists all available issues from a specified GitHub repository.

### How it works
Fetches all issues from the repository and provides their titles and URLs in a list format.

### Inputs
- GitHub Credentials: Your authentication details for GitHub
- Repository URL: The web address of the GitHub repository

### Outputs
- Issues: A list of issues with their titles and URLs
- Error Message: Information if something goes wrong

### Possible use case
Creating a dashboard of all open issues or generating reports about repository activity.

## GitHub Add Label
### What it is
A tool for adding labels to GitHub issues or pull requests.

### What it does
Applies specified labels to any GitHub issue or pull request you have access to.

### How it works
Adds the specified label to the issue or pull request identified by the URL.

### Inputs
- GitHub Credentials: Your authentication details for GitHub
- Issue URL: The web address of the issue or pull request
- Label: The name of the label to add

### Outputs
- Status: Confirmation of the label addition
- Error Message: Information if something goes wrong

### Possible use case
Automatically categorizing issues based on their content or priority level.

## GitHub Remove Label
### What it is
A tool for removing labels from GitHub issues or pull requests.

### What it does
Removes specified labels from any GitHub issue or pull request you have access to.

### How it works
Removes the specified label from the issue or pull request identified by the URL.

### Inputs
- GitHub Credentials: Your authentication details for GitHub
- Issue URL: The web address of the issue or pull request
- Label: The name of the label to remove

### Outputs
- Status: Confirmation of the label removal
- Error Message: Information if something goes wrong

### Possible use case
Updating issue categories when their status changes or correcting miscategorized issues.

## GitHub Assign Issue
### What it is
A tool for assigning GitHub issues to specific users.

### What it does
Assigns a specified GitHub user to any issue you have access to.

### How it works
Adds the specified user as an assignee to the issue identified by the URL.

### Inputs
- GitHub Credentials: Your authentication details for GitHub
- Issue URL: The web address of the issue
- Assignee: The username of the person to assign

### Outputs
- Status: Confirmation of the assignment
- Error Message: Information if something goes wrong

### Possible use case
Automatically assigning issues to team members based on their expertise or workload.

## GitHub Unassign Issue
### What it is
A tool for removing user assignments from GitHub issues.

### What it does
Removes specified users from being assigned to a GitHub issue.

### How it works
Removes the specified user from the list of assignees on the given issue.

### Inputs
- GitHub Credentials: Your authentication details for GitHub
- Issue URL: The web address of the issue
- Assignee: The username to remove from the assignment

### Outputs
- Status: Confirmation of the unassignment
- Error Message: Information if something goes wrong

### Possible use case
Redistributing workload or clearing assignments when team members are unavailable.
