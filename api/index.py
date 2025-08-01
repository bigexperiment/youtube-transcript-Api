from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
import re
from http.server import BaseHTTPRequestHandler
import json
import requests
import time
import random
import urllib.parse

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

def get_transcript_with_free_methods(video_id, max_retries=3):
    """Try multiple free methods to get transcript"""
    
    # Method 1: Try direct API with delays and different user agents
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    
    for attempt in range(max_retries):
        try:
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id, ['en'])
            return transcript
        except Exception as e:
            if "blocked" in str(e).lower() or "ip" in str(e).lower():
                # Add delay between retries
                time.sleep(random.uniform(2, 5))
                continue
            else:
                raise e
    
    # Method 2: Try with different language codes
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, ['en', 'en-US', 'en-GB'])
        return transcript
    except Exception as e:
        pass
    
    # Method 3: Try to get any available transcript
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
        return transcript.fetch()
    except Exception as e:
        pass
    
    # Method 4: Try alternative approach - check if video has captions
    try:
        # This is a fallback that might work in some cases
        api = YouTubeTranscriptApi()
        transcript_list = api.list_transcripts(video_id)
        # Try any available transcript
        for transcript in transcript_list:
            try:
                return transcript.fetch()
            except:
                continue
    except Exception as e:
        pass
    
    # Method 5: Return helpful error with suggestions
    raise Exception(f"Could not retrieve transcript. This is likely due to YouTube blocking serverless function IPs. Try deploying to a VPS or using the video in a browser to confirm transcript availability.")

def get_transcript_with_web_scraping(video_id):
    """Alternative method using web scraping (free)"""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Look for transcript data in the page
            content = response.text
            # This is a simplified approach - in practice you'd need to parse the actual transcript data
            if 'transcript' in content.lower() or 'caption' in content.lower():
                return {"message": "Video appears to have transcripts available, but serverless functions are blocked by YouTube"}
        
        return {"message": "Could not access video transcript via web scraping"}
        
    except Exception as e:
        return {"message": f"Web scraping failed: {str(e)}"}

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
        
        # Try to get transcript with free methods
        transcript = get_transcript_with_free_methods(video_id)
        
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
        # Try web scraping as fallback
        web_result = get_transcript_with_web_scraping(video_id)
        
        return jsonify({
            'error': f'Failed to get transcript: {str(e)}',
            'note': 'YouTube blocks requests from serverless functions (Vercel, Netlify, etc.)',
            'free_solutions': [
                'Deploy to Railway/Render (free tier with real IP)',
                'Deploy to a VPS ($5/month)',
                'Use GitHub Actions as free server',
                'Use RapidAPI free tier',
                'Check if video has transcripts in browser first'
            ],
            'web_scraping_result': web_result,
            'video_url': f'https://www.youtube.com/watch?v={video_id}'
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
        
        # Try to get transcript with free methods
        transcript = get_transcript_with_free_methods(video_id)
        
        # Combine all text
        full_text = ' '.join([snippet.text for snippet in transcript.snippets])
        
        return jsonify({
            'video_id': video_id,
            'text': full_text
        })
        
    except Exception as e:
        # Try web scraping as fallback
        web_result = get_transcript_with_web_scraping(video_id)
        
        return jsonify({
            'error': f'Failed to get transcript: {str(e)}',
            'note': 'YouTube blocks requests from serverless functions (Vercel, Netlify, etc.)',
            'free_solutions': [
                'Deploy to Railway/Render (free tier with real IP)',
                'Deploy to a VPS ($5/month)',
                'Use GitHub Actions as free server',
                'Use RapidAPI free tier',
                'Check if video has transcripts in browser first'
            ],
            'web_scraping_result': web_result,
            'video_url': f'https://www.youtube.com/watch?v={video_id}'
        }), 500

@app.route('/', methods=['GET'])
def home():
    """API documentation"""
    return jsonify({
        'message': 'YouTube Transcript API (Free Version)',
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
        },
        'note': 'Due to YouTube blocking serverless function IPs, this API may not work reliably.',
        'free_alternatives': [
            'Deploy to Railway/Render (free tier)',
            'Use RapidAPI free tier',
            'Deploy to VPS ($5/month)',
            'Use GitHub Actions as free server'
        ]
    })

# Vercel serverless function handler
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the path and query parameters
        from urllib.parse import urlparse, parse_qs
        
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        # Convert query params to single values
        args = {k: v[0] if v else None for k, v in query_params.items()}
        
        # Create a mock request object
        class MockRequest:
            def __init__(self, path, args):
                self.path = path
                self.args = args
            
            def args_get(self, key):
                return self.args.get(key)
        
        mock_request = MockRequest(path, args)
        
        # Route the request
        if path == '/transcript':
            response = get_transcript_handler(mock_request)
        elif path == '/transcript/text':
            response = get_transcript_text_handler(mock_request)
        elif path == '/':
            response = home_handler()
        else:
            response = {'error': 'Not found'}, 404
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        if isinstance(response, tuple):
            data, status_code = response
            self.send_response(status_code)
        else:
            data = response
        
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def get_transcript_handler(request):
    """Handler for /transcript endpoint"""
    video_id_or_url = request.args_get('video_id')
    
    if not video_id_or_url:
        return {
            'error': 'Missing video_id parameter',
            'usage': 'GET /transcript?video_id=YOUR_VIDEO_ID_OR_URL'
        }, 400
    
    try:
        # Extract video ID from URL or use directly
        video_id = extract_video_id(video_id_or_url)
        
        if not video_id:
            return {
                'error': 'Invalid YouTube URL or video ID'
            }, 400
        
        # Try to get transcript with free methods
        transcript = get_transcript_with_free_methods(video_id)
        
        # Format the response
        formatted_transcript = []
        for snippet in transcript.snippets:
            formatted_transcript.append({
                'text': snippet.text,
                'start': snippet.start,
                'duration': snippet.duration
            })
        
        return {
            'video_id': video_id,
            'transcript': formatted_transcript,
            'total_entries': len(formatted_transcript)
        }
        
    except Exception as e:
        # Try web scraping as fallback
        web_result = get_transcript_with_web_scraping(video_id)
        
        return {
            'error': f'Failed to get transcript: {str(e)}',
            'note': 'YouTube blocks requests from serverless functions (Vercel, Netlify, etc.)',
            'free_solutions': [
                'Deploy to Railway/Render (free tier with real IP)',
                'Deploy to a VPS ($5/month)',
                'Use GitHub Actions as free server',
                'Use RapidAPI free tier',
                'Check if video has transcripts in browser first'
            ],
            'web_scraping_result': web_result,
            'video_url': f'https://www.youtube.com/watch?v={video_id}'
        }, 500

def get_transcript_text_handler(request):
    """Handler for /transcript/text endpoint"""
    video_id_or_url = request.args_get('video_id')
    
    if not video_id_or_url:
        return {
            'error': 'Missing video_id parameter',
            'usage': 'GET /transcript/text?video_id=YOUR_VIDEO_ID_OR_URL'
        }, 400
    
    try:
        # Extract video ID from URL or use directly
        video_id = extract_video_id(video_id_or_url)
        
        if not video_id:
            return {
                'error': 'Invalid YouTube URL or video ID'
            }, 400
        
        # Try to get transcript with free methods
        transcript = get_transcript_with_free_methods(video_id)
        
        # Combine all text
        full_text = ' '.join([snippet.text for snippet in transcript.snippets])
        
        return {
            'video_id': video_id,
            'text': full_text
        }
        
    except Exception as e:
        # Try web scraping as fallback
        web_result = get_transcript_with_web_scraping(video_id)
        
        return {
            'error': f'Failed to get transcript: {str(e)}',
            'note': 'YouTube blocks requests from serverless functions (Vercel, Netlify, etc.)',
            'free_solutions': [
                'Deploy to Railway/Render (free tier with real IP)',
                'Deploy to a VPS ($5/month)',
                'Use GitHub Actions as free server',
                'Use RapidAPI free tier',
                'Check if video has transcripts in browser first'
            ],
            'web_scraping_result': web_result,
            'video_url': f'https://www.youtube.com/watch?v={video_id}'
        }, 500

def home_handler():
    """Handler for / endpoint"""
    return {
        'message': 'YouTube Transcript API (Free Version)',
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
        },
        'note': 'Due to YouTube blocking serverless function IPs, this API may not work reliably.',
        'free_alternatives': [
            'Deploy to Railway/Render (free tier)',
            'Use RapidAPI free tier',
            'Deploy to VPS ($5/month)',
            'Use GitHub Actions as free server'
        ]
    } 