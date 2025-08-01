from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
import re

app = Flask(__name__)
CORS(app)

def extract_video_id(url_or_id):
    """Extract video ID from YouTube URL or use the ID directly"""
    if 'youtube.com' in url_or_id or 'youtu.be' in url_or_id:
        # Handle different YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)
        return None
    else:
        # Assume it's already a video ID
        return url_or_id

@app.route('/transcript', methods=['GET'])
def get_transcript():
    """Get transcript for a YouTube video"""
    video_id_or_url = request.args.get('video_id')
    
    if not video_id_or_url:
        return jsonify({
            'error': 'Missing video_id parameter',
            'usage': 'GET /transcript?video_id=YOUR_VIDEO_ID_OR_URL'
        }), 400
    
    try:
        # Extract video ID from URL or use directly
        video_id = extract_video_id(video_id_or_url)
        
        if not video_id:
            return jsonify({
                'error': 'Invalid YouTube URL or video ID'
            }), 400
        
        # Get transcript using correct API method
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, ['en'])
        
        # Format the response
        formatted_transcript = []
        for snippet in transcript.snippets:
            formatted_transcript.append({
                'text': snippet.text,
                'start': snippet.start,
                'duration': snippet.duration
            })
        
        return jsonify({
            'video_id': video_id,
            'transcript': formatted_transcript,
            'total_entries': len(formatted_transcript)
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get transcript: {str(e)}',
            'note': 'This might be due to YouTube API changes or network issues'
        }), 500

@app.route('/transcript/text', methods=['GET'])
def get_transcript_text():
    """Get transcript as plain text"""
    video_id_or_url = request.args.get('video_id')
    
    if not video_id_or_url:
        return jsonify({
            'error': 'Missing video_id parameter',
            'usage': 'GET /transcript/text?video_id=YOUR_VIDEO_ID_OR_URL'
        }), 400
    
    try:
        # Extract video ID from URL or use directly
        video_id = extract_video_id(video_id_or_url)
        
        if not video_id:
            return jsonify({
                'error': 'Invalid YouTube URL or video ID'
            }), 400
        
        # Get transcript using correct API method
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, ['en'])
        
        # Combine all text
        full_text = ' '.join([snippet.text for snippet in transcript.snippets])
        
        return jsonify({
            'video_id': video_id,
            'text': full_text
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get transcript: {str(e)}',
            'note': 'This might be due to YouTube API changes or network issues'
        }), 500

@app.route('/', methods=['GET'])
def home():
    """API documentation"""
    return jsonify({
        'message': 'YouTube Transcript API',
        'endpoints': {
            '/transcript': {
                'method': 'GET',
                'params': 'video_id (YouTube video ID or URL)',
                'description': 'Get transcript with timing information'
            },
            '/transcript/text': {
                'method': 'GET', 
                'params': 'video_id (YouTube video ID or URL)',
                'description': 'Get transcript as plain text'
            }
        },
        'examples': {
            'by_video_id': '/transcript?video_id=dQw4w9WgXcQ',
            'by_url': '/transcript?video_id=https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

# Vercel handler
def handler(request, context):
    return app(request, context) 