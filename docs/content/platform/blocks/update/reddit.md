
# Reddit Interaction Blocks

## Get Reddit Posts

### What it is
A tool that retrieves posts from a specified subreddit with customizable filtering options.

### What it does
Fetches recent posts from any specified subreddit, allowing you to control how many posts to retrieve and filter them based on time or specific post IDs.

### How it works
The block connects to Reddit using provided credentials, navigates to the specified subreddit, and retrieves posts based on your settings. It can limit the number of posts retrieved and filter them based on how recent they are.

### Inputs
- Subreddit: The name of the subreddit to fetch posts from
- Reddit Credentials: Authentication details needed to access Reddit
- Last Minutes (optional): Only retrieve posts from the last X minutes
- Last Post (optional): Stop retrieving posts when reaching a specific post ID
- Post Limit (optional): Maximum number of posts to retrieve (defaults to 10)

### Outputs
- Post: Information about each Reddit post, including:
  * Post ID
  * Subreddit name
  * Post title
  * Post content

### Possible use case
Monitoring a cryptocurrency subreddit for recent discussions about market trends, retrieving the last 20 posts from the past hour to analyze community sentiment.

## Post Reddit Comment

### What it is
A tool that posts comments on Reddit posts automatically.

### What it does
Creates and posts comments on specific Reddit posts using provided credentials and comment content.

### How it works
The block takes your Reddit credentials and comment information, connects to Reddit, finds the specified post, and adds your comment to that post.

### Inputs
- Reddit Credentials: Authentication details needed to access Reddit
- Comment Data: Contains:
  * Post ID to comment on
  * Comment text to post

### Outputs
- Comment ID: The unique identifier of the posted comment

### Possible use case
Automatically responding to customer support queries on your company's subreddit with helpful information or acknowledgments of their posts.

