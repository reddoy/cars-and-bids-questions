#!/usr/bin/env python3
"""
Extract transcriptions for each question from YouTube videos.

For each question, extracts the transcript from the question's timestamp
to the next question's timestamp (or end of video for the last question).
"""

import csv
import json
import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import argparse
import time


def get_video_transcript(video_id, retries=3):
    """Get transcript for a video with retry logic."""
    ytt_api = YouTubeTranscriptApi()
    for attempt in range(retries):
        try:
            # Use list() to get available transcripts
            transcript_list = ytt_api.list(video_id)
            # Try to find English transcript first
            try:
                transcript = transcript_list.find_transcript(['en']).fetch()
            except:
                # If no English, get the first available generated transcript
                transcript = transcript_list.find_generated_transcript(['en']).fetch()
            return transcript
        except TranscriptsDisabled:
            print(f"  ⚠️  Transcripts disabled for video {video_id}")
            return None
        except NoTranscriptFound:
            print(f"  ⚠️  No transcript found for video {video_id}")
            return None
        except VideoUnavailable:
            print(f"  ⚠️  Video unavailable: {video_id}")
            return None
        except Exception as e:
            error_str = str(e)
            if "IP" in error_str or "blocked" in error_str.lower() or "RequestBlocked" in error_str:
                # IP ban detected - wait much longer
                wait_time = (attempt + 1) * 30  # Exponential backoff: 30s, 60s, 90s
                print(f"  ⚠️  IP ban detected (attempt {attempt + 1}/{retries}). Waiting {wait_time} seconds...")
                print(f"  💡 Tip: If this continues, wait 10-15 minutes and resume the script")
                time.sleep(wait_time)
            elif attempt < retries - 1:
                wait_time = (attempt + 1) * 5  # 5s, 10s, 15s for other errors
                print(f"  ⚠️  Error getting transcript (attempt {attempt + 1}/{retries}): {str(e)[:100]}")
                print(f"  ⏳ Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                print(f"  ❌ Failed to get transcript after {retries} attempts: {str(e)[:200]}")
                return None
    return None


def extract_text_between_timestamps(transcript, start_seconds, end_seconds):
    """Extract transcript text between two timestamps."""
    if not transcript:
        return ""
    
    text_segments = []
    for entry in transcript:
        # Handle both dict and object formats
        if hasattr(entry, 'start'):
            entry_start = entry.start
            entry_duration = getattr(entry, 'duration', 0)
            entry_text = entry.text
        else:
            entry_start = entry['start']
            entry_duration = entry.get('duration', 0)
            entry_text = entry['text']
        
        entry_end = entry_start + entry_duration
        
        # Check if this entry overlaps with our time range
        if entry_start < end_seconds and entry_end > start_seconds:
            text_segments.append(entry_text)
    
    return ' '.join(text_segments).strip()


def load_checkpoint(checkpoint_file):
    """Load checkpoint data if it exists."""
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            print(f"📂 Loaded checkpoint: {len(checkpoint.get('processed_videos', []))} videos already processed")
            return checkpoint
        except:
            return {'processed_videos': [], 'processed_questions': {}}
    return {'processed_videos': [], 'processed_questions': {}}


def save_checkpoint(checkpoint_file, processed_videos, processed_questions):
    """Save checkpoint data."""
    checkpoint = {
        'processed_videos': processed_videos,
        'processed_questions': processed_questions
    }
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=2)


def process_questions(input_file, output_file, checkpoint_file='transcription_checkpoint.json'):
    """Process questions and extract transcriptions."""
    print(f"Reading questions from {input_file}...")
    
    # Load checkpoint
    checkpoint = load_checkpoint(checkpoint_file)
    processed_videos = set(checkpoint.get('processed_videos', []))
    processed_questions = checkpoint.get('processed_questions', {})
    
    # Read all questions
    questions = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            question_key = f"{row['video_id']}_{row['timestamp_seconds']}"
            # If already processed, use existing transcription
            if question_key in processed_questions:
                questions.append({
                    'video_id': row['video_id'],
                    'video_title': row['video_title'],
                    'video_url': row['video_url'],
                    'timestamp': row['timestamp'],
                    'timestamp_seconds': int(row['timestamp_seconds']),
                    'question': row['question'],
                    'transcription': processed_questions[question_key]
                })
            else:
                questions.append({
                    'video_id': row['video_id'],
                    'video_title': row['video_title'],
                    'video_url': row['video_url'],
                    'timestamp': row['timestamp'],
                    'timestamp_seconds': int(row['timestamp_seconds']),
                    'question': row['question']
                })
    
    print(f"Found {len(questions)} questions")
    if processed_videos:
        print(f"📊 {len(processed_videos)} videos already processed, will skip them")
    
    # Group questions by video to minimize API calls
    questions_by_video = {}
    for q in questions:
        video_id = q['video_id']
        if video_id not in questions_by_video:
            questions_by_video[video_id] = []
        questions_by_video[video_id].append(q)
    
    print(f"Processing {len(questions_by_video)} unique videos...\n")
    
    # Process each video
    transcripts_cache = {}
    processed_count = 0
    failed_count = 0
    video_count = 0
    total_videos = len(questions_by_video)
    
    for video_id, video_questions in questions_by_video.items():
        video_count += 1
        print(f"\n📹 Video {video_count}/{total_videos}: {video_questions[0]['video_title'][:60]}...")
        print(f"   Video ID: {video_id}")
        
        # Check if this video was already processed
        if video_id in processed_videos:
            print(f"   ⏭️  Already processed, skipping...")
            continue
        
        # Get transcript for this video (cache it)
        if video_id not in transcripts_cache:
            # Add delay before fetching transcript to avoid IP bans
            if video_count > 1:
                delay = 10  # 10 seconds between videos to avoid IP bans
                print(f"   ⏳ Waiting {delay} seconds before fetching transcript...")
                time.sleep(delay)
            
            transcript = get_video_transcript(video_id)
            transcripts_cache[video_id] = transcript
            
            # Additional delay after fetch (successful or not) to be safe
            delay_after = 5  # 5 seconds after each video
            print(f"   ⏳ Waiting {delay_after} seconds before next video...")
            time.sleep(delay_after)
        else:
            transcript = transcripts_cache[video_id]
        
        if not transcript:
            print(f"   ⚠️  Skipping {len(video_questions)} questions (no transcript)")
            failed_count += len(video_questions)
            for q in video_questions:
                q['transcription'] = ""
            # Mark as processed even if failed (to avoid retrying)
            processed_videos.add(video_id)
            save_checkpoint(checkpoint_file, list(processed_videos), processed_questions)
            continue
        
        # Sort questions by timestamp
        video_questions.sort(key=lambda x: x['timestamp_seconds'])
        
        # Extract transcriptions for each question
        for i, question in enumerate(video_questions):
            question_key = f"{video_id}_{question['timestamp_seconds']}"
            
            # Skip if already processed
            if question_key in processed_questions:
                question['transcription'] = processed_questions[question_key]
                continue
            
            start_seconds = question['timestamp_seconds']
            
            # Determine end timestamp
            if i < len(video_questions) - 1:
                # Next question's timestamp
                end_seconds = video_questions[i + 1]['timestamp_seconds']
            else:
                # Last question - use end of video (get from last transcript entry)
                if transcript:
                    last_entry = transcript[-1]
                    if hasattr(last_entry, 'start'):
                        end_seconds = last_entry.start + getattr(last_entry, 'duration', 0)
                    else:
                        end_seconds = last_entry['start'] + last_entry.get('duration', 0)
                else:
                    end_seconds = start_seconds + 180  # Default to 3 minutes if no transcript
            
            # Extract transcription
            transcription = extract_text_between_timestamps(transcript, start_seconds, end_seconds)
            question['transcription'] = transcription
            processed_questions[question_key] = transcription  # Save to checkpoint
            
            if transcription:
                print(f"   ✓ Question {i+1}/{len(video_questions)}: {len(transcription)} chars")
                processed_count += 1
            else:
                print(f"   ⚠️  Question {i+1}/{len(video_questions)}: No transcription found")
                failed_count += 1
        
        # Mark video as processed and save checkpoint
        processed_videos.add(video_id)
        save_checkpoint(checkpoint_file, list(processed_videos), processed_questions)
        print(f"   💾 Checkpoint saved")
        print()  # Empty line between videos
    
    # Write results
    print(f"\nWriting results to {output_file}...")
    
    fieldnames = ['video_id', 'video_title', 'video_url', 'timestamp', 'timestamp_seconds', 
                  'question', 'transcription']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for question in questions:
            writer.writerow(question)
    
    print(f"✅ Successfully processed {processed_count} questions")
    if failed_count > 0:
        print(f"⚠️  {failed_count} questions had no transcription")
    print(f"📄 Results saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Extract transcriptions for YouTube video questions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_transcriptions.py --input questions.csv --output questions_with_transcriptions.csv
        """
    )
    
    parser.add_argument('--input', '-i',
                       help='Input CSV file with questions (default: questions.csv)',
                       default='questions.csv')
    parser.add_argument('--output', '-o',
                       help='Output CSV file with transcriptions (default: questions_with_transcriptions.csv)',
                       default='questions_with_transcriptions.csv')
    parser.add_argument('--checkpoint', '-c',
                       help='Checkpoint file to save/resume progress (default: transcription_checkpoint.json)',
                       default='transcription_checkpoint.json')
    parser.add_argument('--clear-checkpoint',
                       help='Clear checkpoint and start fresh',
                       action='store_true')
    
    args = parser.parse_args()
    
    # Clear checkpoint if requested
    if args.clear_checkpoint and os.path.exists(args.checkpoint):
        os.remove(args.checkpoint)
        print("🗑️  Checkpoint cleared, starting fresh")
    
    try:
        process_questions(args.input, args.output, args.checkpoint)
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == '__main__':
    main()

