#!/usr/bin/env python3
"""
Calculate answer durations - time between question and next question/end
Only includes actual community questions (not questions in first 5 minutes)
"""

import csv
from collections import defaultdict

def timestamp_to_seconds(timestamp):
    """Convert timestamp to seconds"""
    parts = timestamp.split(':')
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    return 0

def format_time(seconds):
    """Format seconds into MM:SS or HH:MM:SS"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

def calculate_answer_durations(csv_file):
    """Calculate how long each question takes to answer - only community questions"""
    questions = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            questions.append({
                'video_id': row['video_id'],
                'video_title': row['video_title'],
                'video_url': row['video_url'],
                'timestamp': row['timestamp'],
                'timestamp_seconds': int(row['timestamp_seconds']),
                'question': row['question']
            })
    
    # Filter out questions that are likely NOT community questions
    # Community questions typically start after 30-40 minutes in the video
    # Questions in first 5 minutes are usually part of the main content
    COMMUNITY_QUESTION_THRESHOLD = 300  # 5 minutes in seconds
    
    community_questions = [
        q for q in questions 
        if q['timestamp_seconds'] >= COMMUNITY_QUESTION_THRESHOLD
    ]
    
    # Group by video
    questions_by_video = defaultdict(list)
    for q in community_questions:
        questions_by_video[q['video_id']].append(q)
    
    # Calculate answer durations
    answer_durations = []
    
    for video_id, video_questions in questions_by_video.items():
        # Sort by timestamp
        sorted_questions = sorted(video_questions, key=lambda x: x['timestamp_seconds'])
        
        for i, q in enumerate(sorted_questions):
            # Duration is time until next question, or estimate end of video
            if i < len(sorted_questions) - 1:
                # Time until next question
                next_q = sorted_questions[i + 1]
                duration = next_q['timestamp_seconds'] - q['timestamp_seconds']
                # If duration is 0 or negative, skip this question (duplicate timestamp)
                if duration <= 0:
                    continue
            else:
                # Last question - estimate 5 minutes for answer (or use video length if available)
                # For now, estimate 5 minutes
                duration = 300  # 5 minutes default
            
            answer_durations.append({
                'question': q['question'],
                'duration_seconds': duration,
                'duration_formatted': format_time(duration),
                'video_id': q['video_id'],
                'video_title': q['video_title'],
                'video_url': q['video_url'],
                'timestamp': q['timestamp'],
                'timestamp_seconds': q['timestamp_seconds']
            })
    
    if not answer_durations:
        return {
            'longest_answer': None,
            'shortest_answer': None,
            'avg_answer_duration': 0
        }
    
    # Find longest and shortest answer durations
    longest = max(answer_durations, key=lambda x: x['duration_seconds'])
    shortest = min(answer_durations, key=lambda x: x['duration_seconds'])
    
    return {
        'longest_answer': longest,
        'shortest_answer': shortest,
        'avg_answer_duration': sum(d['duration_seconds'] for d in answer_durations) / len(answer_durations) if answer_durations else 0
    }

if __name__ == '__main__':
    import json
    stats = calculate_answer_durations('questions.csv')
    print(json.dumps(stats, indent=2))

