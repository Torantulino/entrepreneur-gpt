
# Web Search and Content Extraction Blocks

## Search The Web

### What it is
A tool that performs web searches using the Jina.ai search engine.

### What it does
This block takes a search query and returns comprehensive results from across the internet, including content from the top 5 relevant URLs.

### How it works
When you provide a search query, the block sends it to Jina.ai's search service, which scans the internet and returns the most relevant results. The process is similar to using a regular search engine, but it's designed to be integrated into automated workflows.

### Inputs
- Credentials: Your Jina.ai authentication details
- Query: The text you want to search for on the internet

### Outputs
- Results: A collection of search findings including content from the most relevant web pages
- Error: Any error message if the search wasn't successful

### Possible use case
A researcher could use this block to automatically gather information about a specific topic, such as "renewable energy trends," and receive comprehensive search results from multiple sources in one go.

## Extract Website Content

### What it is
A tool that extracts readable content from any website URL.

### What it does
This block visits a specified webpage and pulls out the main content, removing unnecessary elements like advertisements and navigation menus.

### How it works
When given a URL, the block either performs a direct content extraction (raw mode) or uses Jina.ai's specialized reader service to intelligently extract the most relevant content from the webpage.

### Inputs
- Credentials: Your Jina.ai authentication details
- URL: The web address of the page you want to extract content from
- Raw Content: A toggle that determines whether to use basic extraction or Jina.ai's enhanced reader (advanced option)

### Outputs
- Content: The extracted text from the webpage
- Error: Any error message if the content couldn't be retrieved

### Possible use case
A content curator could use this block to automatically extract articles from various news websites, getting clean, readable content without the clutter of advertisements and sidebars.
