#!/usr/bin/env python3
"""
Quick script to check if there are new videos in the playlist
"""

import os
import json
from googleapiclient.discovery import build

def get_playlist_video_count(youtube_api_key, playlist_id):
    """Get the count of videos in a playlist."""
    try:
        youtube = build('youtube', 'v3', developerKey=youtube_api_key)
        count = 0
        next_page_token = None
        
        while True:
            request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
            
            count += len(response.get('items', []))
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        
        return count
        
    except Exception as e:
        print(f"Error fetching playlist: {e}")
        return None

def main():
    playlist_id = "PLRsapyZqDs1oR-egCLXRK-qmdPIZf1y5-"
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        print("Error: YOUTUBE_API_KEY environment variable not set")
        print("Please set it with: export YOUTUBE_API_KEY=your_key_here")
        return
    
    # Get current count from JSON
    try:
        with open('youtube_descriptions.json', 'r') as f:
            current_videos = json.load(f)
        current_count = len(current_videos)
    except:
        current_count = 0
    
    print(f"Current videos in youtube_descriptions.json: {current_count}")
    
    # Get playlist count
    print(f"Checking playlist {playlist_id}...")
    playlist_count = get_playlist_video_count(api_key, playlist_id)
    
    if playlist_count is None:
        return
    
    print(f"Videos in playlist: {playlist_count}")
    
    if playlist_count > current_count:
        print(f"\n✅ NEW VIDEOS FOUND! {playlist_count - current_count} new video(s) added to the playlist.")
        print(f"   Current: {current_count}, Playlist: {playlist_count}")
    elif playlist_count == current_count:
        print(f"\n✓ Playlist is up to date ({current_count} videos)")
    else:
        print(f"\n⚠ Warning: Playlist has fewer videos than JSON file ({playlist_count} vs {current_count})")

if __name__ == '__main__':
    main()

