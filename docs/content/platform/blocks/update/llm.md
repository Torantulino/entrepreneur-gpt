
# Language Model Blocks Documentation

## AI Structured Response Generator

### What it is
A sophisticated AI component that generates structured, formatted responses using various language models.

### What it does
Converts user prompts into structured data responses, ensuring the output follows a specific format defined by the user.

### How it works
The component sends your prompt to an AI model, along with formatting instructions, and ensures the response matches your required structure. It will retry multiple times if the response isn't properly formatted.

### Inputs
- Prompt: The main question or instruction for the AI
- Expected Format: The structure you want the response to follow
- Model: Choice of AI model to use
- System Prompt: Additional context or instructions for the AI
- Conversation History: Previous messages for context
- Retry Count: Number of attempts to get a properly formatted response
- Prompt Values: Variables to insert into the prompt

### Outputs
- Response: The structured data response from the AI
- Error: Any error messages if the process fails

### Possible use case
Converting unstructured customer feedback into categorized data with specific fields like sentiment, main topics, and action items.

## AI Text Generator

### What it is
A straightforward tool for generating natural language text responses.

### What it does
Processes your prompt and returns a natural language response without any specific formatting requirements.

### How it works
Sends your prompt to an AI model and returns the response as plain text, handling all the technical details of the AI interaction.

### Inputs
- Prompt: Your question or instruction
- Model: Choice of AI model
- System Prompt: Additional context or instructions
- Prompt Values: Variables to insert into the prompt

### Outputs
- Response: The generated text
- Error: Any error messages

### Possible use case
Generating product descriptions, creative writing, or answering general questions.

## AI Text Summarizer

### What it is
A tool that condenses long texts into shorter, meaningful summaries.

### What it does
Processes long pieces of text and creates concise summaries while maintaining the most important information.

### How it works
Breaks down long text into manageable chunks, summarizes each chunk, and then combines these summaries into a final, coherent summary.

### Inputs
- Text: The long text to summarize
- Model: Choice of AI model
- Focus: Specific topic to focus on in the summary
- Style: Format of the summary (concise, detailed, bullet points, or numbered list)
- Max Tokens: Maximum length of the summary
- Chunk Overlap: How much overlap to maintain between chunks for context

### Outputs
- Summary: The final summarized text
- Error: Any error messages

### Possible use case
Summarizing long research papers, articles, or reports into brief executive summaries.

## AI Conversation

### What it is
A tool for managing multi-turn conversations with AI models.

### What it does
Maintains a conversation thread with an AI, keeping track of context and previous messages.

### How it works
Sends the entire conversation history to the AI model with each new message, ensuring responses remain contextually relevant.

### Inputs
- Messages: List of previous conversation messages
- Model: Choice of AI model
- Max Tokens: Maximum length of responses

### Outputs
- Response: The AI's reply to the conversation
- Error: Any error messages

### Possible use case
Creating interactive chatbots or virtual assistants that maintain context throughout a conversation.

## AI List Generator

### What it is
A specialized tool for creating lists from text or prompts.

### What it does
Generates organized lists based on provided information or creates new lists based on specific topics.

### How it works
Analyzes source data or follows prompt instructions to create structured lists, validating the format and ensuring proper list generation.

### Inputs
- Focus: The main topic or purpose of the list
- Source Data: Optional text to extract list items from
- Model: Choice of AI model
- Max Retries: Number of attempts to generate a valid list
- Max Tokens: Maximum length of the generated list

### Outputs
- Generated List: The complete list of items
- List Item: Individual items from the list
- Error: Any error messages

### Possible use case
Extracting key points from meeting notes or creating organized lists of items from unstructured text data.
