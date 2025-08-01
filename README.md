# YouTube Transcript Generator

A simple Flask web application that generates transcripts from YouTube videos using the `youtube-transcript-api`.

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the server:
```bash
python app.py
```

2. The server will run on `http://localhost:5000`

## API Endpoints

### Home Page
- **URL**: `http://localhost:5000/`
- **Description**: Shows usage instructions and available endpoints

### Get Transcript
- **URL**: `http://localhost:5000/gettranscript/<video_id>`
- **Description**: Get transcript as JSON with metadata
- **Example**: `http://localhost:5000/gettranscript/dQw4w9WgXcQ`

### Get Transcript as Text
- **URL**: `http://localhost:5000/gettranscript/<video_id>/text`
- **Description**: Get transcript as plain text
- **Example**: `http://localhost:5000/gettranscript/dQw4w9WgXcQ/text`

### Get Transcript as Formatted JSON
- **URL**: `http://localhost:5000/gettranscript/<video_id>/json`
- **Description**: Get transcript as formatted JSON
- **Example**: `http://localhost:5000/gettranscript/dQw4w9WgXcQ/json`

### List Available Transcripts
- **URL**: `http://localhost:5000/list-transcripts/<video_id>`
- **Description**: List all available transcripts for a video
- **Example**: `http://localhost:5000/list-transcripts/dQw4w9WgXcQ`

## Video ID Formats

You can use:
- **Video ID only**: `dQw4w9WgXcQ`
- **Full YouTube URL**: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- **Short URL**: `https://youtu.be/dQw4w9WgXcQ`
- **Embed URL**: `https://www.youtube.com/embed/dQw4w9WgXcQ`

## Features

- ✅ Extracts video ID from various YouTube URL formats
- ✅ Returns transcripts in multiple formats (JSON, text, formatted JSON)
- ✅ Handles errors gracefully
- ✅ Lists available transcripts for a video
- ✅ Defaults to English transcripts
- ✅ Includes metadata (language, duration, etc.)

## Example Response

```json
{
  "success": true,
  "video_id": "dQw4w9WgXcQ",
  "language": "English",
  "language_code": "en",
  "is_generated": false,
  "snippet_count": 45,
  "transcript": [
    {
      "text": "We're no strangers to love",
      "start": 0.0,
      "duration": 2.5
    },
    {
      "text": "You know the rules and so do I",
      "start": 2.5,
      "duration": 3.2
    }
  ]
}
```

## Error Handling

The API returns error responses in JSON format:

```json
{
  "success": false,
  "error": "Error message here",
  "video_id": "invalid_video_id"
}
```

## Notes

- The application defaults to English transcripts
- Some videos may not have transcripts available
- Age-restricted videos may not be accessible without authentication
- The API may be rate-limited by YouTube 