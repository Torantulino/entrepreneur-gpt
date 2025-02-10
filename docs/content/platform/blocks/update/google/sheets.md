
# Google Sheets Integration Blocks

## Google Sheets Reader

### What it is
A tool that allows you to retrieve data from Google Sheets spreadsheets.

### What it does
Reads specified ranges of data from a Google Sheets spreadsheet and returns the content in an organized format.

### How it works
1. Connects to Google Sheets using your provided credentials
2. Locates the specified spreadsheet using its ID
3. Retrieves data from the specified range of cells
4. Returns the data as a structured list

### Inputs
- Credentials: Your Google account authentication details
- Spreadsheet ID: The unique identifier for your Google Sheet (found in the sheet's URL)
- Range: The cell range you want to read (e.g., "Sheet1!A1:B2")

### Outputs
- Result: The data retrieved from the spreadsheet, organized in rows and columns
- Error: Any error message if the operation wasn't successful

### Possible use case
Automatically collecting daily sales data from a team's shared spreadsheet for analysis or reporting.

## Google Sheets Writer

### What it is
A tool that enables you to write data into Google Sheets spreadsheets.

### What it does
Writes data into specified ranges of a Google Sheets spreadsheet, updating or replacing existing content.

### How it works
1. Connects to Google Sheets using your provided credentials
2. Locates the specified spreadsheet using its ID
3. Updates the specified range with your provided data
4. Returns information about the update operation

### Inputs
- Credentials: Your Google account authentication details
- Spreadsheet ID: The unique identifier for your Google Sheet (found in the sheet's URL)
- Range: The cell range where you want to write data (e.g., "Sheet1!A1:B2")
- Values: The data you want to write, organized in rows and columns

### Outputs
- Result: Details about the write operation, including number of cells, rows, and columns updated
- Error: Any error message if the operation wasn't successful

### Possible use case
Automatically updating a project status spreadsheet with daily progress metrics collected from various sources.
