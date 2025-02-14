
## Step Through Items

### What it is
A logical component that helps you process lists or collections of items one at a time, like going through items in a shopping list one by one.

### What it does
Takes a collection of items (either as a list or a dictionary) and processes them individually, outputting each item along with its position or identifier in the sequence.

### How it works
The component accepts your collection of items and then:
1. Checks if you've provided items in any of the accepted formats
2. Goes through each item one by one
3. For each item, provides both the item itself and its position/identifier
4. Continues until all items have been processed

### Inputs
- Items: A list of items you want to process (like [1, 2, 3] or ["apple", "banana", "orange"])
- Items Object: A dictionary of items with labels (like {"fruit": "apple", "vegetable": "carrot"})
- Items String: A text version of your list or dictionary, useful when your data comes as formatted text

### Outputs
- Item: The current item being processed from your collection
- Key: The position (for lists) or label (for dictionaries) of the current item

### Possible use cases
- Processing a list of customer orders one at a time
- Going through a collection of files in a folder
- Handling survey responses individually
- Processing inventory items one by one
- Working through a series of tasks in sequence
