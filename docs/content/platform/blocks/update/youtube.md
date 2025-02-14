
# YouTube Blocks

## YouTube Video Transcriber

### What it is
A tool that converts spoken content from YouTube videos into written text format.

### What it does
Takes a YouTube video URL and produces a text transcript of all spoken content in the video. It can handle various YouTube URL formats, including standard watch URLs, shortened URLs (youtu.be), and embedded video URLs.

### How it works
1. Takes your provided YouTube video URL
2. Extracts the unique video identifier from the URL
3. Searches for available transcripts for the video
4. Retrieves the transcript in the first available language
5. Formats the transcript into clean, readable text

### Inputs
- YouTube URL: The web address of the YouTube video you want to transcribe. This can be in any standard YouTube format (e.g., regular watch URL, shortened URL, or embed URL)

### Outputs
- Video ID: The unique identifier for the YouTube video
- Transcript: The complete text version of the video's spoken content
- Error: A message explaining what went wrong if the transcription fails

### Possible use cases
- A content creator wanting to create subtitles or captions for their videos
- A student needing to reference specific parts of a lecture video
- A researcher collecting data from educational videos
- A marketing team analyzing competitor video content
- A journalist quoting from video interviews
- Making video content accessible to deaf or hard-of-hearing viewers

### Notes
- The video must have available transcripts (either auto-generated or manually created)
- The tool will use the first available language version of the transcript
- Works with both public and unlisted videos (as long as you have the URL)
