
# Time Management Blocks

## Current Time

### What it is
A tool that provides the current time in a customizable format.

### What it does
Returns the current time when triggered, allowing you to specify how the time should be displayed.

### How it works
When activated, it captures the current system time and formats it according to your specifications.

### Inputs
- Trigger: Any input that activates the block
- Format: How you want the time displayed (default is hours:minutes:seconds)

### Outputs
- Time: The current time in your specified format

### Possible use case
Creating a digital clock display or adding timestamps to automated messages.

## Current Date

### What it is
A tool that provides the current date with optional day adjustments.

### What it does
Returns the current date or a date offset by a specified number of days, in your preferred format.

### How it works
Captures today's date and can adjust it forward or backward by a specified number of days before displaying it in your chosen format.

### Inputs
- Trigger: Any input that activates the block
- Days Offset: Number of days to adjust from current date
- Format: How you want the date displayed (default is YYYY-MM-DD)

### Outputs
- Date: The formatted date based on your specifications

### Possible use case
Calculating due dates for projects or scheduling future events.

## Current Date and Time

### What it is
A combined tool that provides both the current date and time together.

### What it does
Returns the current date and time in a single, formatted output.

### How it works
Captures the current system date and time and presents them together in your specified format.

### Inputs
- Trigger: Any input that activates the block
- Format: How you want the date and time displayed (default is YYYY-MM-DD HH:MM:SS)

### Outputs
- Date and Time: The current date and time in your specified format

### Possible use case
Creating comprehensive timestamps for logging or recording event occurrences.

## Countdown Timer

### What it is
A timing tool that triggers a message after a specified duration.

### What it does
Waits for a set period and then outputs a custom message.

### How it works
Counts down the specified duration and delivers your message when the time is up.

### Inputs
- Message: The text to output when the timer finishes (default is "timer finished")
- Seconds: Number of seconds to wait
- Minutes: Number of minutes to wait
- Hours: Number of hours to wait
- Days: Number of days to wait

### Outputs
- Message: Your specified message, delivered after the countdown completes

### Possible use case
Setting up delayed notifications or scheduling automated actions after a specific waiting period.
