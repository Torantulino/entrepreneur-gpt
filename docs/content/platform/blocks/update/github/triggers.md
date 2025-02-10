
## GitHub Pull Request Trigger

### What it is
A monitoring tool that watches for and responds to GitHub pull request activities in specified repositories.

### What it does
This block listens for various pull request events on a GitHub repository and provides detailed information about these events when they occur. It can track multiple types of pull request activities, such as when pull requests are opened, closed, edited, or updated.

### How it works
The block sets up a webhook connection with a specified GitHub repository. When pull request activities occur in the repository, GitHub sends information to this webhook. The block then processes this information and provides structured data about the event and the pull request.

### Inputs
- Repository Path: The GitHub repository to monitor (format: "owner/repository")
- Event Selections: Choose which pull request events to monitor:
  - Pull request opened
  - Pull request closed
  - Pull request edited
  - Pull request reopened
  - Changes pushed (synchronize)
  - Assignee changes
  - Label changes
  - Draft status changes
  - Lock status changes
  - Review request changes
  - Milestone changes
  - Auto-merge setting changes
- GitHub Credentials: Authentication details for accessing the repository

### Outputs
- Event Type: The specific type of pull request event that occurred
- Pull Request Number: The identifying number of the affected pull request
- Pull Request Details: Complete information about the pull request
- Pull Request URL: Direct link to the pull request on GitHub
- Triggered User: Information about the GitHub user who caused the event
- Complete Payload: Detailed technical information about the event
- Error Message: Information about any problems that occurred (if applicable)

### Possible use cases
1. Automatically notify team channels when new pull requests are opened
2. Track pull request status changes for project management
3. Generate reports on pull request activities
4. Trigger automated code review processes
5. Update project dashboards with real-time pull request information
