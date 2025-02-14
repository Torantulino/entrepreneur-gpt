
# Search Blocks Documentation

## Wikipedia Summary

### What it is
A tool that retrieves concise summaries of topics from Wikipedia.

### What it does
This block fetches and returns a summary of any specified topic using Wikipedia's API service.

### How it works
When you provide a topic, the block connects to Wikipedia's servers, searches for the topic, and returns a condensed version of the article's main content.

### Inputs
- Topic: The subject you want to learn about (e.g., "Artificial Intelligence", "Solar System")

### Outputs
- Summary: A concise explanation of the requested topic
- Error: A message explaining what went wrong if the summary couldn't be retrieved

### Possible use case
A student researching various topics for a school project could quickly gather basic information about multiple subjects without having to read entire Wikipedia articles.

## Weather Information

### What it is
A weather information retrieval system that connects to OpenWeatherMap's service.

### What it does
This block fetches current weather conditions for any specified location, including temperature, humidity, and general weather conditions.

### How it works
The block takes your desired location, connects to OpenWeatherMap's service using your API credentials, and returns current weather data in your preferred temperature format.

### Inputs
- Location: The place you want weather information for (e.g., "New York", "London")
- API Credentials: Your OpenWeatherMap API access information
- Temperature Format: Choose between Celsius (default) or Fahrenheit

### Outputs
- Temperature: Current temperature in the specified location
- Humidity: Current humidity percentage
- Condition: Description of current weather conditions (e.g., "partly cloudy", "rain")
- Error: A message explaining what went wrong if the weather information couldn't be retrieved

### Possible use case
A travel planning application could use this block to show current weather conditions for various destinations, helping users pack appropriate clothing and plan activities.
