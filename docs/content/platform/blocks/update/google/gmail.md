
# Gmail Integration Blocks

## Gmail Reader

### What it is
A tool that reads and retrieves emails from your Gmail account.

### What it does
Fetches emails based on search criteria and provides detailed information about each email, including subject, sender, content, and attachments.

### How it works
Connects to your Gmail account, searches for emails matching your criteria, and returns both the email content and metadata in an organized format.

### Inputs
- Credentials: Your Gmail account access permissions
- Search Query: How to filter emails (e.g., "is:unread" for unread emails)
- Maximum Results: How many emails to retrieve at once

### Outputs
- Email: Individual email data including subject, sender, content, and attachments
- Emails: List of multiple email data
- Error: Any error messages if something goes wrong

### Possible use case
Automatically monitoring incoming emails for important messages or creating a custom email dashboard.

## Gmail Sender

### What it is
A tool for sending emails through your Gmail account.

### What it does
Composes and sends emails to specified recipients with custom subjects and content.

### How it works
Uses your Gmail account to create and send new email messages to designated recipients.

### Inputs
- Credentials: Your Gmail account access permissions
- To: Recipient's email address
- Subject: Email subject line
- Body: Email content

### Outputs
- Result: Confirmation of email sending
- Error: Any error messages if something goes wrong

### Possible use case
Sending automated notifications or responses based on specific triggers.

## Gmail Label Lister

### What it is
A tool that shows all labels in your Gmail account.

### What it does
Retrieves and displays a complete list of all labels (categories) in your Gmail account.

### How it works
Connects to Gmail and fetches all existing labels, both system-created and custom.

### Inputs
- Credentials: Your Gmail account access permissions

### Outputs
- Result: List of all Gmail labels
- Error: Any error messages if something goes wrong

### Possible use case
Reviewing available labels before setting up email organization rules.

## Gmail Label Adder

### What it is
A tool that adds labels to specific emails in Gmail.

### What it does
Applies specified labels to individual email messages for organization.

### How it works
Takes an email message and a label name, then applies that label to the message.

### Inputs
- Credentials: Your Gmail account access permissions
- Message ID: The specific email to label
- Label Name: The label to apply

### Outputs
- Result: Confirmation of label addition
- Error: Any error messages if something goes wrong

### Possible use case
Automatically categorizing incoming emails based on content or sender.

## Gmail Label Remover

### What it is
A tool that removes labels from specific emails in Gmail.

### What it does
Removes specified labels from individual email messages.

### How it works
Takes an email message and a label name, then removes that label from the message.

### Inputs
- Credentials: Your Gmail account access permissions
- Message ID: The specific email to modify
- Label Name: The label to remove

### Outputs
- Result: Confirmation of label removal
- Error: Any error messages if something goes wrong

### Possible use case
Cleaning up email categorization or updating email status after processing.
