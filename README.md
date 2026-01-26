# YouTube Video Description Fetcher

A Python script to fetch descriptions and metadata from YouTube videos using the YouTube Data API v3.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get a YouTube Data API Key:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the "YouTube Data API v3"
   - Create credentials (API Key)
   - Copy your API key

3. **Prepare your video list:**
   - Create a text file (e.g., `video_ids.txt`) with one video ID or URL per line
   - You can use:
     - Video IDs: `dQw4w9WgXcQ`
     - Full URLs: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
     - Short URLs: `https://youtu.be/dQw4w9WgXcQ`
   - Lines starting with `#` are treated as comments and ignored
   - See `video_ids.txt.example` for an example

## Usage

### Fetch from a YouTube playlist (recommended for multiple videos):
```bash
python get_youtube_descriptions.py --api-key YOUR_API_KEY --playlist "https://www.youtube.com/playlist?list=PLRsapyZqDs1oR-egCLXRK-qmdPIZf1y5-"
```

### Fetch from individual video IDs in a file:
```bash
python get_youtube_descriptions.py --api-key YOUR_API_KEY --input video_ids.txt
```

### Using environment variable for API key:
```bash
export YOUTUBE_API_KEY=your_api_key_here
python get_youtube_descriptions.py --playlist "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"
# or
python get_youtube_descriptions.py --input video_ids.txt
```

### Output formats:

**JSON (default):**
```bash
python get_youtube_descriptions.py --api-key YOUR_API_KEY --input video_ids.txt --output results.json --format json
```

**Text:**
```bash
python get_youtube_descriptions.py --api-key YOUR_API_KEY --input video_ids.txt --output results.txt --format txt
```

**CSV:**
```bash
python get_youtube_descriptions.py --api-key YOUR_API_KEY --playlist "PLAYLIST_URL" --output results.csv --format csv
# or
python get_youtube_descriptions.py --api-key YOUR_API_KEY --input video_ids.txt --output results.csv --format csv
```

## Output

The script fetches the following information for each video:
- Video ID
- Title
- Channel name
- Publication date
- Description (full text)
- View count
- Like count
- Video URL

## Features

- **Playlist support**: Automatically fetches all videos from a YouTube playlist
- **Batch processing**: Processes videos in batches of 50 (YouTube API limit)
- **Multiple formats**: Output in JSON, TXT, or CSV format
- **Flexible input**: Accepts video IDs, URLs, or playlist URLs

## Notes

- The script processes videos in batches of 50 (YouTube API limit)
- API quota: Each video fetch counts as 1 unit. The default quota is 10,000 units per day
- Playlist fetching uses additional API quota (1 unit per page, typically 50 videos per page)
- Make sure your API key has the YouTube Data API v3 enabled
- If a video is private, deleted, or doesn't exist, it will be skipped with a warning

