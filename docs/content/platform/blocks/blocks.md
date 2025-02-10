# AutoGPT Blocks Overview

AutoGPT uses a modular approach with various "blocks" to handle different tasks. These blocks are the building blocks of AutoGPT workflows, allowing users to create complex automations by combining simple, specialized components.

Below is a comprehensive list of all available blocks, categorized by their primary function. Click on any block name to view its detailed documentation.

## Basic Operations
| Block Name | Description |
|------------|-------------|
| [Store Value](update/basic.md#store-value) | Stores and forwards a value |
| [Print to Console](update/basic.md#print-to-console) | Outputs text to the console for debugging |
| [Find in Dictionary](update/basic.md#find-in-dictionary) | Looks up a value in a dictionary or list |
| [Agent Input](update/basic.md#agent-input) | Accepts user input in a workflow |
| [Agent Output](update/basic.md#agent-output) | Records and formats workflow results |
| [Add to Dictionary](update/basic.md#add-to-dictionary) | Adds a new key-value pair to a dictionary |
| [Add to List](update/basic.md#add-to-list) | Adds a new entry to a list |
| [Note](update/basic.md#note) | Displays a sticky note in the workflow |
| [Create Dictionary](update/basic.md#create-dictionary) | Creates a new dictionary with specified key-value pairs |
| [Create List](update/basic.md#create-list) | Creates a new list with specified values |

## Data Processing
| Block Name | Description |
|------------|-------------|
| [Read CSV](csv.md#read-csv) | Processes and extracts data from CSV files |
| [Data Sampling](sampling.md#data-sampling) | Selects a subset of data using various sampling methods |

## Text Processing
| Block Name | Description |
|------------|-------------|
| [Match Text Pattern](text.md#match-text-pattern) | Checks if text matches a specified pattern |
| [Extract Text Information](text.md#extract-text-information) | Extracts specific information from text using patterns |
| [Fill Text Template](text.md#fill-text-template) | Populates a template with provided values |
| [Combine Texts](text.md#combine-texts) | Merges multiple text inputs into one |
| [Text Decoder](decoder_block.md#text-decoder) | Converts encoded text into readable format |

## AI and Language Models
| Block Name | Description |
|------------|-------------|
| [AI Structured Response Generator](llm.md#ai-structured-response-generator) | Generates structured responses using LLMs |
| [AI Text Generator](llm.md#ai-text-generator) | Produces text responses using LLMs |
| [AI Text Summarizer](llm.md#ai-text-summarizer) | Summarizes long texts using LLMs |
| [AI Conversation](llm.md#ai-conversation) | Facilitates multi-turn conversations with LLMs |
| [AI List Generator](llm.md#ai-list-generator) | Creates lists based on prompts using LLMs |
| [AI Music Generator](update/ai_music_generator.md#ai-music-generator) | Creates unique music using AI based on text descriptions |

## Web and API Interactions
| Block Name | Description |
|------------|-------------|
| [Send Web Request](update/http.md#web-request-sender) | Makes HTTP requests to specified web addresses |
| [HTTP Request Handler](update/helpers/http.md#http-request-handler) | Simplifies making HTTP GET requests to web services |
| [Read RSS Feed](rss.md#read-rss-feed) | Retrieves and processes entries from RSS feeds |
| [Get Weather Information](search.md#get-weather-information) | Fetches current weather data for a location |
| [Google Maps Search](google_maps.md#google-maps-search) | Searches for local businesses using Google Maps API |

## Social Media and Content
| Block Name | Description |
|------------|-------------|
| [Get Reddit Posts](reddit.md#get-reddit-posts) | Retrieves posts from specified subreddits |
| [Post Reddit Comment](reddit.md#post-reddit-comment) | Posts comments on Reddit |
| [Publish to Medium](medium.md#publish-to-medium) | Publishes content directly to Medium |
| [Read Discord Messages](discord.md#read-discord-messages) | Retrieves messages from Discord channels |
| [Send Discord Message](discord.md#send-discord-message) | Sends messages to Discord channels |

## Search and Information Retrieval
| Block Name | Description |
|------------|-------------|
| [Get Wikipedia Summary](search.md#get-wikipedia-summary) | Fetches summaries of topics from Wikipedia |
| [Search The Web](search.md#search-the-web) | Performs web searches and returns results |
| [Extract Website Content](search.md#extract-website-content) | Retrieves and extracts content from websites |

## Time and Date
| Block Name | Description |
|------------|-------------|
| [Get Current Time](time_blocks.md#get-current-time) | Provides the current time |
| [Get Current Date](time_blocks.md#get-current-date) | Provides the current date |
| [Get Current Date and Time](time_blocks.md#get-current-date-and-time) | Provides both current date and time |
| [Countdown Timer](time_blocks.md#countdown-timer) | Acts as a countdown timer |

## Math and Calculations
| Block Name | Description |
|------------|-------------|
| [Calculator](maths.md#calculator) | Performs basic mathematical operations |
| [Count Items](maths.md#count-items) | Counts items in a collection |

## Media Generation
| Block Name | Description |
|------------|-------------|
| [Ideogram Model](update/ideogram.md#ideogram-model) | Generates images based on text prompts |
| [Create Talking Avatar Video](talking_head.md#create-talking-avatar-video) | Creates videos with talking avatars |
| [Unreal Text to Speech](text_to_speech_block.md#unreal-text-to-speech) | Converts text to speech using Unreal Speech API |
| [AI Shortform Video Creator](ai_shortform_video_block.md#ai-shortform-video-creator) | Generates short-form videos using AI |
| [Replicate Flux Advanced Model](replicate_flux_advanced.md#replicate-flux-advanced-model) | Creates images using Replicate's Flux models |
| [AI Music Generator](update/ai_music_generator.md#ai-music-generator) | Creates unique music using AI based on text descriptions |

## Miscellaneous
| Block Name | Description |
|------------|-------------|
| [Transcribe YouTube Video](youtube.md#transcribe-youtube-video) | Transcribes audio from YouTube videos |
| [Send Email](email_block.md#send-email) | Sends emails using SMTP |
| [Condition Block](update/branching.md#condition-block) | Evaluates conditions for workflow branching |
| [Step Through Items](update/iteration.md#step-through-items) | Iterates through lists or dictionaries |

## HubSpot Integration
| Block Name | Description |
|------------|-------------|
| [HubSpot Company Manager](update/hubspot/company.md#hubspot-company-manager) | Manages company records in HubSpot CRM |
| [HubSpot Contact Manager](update/hubspot/contact.md#hubspot-contact-manager) | Manages contact information in HubSpot CRM |
| [HubSpot Engagement Manager](update/hubspot/engagement.md#hubspot-engagement-manager) | Tracks and manages customer interactions in HubSpot |

## Code Management
| Block Name | Description |
|------------|-------------|
| [Code Executor](update/code_executor.md#code-executor) | Executes code snippets in a secure sandbox environment |

## Compass Integration
| Block Name | Description |
|------------|-------------|
| [Compass AI Trigger](update/compass/triggers.md#compass-ai-trigger) | Processes transcription content from Compass hardware |

## Google Services
| Block Name | Description |
|------------|-------------|
| [Gmail Read](google/gmail.md#gmail-read) | Retrieves and reads emails from a Gmail account |
| [Gmail Send](google/gmail.md#gmail-send) | Sends emails using a Gmail account |
| [Gmail List Labels](google/gmail.md#gmail-list-labels) | Retrieves all labels from a Gmail account |
| [Gmail Add Label](google/gmail.md#gmail-add-label) | Adds a label to a specific email in a Gmail account |
| [Gmail Remove Label](google/gmail.md#gmail-remove-label) | Removes a label from a specific email in a Gmail account |
| [Google Sheets Read](google/sheet.md#google-sheets-read) | Reads data from a Google Sheets spreadsheet |
| [Google Sheets Write](google/sheet.md#google-sheets-write) | Writes data to a Google Sheets spreadsheet |
| [Google Maps Search](google_maps.md#google-maps-search) | Searches for local businesses using the Google Maps API |

## GitHub Integration
| Block Name | Description |
|------------|-------------|
| [GitHub Comment](github/issues.md#github-comment) | Posts comments on GitHub issues or pull requests |
| [GitHub Make Issue](github/issues.md#github-make-issue) | Creates new issues on GitHub repositories |
| [GitHub Read Issue](github/issues.md#github-read-issue) | Retrieves information about a specific GitHub issue |
| [GitHub List Issues](github/issues.md#github-list-issues) | Retrieves a list of issues from a GitHub repository |
| [GitHub Add Label](github/issues.md#github-add-label) | Adds a label to a GitHub issue or pull request |
| [GitHub Remove Label](github/issues.md#github-remove-label) | Removes a label from a GitHub issue or pull request |
| [GitHub Assign Issue](github/issues.md#github-assign-issue) | Assigns a user to a GitHub issue |
| [GitHub List Tags](github/repo.md#github-list-tags) | Retrieves and lists all tags for a specified GitHub repository |
| [GitHub List Branches](github/repo.md#github-list-branches) | Retrieves and lists all branches for a specified GitHub repository |
| [GitHub List Discussions](github/repo.md#github-list-discussions) | Retrieves and lists recent discussions for a specified GitHub repository |
| [GitHub Make Branch](github/repo.md#github-make-branch) | Creates a new branch in a GitHub repository |
| [GitHub Delete Branch](github/repo.md#github-delete-branch) | Deletes a specified branch from a GitHub repository |
| [GitHub List Pull Requests](github/pull_requests.md#github-list-pull-requests) | Retrieves a list of pull requests from a specified GitHub repository |
| [GitHub Make Pull Request](github/pull_requests.md#github-make-pull-request) | Creates a new pull request in a specified GitHub repository |
| [GitHub Read Pull Request](github/pull_requests.md#github-read-pull-request) | Retrieves detailed information about a specific GitHub pull request |
| [GitHub Assign PR Reviewer](github/pull_requests.md#github-assign-pr-reviewer) | Assigns a reviewer to a specific GitHub pull request |
| [GitHub Unassign PR Reviewer](github/pull_requests.md#github-unassign-pr-reviewer) | Removes an assigned reviewer from a specific GitHub pull request |
| [GitHub List PR Reviewers](github/pull_requests.md#github-list-pr-reviewers) | Retrieves a list of all assigned reviewers for a specific GitHub pull request |

## Twitter Integration
| Block Name | Description |
|------------|-------------|
| [Twitter Post Tweet](twitter/twitter.md#twitter-post-tweet-block) | Creates a tweet on Twitter with text content and optional attachments including media, polls, quotes, or deep links |
| [Twitter Delete Tweet](twitter/twitter.md#twitter-delete-tweet-block) | Deletes a specified tweet using its tweet ID |
| [Twitter Search Recent Tweets](twitter/twitter.md#twitter-search-recent-tweets-block) | Searches for tweets matching specified criteria with options for filtering and pagination |
| [Twitter Get Quote Tweets](twitter/twitter.md#twitter-get-quote-tweets-block) | Gets tweets that quote a specified tweet ID with options for pagination and filtering |
| [Twitter Retweet](twitter/twitter.md#twitter-retweet-block) | Creates a retweet of a specified tweet using its tweet ID |
| [Twitter Remove Retweet](twitter/twitter.md#twitter-remove-retweet-block) | Removes an existing retweet of a specified tweet |
| [Twitter Get Retweeters](twitter/twitter.md#twitter-get-retweeters-block) | Gets list of users who have retweeted a specified tweet with pagination and filtering options |
| [Twitter Get User Mentions](twitter/twitter.md#twitter-get-user-mentions-block) | Gets tweets where a specific user is mentioned using their user ID |
| [Twitter Get Home Timeline](twitter/twitter.md#twitter-get-home-timeline-block) | Gets recent tweets and retweets from authenticated user and followed accounts |
| [Twitter Get User](twitter/twitter.md#twitter-get-user-block) | Gets detailed profile information for a single Twitter user |
| [Twitter Get Users](twitter/twitter.md#twitter-get-users-block) | Gets profile information for multiple Twitter users (up to 100) |
| [Twitter Search Spaces](twitter/twitter.md#twitter-search-spaces-block) | Searches for Twitter Spaces matching title keywords with state filtering |
| [Twitter Get Spaces](twitter/twitter.md#twitter-get-spaces-block) | Gets information about multiple Twitter Spaces by Space IDs or creator IDs |
| [Twitter Get Space By Id](twitter/twitter.md#twitter-get-space-by-id-block) | Gets detailed information about a single Twitter Space |
| [Twitter Get Space Tweets](twitter/twitter.md#twitter-get-space-tweets-block) | Gets tweets that were shared during a Twitter Space session |
| [Twitter Follow List](twitter/twitter.md#twitter-follow-list-block) | Follows a Twitter List using its List ID |
| [Twitter Unfollow List](twitter/twitter.md#twitter-unfollow-list-block) | Unfollows a previously followed Twitter List |
| [Twitter Get List](twitter/twitter.md#twitter-get-list-block) | Gets detailed information about a specific Twitter List |
| [Twitter Get Owned Lists](twitter/twitter.md#twitter-get-owned-lists-block) | Gets all Twitter Lists owned by a specified user |
| [Twitter Get List Members](twitter/twitter.md#twitter-get-list-members-block) | Gets information about members of a specified Twitter List |
| [Twitter Add List Member](twitter/twitter.md#twitter-add-list-member-block) | Adds a specified user as a member to a Twitter List |
| [Twitter Remove List Member](twitter/twitter.md#twitter-remove-list-member-block) | Removes a specified user from a Twitter List |
| [Twitter Get List Tweets](twitter/twitter.md#twitter-get-list-tweets-block) | Gets tweets posted within a specified Twitter List |
| [Twitter Create List](twitter/twitter.md#twitter-create-list-block) | Creates a new Twitter List with specified name and settings |
| [Twitter Update List](twitter/twitter.md#twitter-update-list-block) | Updates name and/or description of an existing Twitter List |
| [Twitter Delete List](twitter/twitter.md#twitter-delete-list-block) | Deletes a specified Twitter List |
| [Twitter Pin List](twitter/twitter.md#twitter-pin-list-block) | Pins a Twitter List to appear at top of Lists |
| [Twitter Unpin List](twitter/twitter.md#twitter-unpin-list-block) | Removes a Twitter List from pinned Lists |
| [Twitter Get Pinned Lists](twitter/twitter.md#twitter-get-pinned-lists-block) | Gets all Twitter Lists that are currently pinned |
| Twitter List Get Followers | Working... Gets all followers of a specified Twitter List |
| Twitter Get Followed Lists | Working... Gets all Lists that a user follows |
| Twitter Get DM Events | Working... Retrieves direct message events for a user |
| Twitter Send Direct Message | Working... Sends a direct message to a specified user |
| Twitter Create DM Conversation | Working... Creates a new direct message conversation |

## Todoist Integration
| Block Name | Description |
|------------|-------------|
| [Todoist Create Label](todoist.md#todoist-create-label) | Creates a new label in Todoist |
| [Todoist List Labels](todoist.md#todoist-list-labels) | Retrieves all personal labels from Todoist |
| [Todoist Get Label](todoist.md#todoist-get-label) | Retrieves a specific label by ID |
| [Todoist Create Task](todoist.md#todoist-create-task) | Creates a new task in Todoist |
| [Todoist Get Tasks](todoist.md#todoist-get-tasks) | Retrieves active tasks from Todoist |
| [Todoist Update Task](todoist.md#todoist-update-task) | Updates an existing task |
| [Todoist Close Task](todoist.md#todoist-close-task) | Completes/closes a task |
| [Todoist Reopen Task](todoist.md#todoist-reopen-task) | Reopens a completed task |
| [Todoist Delete Task](todoist.md#todoist-delete-task) | Permanently deletes a task |
| [Todoist List Projects](todoist.md#todoist-list-projects) | Retrieves all projects from Todoist |
| [Todoist Create Project](todoist.md#todoist-create-project) | Creates a new project in Todoist |
| [Todoist Get Project](todoist.md#todoist-get-project) | Retrieves details for a specific project |
| [Todoist Update Project](todoist.md#todoist-update-project) | Updates an existing project |
| [Todoist Delete Project](todoist.md#todoist-delete-project) | Deletes a project and its contents |
| [Todoist List Collaborators](todoist.md#todoist-list-collaborators) | Retrieves collaborators on a project |
| [Todoist List Sections](todoist.md#todoist-list-sections) | Retrieves sections from Todoist |
| [Todoist Get Section](todoist.md#todoist-get-section) | Retrieves details for a specific section |
| [Todoist Delete Section](todoist.md#todoist-delete-section) | Deletes a section and its tasks |
| [Todoist Create Comment](todoist.md#todoist-create-comment) | Creates a new comment on a task or project |
| [Todoist Get Comments](todoist.md#todoist-get-comments) | Retrieves all comments for a task or project |
| [Todoist Get Comment](todoist.md#todoist-get-comment) | Retrieves a specific comment by ID |
| [Todoist Update Comment](todoist.md#todoist-update-comment) | Updates an existing comment |
| [Todoist Delete Comment](todoist.md#todoist-delete-comment) | Deletes a comment |

This comprehensive list covers all the blocks available in AutoGPT. Each block is designed to perform a specific task, and they can be combined to create powerful, automated workflows. For more detailed information on each block, click on its name to view the full documentation.
