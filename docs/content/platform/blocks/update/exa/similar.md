
## Exa Find Similar

### What it is
A tool that finds web content similar to a specified URL using Exa's content discovery technology.

### What it does
This block searches across the web to find content that is similar to a given webpage. It can filter results based on various criteria such as domains, dates, and specific text patterns, making it highly customizable for different search needs.

### How it works
When you provide a URL, the block analyzes the content and searches Exa's database to find similar content across the web. It applies any specified filters (such as date ranges or domain restrictions) and returns a list of matching documents, ranked by similarity.

### Inputs
- URL: The webpage address you want to find similar content for
- Number of Results: How many similar items you want to receive (default is 10)
- Include Domains: List of website domains to specifically search within
- Exclude Domains: List of website domains to ignore in the search
- Start Crawl Date: Earliest date from which to consider when content was discovered
- End Crawl Date: Latest date from which to consider when content was discovered
- Start Published Date: Earliest publication date to consider
- End Published Date: Latest publication date to consider
- Include Text: Specific text patterns to look for (limited to 5 words)
- Exclude Text: Specific text patterns to exclude (limited to 5 words)
- Content Settings: Advanced settings for how content should be retrieved

### Outputs
- Results: A list of similar documents, each containing:
  - Title of the page
  - URL of the page
  - Publication date
  - Author information
  - Similarity score

### Possible use cases
- A content creator researching similar articles in their field
- A marketing professional tracking competitive content
- A researcher finding related academic papers
- A news organization identifying similar coverage of a story
- A website owner finding potentially duplicate or plagiarized content
