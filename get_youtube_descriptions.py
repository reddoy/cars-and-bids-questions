#!/usr/bin/env python3
"""
YouTube Video Description Fetcher

This script fetches descriptions from YouTube videos using the YouTube Data API v3.
You can provide video IDs either via a text file or directly in the script.
"""

import os
import json
import argparse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def extract_playlist_id(playlist_url):
    """Extract playlist ID from a YouTube playlist URL."""
    if 'list=' in playlist_url:
        playlist_id = playlist_url.split('list=')[1].split('&')[0]
        return playlist_id
    return None


def get_playlist_video_ids(youtube_api_key, playlist_id):
    """Fetch all video IDs from a YouTube playlist."""
    try:
        youtube = build('youtube', 'v3', developerKey=youtube_api_key)
        video_ids = []
        next_page_token = None
        
        print(f"Fetching video IDs from playlist: {playlist_id}...")
        
        while True:
            request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=50,  # API allows up to 50 per request
                pageToken=next_page_token
            )
            response = request.execute()
            
            # Extract video IDs from this page
            for item in response.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)
            
            # Check if there are more pages
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        
        print(f"Found {len(video_ids)} video(s) in playlist")
        return video_ids
        
    except HttpError as e:
        print(f"An HTTP error occurred while fetching playlist: {e}")
        raise
    except Exception as e:
        print(f"An error occurred while fetching playlist: {e}")
        raise


def load_video_ids(file_path):
    """Load video IDs from a text file (one per line)."""
    video_ids = []
    with open(file_path, 'r') as f:
        for line in f:
            video_id = line.strip()
            if video_id and not video_id.startswith('#'):  # Skip empty lines and comments
                # Extract video ID from URL if full URL is provided
                if 'youtube.com/watch?v=' in video_id:
                    video_id = video_id.split('v=')[1].split('&')[0]
                elif 'youtu.be/' in video_id:
                    video_id = video_id.split('youtu.be/')[1].split('?')[0]
                video_ids.append(video_id)
    return video_ids


def get_video_descriptions(youtube_api_key, video_ids):
    """Fetch descriptions for a list of video IDs."""
    try:
        # Build the YouTube API service
        youtube = build('youtube', 'v3', developerKey=youtube_api_key)
        
        results = []
        
        # Process videos in batches (API allows up to 50 at a time)
        batch_size = 50
        for i in range(0, len(video_ids), batch_size):
            batch = video_ids[i:i + batch_size]
            
            # Make API request
            request = youtube.videos().list(
                part='snippet,statistics',
                id=','.join(batch)
            )
            response = request.execute()
            
            # Process results
            for item in response.get('items', []):
                video_id = item['id']
                snippet = item['snippet']
                stats = item.get('statistics', {})
                
                results.append({
                    'video_id': video_id,
                    'title': snippet.get('title', 'N/A'),
                    'channel': snippet.get('channelTitle', 'N/A'),
                    'published_at': snippet.get('publishedAt', 'N/A'),
                    'description': snippet.get('description', ''),
                    'view_count': stats.get('viewCount', 'N/A'),
                    'like_count': stats.get('likeCount', 'N/A'),
                    'url': f"https://www.youtube.com/watch?v={video_id}"
                })
        
        # Handle videos that weren't found
        found_ids = {result['video_id'] for result in results}
        not_found = [vid for vid in video_ids if vid not in found_ids]
        
        if not_found:
            print(f"\nWarning: {len(not_found)} video(s) not found: {', '.join(not_found)}")
        
        return results
        
    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise


def save_results(results, output_file, format='json'):
    """Save results to a file."""
    if format == 'json':
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    elif format == 'txt':
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(f"{'='*80}\n")
                f.write(f"Title: {result['title']}\n")
                f.write(f"Video ID: {result['video_id']}\n")
                f.write(f"URL: {result['url']}\n")
                f.write(f"Channel: {result['channel']}\n")
                f.write(f"Published: {result['published_at']}\n")
                f.write(f"Views: {result['view_count']}\n")
                f.write(f"Likes: {result['like_count']}\n")
                f.write(f"\nDescription:\n{result['description']}\n")
                f.write(f"{'='*80}\n\n")
    elif format == 'csv':
        import csv
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['video_id', 'title', 'channel', 'published_at', 
                                                   'view_count', 'like_count', 'url', 'description'])
            writer.writeheader()
            for result in results:
                # Replace newlines in description for CSV
                result_copy = result.copy()
                result_copy['description'] = result_copy['description'].replace('\n', ' ').replace('\r', ' ')
                writer.writerow(result_copy)
    
    print(f"Results saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Fetch descriptions from YouTube videos or playlists',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch from a playlist
  python get_youtube_descriptions.py --api-key YOUR_API_KEY --playlist "https://www.youtube.com/playlist?list=PLRsapyZqDs1oR-egCLXRK-qmdPIZf1y5-"
  
  # Use a file with video IDs
  python get_youtube_descriptions.py --api-key YOUR_API_KEY --input video_ids.txt
  
  # Use environment variable for API key
  export YOUTUBE_API_KEY=your_key_here
  python get_youtube_descriptions.py --playlist "https://www.youtube.com/playlist?list=PLRsapyZqDs1oR-egCLXRK-qmdPIZf1y5-"
  
  # Output to CSV format
  python get_youtube_descriptions.py --api-key YOUR_API_KEY --playlist "PLAYLIST_URL" --output results.csv --format csv
        """
    )
    
    parser.add_argument('--api-key', 
                       help='YouTube Data API v3 key (or set YOUTUBE_API_KEY env var)',
                       default=os.getenv('YOUTUBE_API_KEY'))
    parser.add_argument('--input', '-i',
                       help='Input file with video IDs (one per line, or full URLs)',
                       default=None)
    parser.add_argument('--playlist', '-p',
                       help='YouTube playlist URL or playlist ID',
                       default=None)
    parser.add_argument('--output', '-o',
                       help='Output file path (default: youtube_descriptions.json)',
                       default='youtube_descriptions.json')
    parser.add_argument('--format', '-f',
                       choices=['json', 'txt', 'csv'],
                       help='Output format (default: json)',
                       default='json')
    
    args = parser.parse_args()
    
    # Check for API key
    if not args.api_key:
        print("Error: YouTube API key is required!")
        print("Set it via --api-key argument or YOUTUBE_API_KEY environment variable")
        return
    
    # Check that either input file or playlist is provided
    if not args.input and not args.playlist:
        print("Error: Either --input or --playlist must be provided!")
        return
    
    if args.input and args.playlist:
        print("Error: Please provide either --input or --playlist, not both!")
        return
    
    # Get video IDs from playlist or file
    if args.playlist:
        # Extract playlist ID from URL if needed
        playlist_id = args.playlist
        if 'list=' in playlist_id:
            playlist_id = extract_playlist_id(playlist_id)
        
        if not playlist_id:
            print(f"Error: Could not extract playlist ID from: {args.playlist}")
            return
        
        video_ids = get_playlist_video_ids(args.api_key, playlist_id)
        
        if not video_ids:
            print("No videos found in playlist!")
            return
    else:
        # Load video IDs from file
        if not os.path.exists(args.input):
            print(f"Error: Input file '{args.input}' not found!")
            return
        
        print(f"Loading video IDs from {args.input}...")
        video_ids = load_video_ids(args.input)
        print(f"Found {len(video_ids)} video ID(s)")
        
        if not video_ids:
            print("No video IDs found in input file!")
            return
    
    # Fetch descriptions
    print("Fetching video descriptions from YouTube API...")
    results = get_video_descriptions(args.api_key, video_ids)
    
    print(f"\nSuccessfully fetched {len(results)} video description(s)")
    
    # Save results
    save_results(results, args.output, args.format)
    
    # Print summary
    print(f"\nSummary:")
    print(f"  Total videos requested: {len(video_ids)}")
    print(f"  Successfully fetched: {len(results)}")


if __name__ == '__main__':
    main()

