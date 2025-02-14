
# Basic Blocks Documentation

## Store Value

### What it is
A data storage and forwarding component that can hold and pass along values.

### What it does
Stores a provided value and makes it available for reuse without modification.

### How it works
Takes an input value and either stores it directly or uses a pre-stored value, then forwards it as output.

### Inputs
- Input: The value to be stored (if no data is provided)
- Data: A pre-stored value to use instead of the input (optional)

### Outputs
- Output: The stored value

### Possible use case
Storing a user's name that needs to be used multiple times throughout a workflow.

## Print to Console

### What it is
A debugging tool that displays information during operation.

### What it does
Prints text messages to the console for monitoring and debugging purposes.

### How it works
Takes a text message and displays it in the console with a "Print: " prefix.

### Inputs
- Text: The message to be displayed

### Outputs
- Status: Confirmation that the message was printed

### Possible use case
Monitoring the progress of a workflow by printing status updates.

## Find in Dictionary

### What it is
A search tool for looking up values in data structures.

### What it does
Searches for and retrieves values from dictionaries, lists, or objects using a specified key.

### How it works
Takes a data structure and a key, then attempts to find and return the corresponding value.

### Inputs
- Input: The data structure to search in
- Key: The key to look up

### Outputs
- Output: The found value
- Missing: The original input when the key isn't found

### Possible use case
Looking up a user's details from a database response using their ID.

## Agent Input

### What it is
An interface for collecting input values from users.

### What it does
Provides a structured way to gather and validate user input with optional constraints.

### How it works
Creates an input field with customizable properties and validates the entered value.

### Inputs
- Name: Identifier for the input
- Value: The actual input value
- Title: Display name (optional)
- Description: Help text (optional)
- Placeholder Values: Suggested values
- Limit to Placeholder Values: Restrict input to suggestions only

### Outputs
- Result: The collected input value

### Possible use case
Creating a form field for users to enter their age with suggested ranges.

## Agent Output

### What it is
A display component for showing results to users.

### What it does
Formats and presents output values in a user-friendly way.

### How it works
Takes a value and optional formatting instructions to display the result.

### Inputs
- Value: The data to display
- Name: Identifier for the output
- Title: Display name
- Description: Additional information
- Format: Custom formatting instructions

### Outputs
- Output: The formatted result

### Possible use case
Displaying the results of a calculation with proper formatting and explanation.

## Add to Dictionary

### What it is
A tool for adding new entries to dictionaries.

### What it does
Adds one or more key-value pairs to an existing or new dictionary.

### How it works
Takes a dictionary and new entries, then creates an updated dictionary with the additions.

### Inputs
- Dictionary: Existing dictionary (optional)
- Key: New entry key
- Value: New entry value
- Entries: Multiple entries to add

### Outputs
- Updated Dictionary: The modified dictionary
- Error: Any error messages

### Possible use case
Adding a new user preference to an existing settings dictionary.

## Add to List

### What it is
A tool for adding items to lists.

### What it does
Adds one or more items to an existing or new list at specified positions.

### How it works
Takes a list and new items, then creates an updated list with the additions.

### Inputs
- List: Existing list (optional)
- Entry: Single item to add
- Entries: Multiple items to add
- Position: Where to insert items

### Outputs
- Updated List: The modified list
- Error: Any error messages

### Possible use case
Adding new tasks to a todo list at specific priorities.

## Note

### What it is
A documentation tool for adding explanatory notes.

### What it does
Displays text as a sticky note in the workflow.

### How it works
Takes text input and displays it as a note for documentation purposes.

### Inputs
- Text: The note content

### Outputs
- Output: The displayed note text

### Possible use case
Adding explanatory comments to describe complex workflow steps.

## Create Dictionary

### What it is
A dictionary creation tool.

### What it does
Creates a new dictionary with specified key-value pairs.

### How it works
Takes a set of key-value pairs and combines them into a new dictionary.

### Inputs
- Values: Key-value pairs for the dictionary

### Outputs
- Dictionary: The created dictionary
- Error: Any error messages

### Possible use case
Creating a new user profile with multiple fields.

## Create List

### What it is
A list creation tool.

### What it does
Creates a new list with specified values.

### How it works
Takes a set of values and combines them into a new list.

### Inputs
- Values: Items for the list

### Outputs
- List: The created list
- Error: Any error messages

### Possible use case
Creating a new shopping list with multiple items.
