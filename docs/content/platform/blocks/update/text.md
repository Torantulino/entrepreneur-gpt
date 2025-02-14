
# Text Processing Blocks Documentation

## Match Text Pattern

### What it is
A text matching tool that checks if a given text matches a specific pattern.

### What it does
Examines input text against a specified pattern and routes the data to different outputs based on whether a match is found.

### How it works
The block takes your text and pattern, compares them (considering your case sensitivity preferences), and directs the data to either a positive or negative output path.

### Inputs
- Text: The text content you want to check
- Pattern: The pattern you want to find in the text
- Data: Information you want to pass through the block
- Case Sensitive: Whether uppercase and lowercase letters should be treated differently
- Dot All: Whether the dot character should match any character including newlines

### Outputs
- Positive: Receives the data when a pattern match is found
- Negative: Receives the data when no pattern match is found

### Possible use case
Filtering customer feedback messages to route complaints (containing specific keywords) to the urgent response team and other messages to the general response team.

## Extract Text Information

### What it is
A tool that pulls specific information out of text using patterns.

### What it does
Searches through text to find and extract specific pieces of information based on a given pattern.

### How it works
The block searches the input text for matches to your pattern and extracts either the whole match or a specific group you specify. It can find either the first match or all matches.

### Inputs
- Text: The text you want to extract information from
- Pattern: The pattern that describes what you want to extract
- Group: Which part of the match to extract
- Case Sensitive: Whether uppercase and lowercase letters should be treated differently
- Dot All: Whether the dot character should match any character including newlines
- Find All: Whether to find all matches or just the first one

### Outputs
- Positive: The extracted text when matches are found
- Negative: The original text when no matches are found

### Possible use case
Extracting all email addresses from a document or pulling specific data fields from formatted text entries.

## Fill Text Template

### What it is
A template-based text formatting tool that creates customized text using provided values.

### What it does
Creates formatted text by inserting provided values into a template structure.

### How it works
The block takes a template with placeholders and fills them with the values you provide, creating a complete text output.

### Inputs
- Values: A collection of named values to insert into the template
- Format: The template structure showing where to place the values

### Outputs
- Output: The final formatted text with all values inserted

### Possible use case
Creating personalized email messages by inserting customer names and specific details into a standard template.

## Combine Texts

### What it is
A text combination tool that joins multiple text pieces into a single text.

### What it does
Merges multiple separate text inputs into one unified text output, with an optional separator between them.

### How it works
The block takes your list of texts and joins them together, optionally placing a delimiter (separator) between each piece.

### Inputs
- Input: List of text pieces to combine
- Delimiter: Optional text to insert between combined pieces

### Outputs
- Output: The final combined text

### Possible use case
Combining multiple paragraphs into a single document or joining separate pieces of content with proper spacing or punctuation.
