
## Publish to Medium

### What it is
A tool that enables automatic publication of content to Medium's blogging platform, allowing for various publication settings and content management options.

### What it does
This block takes your content and publishes it to Medium as a new post. It can handle different types of content formats, manage publication status, and provides options for content licensing and reader notifications.

### How it works
The block connects to your Medium account using your credentials, processes your content according to your specified settings, and creates a new post on Medium. It then returns the details of the published post, including its URL and publication time.

### Inputs
- Author ID: Your unique Medium author identifier
- Title: The headline for your Medium post
- Content: The main body of your post
- Content Format: Specify whether your content is in HTML or Markdown format
- Tags: Up to 5 keywords to categorize your post
- Original URL: Optional link to where the content was first published
- Publication Status: Choose between public, draft, or unlisted
- License Type: Specify the copyright terms for your content
- Notify Followers: Choose whether to alert your followers about the new post
- Credentials: Your Medium API access information

### Outputs
- Post ID: A unique identifier for your published post
- Post URL: The direct link to your post on Medium
- Publication Time: When the post was published
- Error Message: Information about any issues that occurred during publication

### Possible use cases
- Automatically republish blog content to Medium
- Create draft posts for team review before publication
- Maintain a consistent content schedule across platforms
- Cross-post content while maintaining proper attribution
- Schedule content releases with specific visibility settings
