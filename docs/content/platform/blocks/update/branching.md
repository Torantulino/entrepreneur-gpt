
## Condition Block

### What it is
A logical comparison tool that helps make decisions based on comparing two values.

### What it does
Compares two values using standard comparison operators (equals, not equals, greater than, less than, etc.) and produces different outputs based on whether the comparison is true or false.

### How it works
1. Takes two values and compares them using the selected operator
2. Determines if the comparison is true or false
3. Outputs the result and the appropriate value based on the comparison outcome
4. If custom output values aren't specified, uses the input values as defaults

### Inputs
- First Value: Any value you want to compare (numbers, text, or true/false values)
- Comparison Operator: The type of comparison to perform (equals, not equals, greater than, less than, etc.)
- Second Value: The value to compare against the first value
- True Result Value (Optional): Custom value to output if the comparison is true
- False Result Value (Optional): Custom value to output if the comparison is false

### Outputs
- Comparison Result: Whether the comparison was true or false
- True Output: The value produced when the comparison is true
- False Output: The value produced when the comparison is false

### Possible use cases
- Creating an age-restricted content filter: Compare user's age against a minimum required age
- Price comparison system: Check if a product's price is below a certain threshold
- Temperature control: Determine if current temperature is within acceptable range
- Grade assessment: Evaluate if a student's score meets passing criteria
- Inventory management: Check if stock levels are below reorder point
