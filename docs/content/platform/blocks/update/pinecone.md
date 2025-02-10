
# Pinecone Integration Blocks

## Pinecone Initializer

### What it is
A setup tool that creates or connects to a Pinecone vector database for storing and searching through information.

### What it does
Creates a new database index or connects to an existing one, setting up the necessary configuration for storing vector data.

### How it works
The block checks if the specified database index exists. If it doesn't, it creates a new one with your specified settings. If it does exist, it connects to the existing index.

### Inputs
- API Key: Your Pinecone authentication credentials
- Index Name: The name you want to give to your database index
- Dimension: The size of the vectors to be stored (default: 768)
- Metric: The method used to measure similarity between vectors (default: cosine)
- Cloud: The cloud provider to use (default: aws)
- Region: The geographical location of the database (default: us-east-1)

### Outputs
- Index: The name of the initialized database index
- Message: A status message indicating whether a new index was created or an existing one was connected

### Possible use case
Setting up a new semantic search system that needs a database to store and retrieve information efficiently.

## Pinecone Query

### What it is
A search tool that finds similar items in your Pinecone database using vector similarity.

### What it does
Searches through the database to find the most similar items to your query, returning both detailed results and combined text from the matches.

### How it works
Takes a query vector and searches the database for the most similar items, returning the top matches based on your specifications.

### Inputs
- API Key: Your Pinecone authentication credentials
- Query Vector: The vector representation of your search query
- Namespace: Optional organization space within the database (default: empty)
- Top K: Number of results to return (default: 3)
- Include Values: Whether to include vector values in results (default: false)
- Include Metadata: Whether to include additional information in results (default: true)
- Host: The database host address
- Index Name: The name of the database index to search

### Outputs
- Results: Detailed search results including matches and combined text
- Combined Results: A consolidated version of the matched text

### Possible use case
Implementing a semantic search feature that finds similar documents or content based on meaning rather than exact keyword matches.

## Pinecone Inserter

### What it is
A data upload tool that adds new information to your Pinecone database.

### What it does
Processes and uploads text chunks and their corresponding vector representations to the database, along with any additional metadata.

### How it works
Takes your text chunks and their vector representations, combines them with metadata, and uploads them to the specified database index.

### Inputs
- API Key: Your Pinecone authentication credentials
- Index: The name of the database index
- Chunks: List of text pieces to store
- Embeddings: Vector representations of the text chunks
- Namespace: Optional organization space within the database (default: empty)
- Metadata: Additional information to store with each vector (default: empty)

### Outputs
- Upsert Response: Confirmation message of successful upload

### Possible use case
Building a knowledge base by uploading and organizing document collections for later retrieval and searching.
