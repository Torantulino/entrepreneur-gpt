
## CSV Reader

### What it is
A versatile tool that converts CSV (Comma-Separated Values) file contents into organized, structured data that's easy to work with.

### What it does
Reads and processes CSV file contents, transforming them into a structured format while offering various customization options like handling headers, skipping rows, and cleaning data.

### How it works
The tool takes your CSV content and breaks it down line by line, organizing each row's data into a neat, labeled structure. It can work with different types of CSV formats and gives you options to customize how the data is processed, such as removing extra spaces or skipping certain rows.

### Inputs
- File Contents: The actual text content of your CSV file
- Delimiter: The character that separates values in your file (default is comma)
- Quote Character: The character used to wrap text that contains special characters (default is double quote)
- Escape Character: The character used to mark special characters (default is backslash)
- Has Header: Whether your file includes column names in the first row (default is yes)
- Skip Rows: Number of rows to skip from the beginning of the file (default is 0)
- Strip Whitespace: Whether to remove extra spaces from values (default is yes)
- Skip Columns: List of columns you want to exclude from the results (default is none)

### Outputs
- Individual Row: Provides each row of data as it's processed, with values organized by column names
- Complete Dataset: Delivers all rows together as a single collection once processing is finished

### Possible use cases
- Importing contact lists from spreadsheets
- Processing financial data from exported reports
- Converting inventory spreadsheets into structured data
- Analyzing survey responses from CSV exports
- Transforming exported data tables into a more usable format
