# YouTube Transcript API

A serverless API to fetch YouTube video transcripts using the YouTube Transcript API.

## Features

- Get transcript with timing information
- Get transcript as plain text
- Support for YouTube video IDs and URLs
- CORS enabled for cross-origin requests

## API Endpoints

### 1. Get Transcript with Timing
```
GET /transcript?video_id=YOUR_VIDEO_ID_OR_URL
```

**Response:**
```json
{
  "video_id": "A_fOHpBqj50",
  "transcript": [
    {
      "text": "I've had this quote from the CEO of Anthropic",
      "start": 0.0,
      "duration": 1.85
    }
  ],
  "total_entries": 1
}
```

### 2. Get Transcript as Plain Text
```
GET /transcript/text?video_id=YOUR_VIDEO_ID_OR_URL
```

**Response:**
```json
{
  "video_id": "A_fOHpBqj50",
  "text": "I've had this quote from the CEO of Anthropic stuck in my head..."
}
```

### 3. API Documentation
```
GET /
```

Returns API documentation and usage examples.

## Examples

### Using Video ID
```
GET /transcript?video_id=A_fOHpBqj50
```

### Using YouTube URL
```
GET /transcript?video_id=https://www.youtube.com/watch?v=A_fOHpBqj50
```

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask app:
```bash
python app.py
```

3. The API will be available at `http://localhost:8000`

## Vercel Deployment

This API is configured for Vercel serverless deployment.

### Deploy to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

3. Follow the prompts to deploy your API

### Environment Variables

No environment variables are required for this API.

## Usage in Other Applications

Once deployed to Vercel, you can call the API from any application:

```javascript
// Example JavaScript usage
fetch('https://your-vercel-app.vercel.app/transcript?video_id=A_fOHpBqj50')
  .then(response => response.json())
  .then(data => console.log(data));
```

```python
# Example Python usage
import requests

response = requests.get('https://your-vercel-app.vercel.app/transcript?video_id=A_fOHpBqj50')
data = response.json()
print(data)
```

## Error Handling

The API returns appropriate error messages for:
- Missing video_id parameter
- Invalid YouTube URL or video ID
- YouTube API errors or network issues

## CORS

The API includes CORS headers to allow cross-origin requests from web applications. 